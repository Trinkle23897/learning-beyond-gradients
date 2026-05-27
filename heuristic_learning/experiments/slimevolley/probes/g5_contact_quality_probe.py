"""Development-only contact-quality probes for SlimeVolley generation 5.

Earlier generation-5 probes showed that terminal-frame jump copies and local
approach tweaks do not close the hard archived-opponent gap. This probe tests a
slightly higher-level idea: use short history to decide whether a front-court
pressure opportunity is contact-quality positive, risky, or better handled by a
brace/recovery action.

Only generation-5 development seeds are used. The script writes an append-only
JSON artifact and does not edit maintained policies or canonical ledgers.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.policies.slimevolley import (
    ACTION_FORWARD,
    ACTION_NOOP,
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyNetPressurePolicy,
    SlimeVolleyRallyServePolicy,
    _state,
    _with_jump,
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

ACTION_BOTH = np.asarray([1, 1, 0], dtype=np.int8)
ACTION_BOTH_JUMP = np.asarray([1, 1, 1], dtype=np.int8)


@dataclass(frozen=True)
class ContactQualityConfig:
    """Readable bounds for one contact-quality pressure rule."""

    name: str
    label: str
    style: str
    require_recent_opponent_contact: bool = False
    suppress_recent_own_contact: bool = False
    recent_contact_window: int = 8
    min_low_descent_frames: int = 2
    ball_x_min: float = -0.08
    ball_x_max: float = 0.55
    ball_y_min: float = 0.58
    ball_y_max: float = 1.30
    ball_vx_max: float = -0.02
    ball_vy_max: float = 0.08
    dx_min: float = 0.08
    dx_max: float = 0.72


QUALITY_CONFIGS: dict[str, ContactQualityConfig] = {
    "quality_gate_recent_opp": ContactQualityConfig(
        name="quality_gate_recent_opp",
        label="structural/history: only pressure after recent opponent-contact evidence",
        style="gated_101",
        require_recent_opponent_contact=True,
    ),
    "quality_gate_no_recent_own": ContactQualityConfig(
        name="quality_gate_no_recent_own",
        label="structural/history: suppress front pressure immediately after own contact",
        style="gated_101",
        suppress_recent_own_contact=True,
    ),
    "quality_two_frame_descent": ContactQualityConfig(
        name="quality_two_frame_descent",
        label="structural/history: pressure only after a two-frame front-court descent",
        style="gated_101",
        min_low_descent_frames=3,
        ball_y_min=0.50,
        ball_y_max=1.10,
    ),
    "quality_brace_110": ContactQualityConfig(
        name="quality_brace_110",
        label="structural/history: replace risky pressure with both-direction no-jump brace",
        style="brace_110",
        suppress_recent_own_contact=True,
        ball_y_min=0.50,
        ball_y_max=1.05,
    ),
    "quality_brace_111": ContactQualityConfig(
        name="quality_brace_111",
        label="structural/history: replace risky pressure with both-direction jump brace",
        style="brace_111",
        suppress_recent_own_contact=True,
        ball_y_min=0.50,
        ball_y_max=1.05,
    ),
    "quality_recover_noop": ContactQualityConfig(
        name="quality_recover_noop",
        label="structural/history: suppress risky pressure after own contact and hold",
        style="noop",
        suppress_recent_own_contact=True,
        ball_y_min=0.50,
        ball_y_max=1.05,
    ),
}


def _action_key(action: Any) -> str:
    values = np.asarray(action if action is not None else [0, 0, 0], dtype=int).reshape(-1)[:3]
    return "".join(str(int(value > 0)) for value in values)


class ContactQualityPolicy(SlimeVolleyNetPressurePolicy):
    """Transient wrapper with short-history pressure-quality gates."""

    def __init__(self, config: ContactQualityConfig) -> None:
        super().__init__()
        self._quality_config = config
        self._history: deque[np.ndarray] = deque(maxlen=6)
        self._previous_values: np.ndarray | None = None
        self._recent_own_contact = 999
        self._recent_opponent_contact = 999
        self.total_candidate_frames = 0
        self.total_override_frames = 0
        self.total_suppressed_frames = 0

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._history.clear()
        self._previous_values = None
        self._recent_own_contact = 999
        self._recent_opponent_contact = 999
        self.total_candidate_frames = 0
        self.total_override_frames = 0
        self.total_suppressed_frames = 0

    def _update_history(self, values: np.ndarray) -> tuple[float, int]:
        if self._previous_values is None:
            self._recent_own_contact += 1
            self._recent_opponent_contact += 1
        else:
            previous = self._previous_values
            own_contact = (
                (previous[6] > 0.08 and values[6] < -0.08 and values[4] > -0.10)
                or (previous[7] < -0.10 and values[7] > 0.04 and values[4] > -0.10 and values[5] < 1.05)
            )
            opponent_contact = previous[6] < -0.08 and values[6] > 0.08 and values[4] < 0.95
            self._recent_own_contact = 0 if own_contact else self._recent_own_contact + 1
            self._recent_opponent_contact = 0 if opponent_contact else self._recent_opponent_contact + 1

        window = [*self._history, values]
        span = max(1, len(window) - 1)
        stacked_ball_vx = float((window[-1][4] - window[0][4]) / span)
        low_descent_frames = sum(
            1
            for before, after in zip(window, window[1:])
            if -0.10 <= after[4] <= 0.62 and 0.42 <= after[5] <= 1.20 and after[5] < before[5] - 0.003
        )
        self._history.append(values.copy())
        self._previous_values = values.copy()
        return stacked_ball_vx, low_descent_frames

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        stacked_ball_vx, low_descent_frames = self._update_history(values)

        # Rebuild the net-pressure decision so candidates can fall back to the
        # rally-serve base action instead of stacking on top of net-pressure.
        action = SlimeVolleyRallyServePolicy.act(self, obs)
        if self._last_diagnostics.get("mode") == "rally_serve":
            return action

        cfg = self._quality_config
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        pressure_window = (
            cfg.ball_x_min <= ball_x <= cfg.ball_x_max
            and cfg.ball_y_min <= ball_y <= cfg.ball_y_max
            and min(ball_vx, stacked_ball_vx) <= cfg.ball_vx_max
            and ball_vy <= cfg.ball_vy_max
            and cfg.dx_min <= dx <= cfg.dx_max
        )
        if not pressure_window:
            return action

        self.total_candidate_frames += 1
        recent_own = self._recent_own_contact <= cfg.recent_contact_window
        recent_opp = self._recent_opponent_contact <= cfg.recent_contact_window
        quality_ok = low_descent_frames >= cfg.min_low_descent_frames
        if cfg.require_recent_opponent_contact and not recent_opp:
            quality_ok = False
        if cfg.suppress_recent_own_contact and recent_own:
            quality_ok = False

        if cfg.style == "gated_101":
            if not quality_ok:
                self.total_suppressed_frames += 1
                return action
            override = _with_jump(ACTION_FORWARD.copy(), True)
        elif cfg.style == "brace_110":
            override = ACTION_BOTH.copy() if not quality_ok else _with_jump(ACTION_FORWARD.copy(), True)
        elif cfg.style == "brace_111":
            override = ACTION_BOTH_JUMP.copy() if not quality_ok else _with_jump(ACTION_FORWARD.copy(), True)
        elif cfg.style == "noop":
            override = ACTION_NOOP.copy() if not quality_ok else _with_jump(ACTION_FORWARD.copy(), True)
        else:
            raise ValueError(f"unknown contact-quality style {cfg.style!r}")

        self.total_override_frames += 1
        return self._record_diagnostics(
            mode=cfg.name,
            action=override,
            target_x=float(ball_x),
            reason=cfg.label,
        )

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["contact_quality_probe"] = self._quality_config.__dict__
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in QUALITY_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return ContactQualityPolicy(QUALITY_CONFIGS[candidate])


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int], *, trace_window: int = 0) -> dict[str, Any]:
    env = make_slimevolley_env()
    policy = _policy_for_candidate(candidate)
    opponent = make_slimevolley_opponent(opponent_name)
    scores: list[float] = []
    outcomes: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    terminal_modes: Counter[str] = Counter()
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
    finally:
        env.close()
    return {
        "candidate": candidate,
        "label": "reference" if candidate in {"net_pressure_reference", "baseline_rnn"} else QUALITY_CONFIGS[candidate].label,
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
        "candidate_frames": int(getattr(policy, "total_candidate_frames", 0)),
        "override_frames": int(getattr(policy, "total_override_frames", 0)),
        "suppressed_frames": int(getattr(policy, "total_suppressed_frames", 0)),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
    }


def run_phase(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *QUALITY_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn"]
    else:
        raise ValueError(f"unknown phase {phase!r}")

    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(candidate, opponent, seeds, trace_window=trace_window if opponent == "builtin" else 0)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:32s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} frames={row['candidate_frames']} overrides={row['override_frames']} suppressed={row['suppressed_frames']}",
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
        default=Path("experiments/slimevolley/results/generation_5_contact_quality_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only contact-quality pressure probe",
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
