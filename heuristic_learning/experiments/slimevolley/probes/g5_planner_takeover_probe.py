"""Development-only planner-takeover probes for SlimeVolley generation 5.

The current `net-pressure` probe wins too few points against archived hard
opponents. Prior generation-5 attempts changed low terminal actions, reset
macros, and opponent-side pressure after contact. This probe tests a different
structural mechanism: let the transparent physics planner briefly take over
only in earlier intercept states, then fall back to `net-pressure` everywhere
else.

Only generation-5 development seeds are used. The script writes an append-only
JSON artifact and does not edit maintained policies or canonical ledgers.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.policies.slimevolley import (
    RALLY_SERVE_CONFIG,
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyNetPressurePolicy,
    SlimeVolleyPlannerPolicy,
    _action_key_for_policy,
    _state,
)
from hl_benchmark.slimevolley.adapter import make_slimevolley_env, run_slimevolley_episode
from hl_benchmark.slimevolley.opponents import make_slimevolley_opponent


SHORT_SEEDS = list(range(12000, 12016))
FULL_SEEDS = list(range(12000, 12050))
HARD_OPPONENTS = ["improved-v3", "improved-v4", "improved-v5", "improved-v6"]
SCREEN_OPPONENTS = ["builtin", *HARD_OPPONENTS]
FULL_POOL = [
    "builtin",
    "random",
    "initial",
    "improved-v0",
    "improved-v2",
    "improved-v3",
    "improved-v4",
    "improved-v5",
    "improved-v6",
]


@dataclass(frozen=True)
class PlannerTakeoverConfig:
    """Readable bounds for a short planner takeover rule."""

    name: str
    label: str
    hold_steps: int = 3
    time_to_floor_max: float = 0.22
    predicted_x_min: float = 0.35
    predicted_x_max: float = 1.75
    net_clearance_max: float = 0.05
    require_ball_vx_positive: bool = True
    allow_intercept: bool = True
    allow_net_guard: bool = True
    require_grounded_agent: bool = False
    require_planner_jump: bool = False


TAKEOVER_CONFIGS: dict[str, PlannerTakeoverConfig] = {
    "planner_takeover_safe": PlannerTakeoverConfig(
        name="planner_takeover_safe",
        label="structural/planner: 3-frame takeover on early safe intercept geometry",
    ),
    "planner_takeover_strict": PlannerTakeoverConfig(
        name="planner_takeover_strict",
        label="structural/planner: stricter low-time intercept with planner jump",
        time_to_floor_max=0.18,
        predicted_x_min=0.45,
        predicted_x_max=1.55,
        require_planner_jump=True,
    ),
    "planner_takeover_netclear": PlannerTakeoverConfig(
        name="planner_takeover_netclear",
        label="structural/planner: takeover only for low predicted net-clearance guard",
        allow_intercept=False,
        net_clearance_max=0.08,
    ),
    "planner_takeover_grounded": PlannerTakeoverConfig(
        name="planner_takeover_grounded",
        label="structural/planner: safe intercept takeover only while grounded",
        require_grounded_agent=True,
    ),
    "planner_takeover_wide": PlannerTakeoverConfig(
        name="planner_takeover_wide",
        label="structural/planner: wider early intercept geometry screen",
        time_to_floor_max=0.30,
        predicted_x_min=0.24,
        predicted_x_max=1.95,
    ),
}


class PlannerTakeoverPolicy(SlimeVolleyNetPressurePolicy):
    """Transient wrapper that delegates only selected earlier states to planner."""

    def __init__(self, config: PlannerTakeoverConfig) -> None:
        super().__init__()
        self._takeover_config = config
        self._planner = SlimeVolleyPlannerPolicy(RALLY_SERVE_CONFIG)
        self._takeover_left = 0
        self._last_takeover_step = -10_000
        self.total_opportunities = 0
        self.total_fired = 0
        self.total_action_changes = 0
        self.takeover_action_counts: Counter[str] = Counter()
        self.opportunity_modes: Counter[str] = Counter()

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._planner.reset(seed)
        self._takeover_left = 0
        self._last_takeover_step = -10_000
        self.total_opportunities = 0
        self.total_fired = 0
        self.total_action_changes = 0
        self.takeover_action_counts.clear()
        self.opportunity_modes.clear()

    def _takeover_allowed(
        self,
        *,
        values: np.ndarray,
        planner_action: np.ndarray,
        planner_diagnostics: dict[str, Any],
    ) -> bool:
        cfg = self._takeover_config
        planner = planner_diagnostics.get("planner") or {}
        planner_mode = str(planner_diagnostics.get("mode", ""))
        if self._last_diagnostics.get("mode") == "rally_serve":
            return False
        if cfg.require_ball_vx_positive and float(values[6]) <= 0.0:
            return False
        if cfg.require_grounded_agent and float(values[1]) > 0.20:
            return False
        if cfg.require_planner_jump and np.asarray(planner_action, dtype=int).reshape(-1)[2] <= 0:
            return False
        if bool(planner.get("wall_bounce_imminent")):
            return False
        time_to_floor = planner.get("time_to_floor")
        if time_to_floor is None or float(time_to_floor) > cfg.time_to_floor_max:
            return False
        predicted_x = planner.get("predicted_intercept_x")
        if predicted_x is None or not cfg.predicted_x_min <= float(predicted_x) <= cfg.predicted_x_max:
            return False

        net_clearance = planner.get("net_clearance")
        low_net = net_clearance is not None and float(net_clearance) <= cfg.net_clearance_max
        intercept_mode = planner_mode == "planner_intercept" and cfg.allow_intercept
        net_guard_mode = planner_mode == "planner_net_clearance_guard" and cfg.allow_net_guard and low_net
        return intercept_mode or net_guard_mode

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        planner_action = self._planner.act(obs)
        planner_diagnostics = self._planner.diagnostics()
        base_action = super().act(obs)
        base_diagnostics = dict(self._last_diagnostics)

        if self._takeover_allowed(
            values=values,
            planner_action=planner_action,
            planner_diagnostics=planner_diagnostics,
        ):
            self.total_opportunities += 1
            self.opportunity_modes[str(planner_diagnostics.get("mode", "unknown"))] += 1
            self._takeover_left = max(self._takeover_left, self._takeover_config.hold_steps)

        if self._takeover_left > 0 and base_diagnostics.get("mode") != "rally_serve":
            self._takeover_left -= 1
            self.total_fired += 1
            self._last_takeover_step = self._steps
            planner_action = np.asarray(planner_action, dtype=np.int8).reshape(-1)[:3]
            if _action_key_for_policy(planner_action) != _action_key_for_policy(base_action):
                self.total_action_changes += 1
            self.takeover_action_counts[_action_key_for_policy(planner_action)] += 1
            return self._record_diagnostics(
                mode=f"{self._takeover_config.name}:{planner_diagnostics.get('mode', 'unknown')}",
                action=planner_action.copy(),
                target_x=(planner_diagnostics.get("planner") or {}).get("predicted_intercept_x"),
                reason=self._takeover_config.label,
            )

        self._last_diagnostics = {
            **base_diagnostics,
            "planner_takeover": {
                "candidate": self._takeover_config.name,
                "planner_mode": planner_diagnostics.get("mode"),
                "planner_action": _action_key_for_policy(planner_action),
                "frames_since_takeover": self._steps - self._last_takeover_step,
                "planner": planner_diagnostics.get("planner"),
            },
        }
        return base_action

    def diagnostics(self) -> dict[str, Any]:
        diagnostics = super().diagnostics()
        diagnostics.setdefault("planner_takeover", {})
        diagnostics["planner_takeover"].update(
            {
                "candidate": self._takeover_config.name,
                "frames_since_takeover": self._steps - self._last_takeover_step,
            }
        )
        return diagnostics

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["planner_takeover_probe"] = asdict(self._takeover_config)
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in TAKEOVER_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return PlannerTakeoverPolicy(TAKEOVER_CONFIGS[candidate])


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int], *, trace_window: int = 0) -> dict[str, Any]:
    env = make_slimevolley_env()
    policy = _policy_for_candidate(candidate)
    opponent = make_slimevolley_opponent(opponent_name)
    scores: list[float] = []
    outcomes: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    terminal_modes: Counter[str] = Counter()
    takeover_point_outcomes: Counter[str] = Counter()
    steps = 0
    points_won = 0
    points_lost = 0
    try:
        for seed in seeds:
            episode = run_slimevolley_episode(
                env=env,
                policy=policy,
                opponent=opponent,
                seed=seed,
                trace_window=trace_window,
            )
            scores.append(float(episode.score))
            outcomes[episode.outcome] += 1
            action_counts.update(episode.action_counts)
            steps += int(episode.steps)
            for event in episode.point_events:
                if event.get("outcome") == "point_won":
                    points_won += 1
                elif event.get("outcome") == "point_lost":
                    points_lost += 1
                diagnostics = event.get("policy_diagnostics") or {}
                mode = diagnostics.get("mode")
                if mode:
                    terminal_modes[str(mode)] += 1
                takeover = diagnostics.get("planner_takeover") or {}
                frames_since = takeover.get("frames_since_takeover")
                if isinstance(frames_since, int) and frames_since <= 24:
                    takeover_point_outcomes[str(event.get("outcome"))] += 1
    finally:
        env.close()

    if candidate == "net_pressure_reference":
        label = "reference"
    elif candidate == "baseline_rnn":
        label = "neural comparator"
    else:
        label = TAKEOVER_CONFIGS[candidate].label
    return {
        "candidate": candidate,
        "label": label,
        "opponent": opponent_name,
        "seeds": f"{seeds[0]}..{seeds[-1]}",
        "episodes": len(seeds),
        "mean": float(np.mean(scores)) if scores else None,
        "std": float(np.std(scores)) if scores else None,
        "wins": int(outcomes.get("win", 0)),
        "losses": int(outcomes.get("loss", 0)),
        "draws": int(outcomes.get("draw", 0)),
        "steps": steps,
        "points_won": points_won,
        "points_lost": points_lost,
        "takeover_opportunities": int(getattr(policy, "total_opportunities", 0)),
        "takeover_fired": int(getattr(policy, "total_fired", 0)),
        "takeover_action_changes": int(getattr(policy, "total_action_changes", 0)),
        "takeover_action_counts": dict(sorted(getattr(policy, "takeover_action_counts", {}).items())),
        "opportunity_modes": dict(sorted(getattr(policy, "opportunity_modes", {}).items())),
        "takeover_point_outcomes": dict(sorted(takeover_point_outcomes.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
    }


def run_phase(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *TAKEOVER_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn"]
    else:
        raise ValueError(f"unknown phase {phase!r}")

    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(
                candidate,
                opponent,
                seeds,
                trace_window=trace_window if opponent == "builtin" else 0,
            )
            rows.append(row)
            print(
                f"{phase:6s} {candidate:30s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} opps={row['takeover_opportunities']} "
                f"fired={row['takeover_fired']} changes={row['takeover_action_changes']}",
                flush=True,
            )
    return {
        "phase": phase,
        "seed_list": seeds,
        "opponents": opponents,
        "candidates": selected,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["screen", "full"], default="screen")
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--trace-window", type=int, default=24)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_5_planner_takeover_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only planner-takeover structural probe",
        "holdout_audit_used": False,
        "phase_result": run_phase(args.phase, args.candidate, trace_window=args.trace_window),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        payload_to_write = existing if isinstance(existing, dict) and "runs" in existing else {"runs": [existing]}
        payload_to_write["runs"].append(payload)
    else:
        payload_to_write = {"runs": [payload]}
    args.output.write_text(json.dumps(payload_to_write, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.output}", flush=True)


if __name__ == "__main__":
    main()
