"""Development-only rally-setup probes for SlimeVolley generation 5.

These transient candidates test whether the heuristic gap to the packaged RNN
comes from positioning before the next exchange rather than from a final-frame
low-contact action. They use generation-5 development seeds only and write an
append-only JSON artifact; they do not edit maintained policies or ledgers.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.policies.slimevolley import (
    ACTION_FORWARD,
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyNetPressurePolicy,
    _move_toward,
    _state,
    _with_jump,
)
from hl_benchmark.slimevolley.adapter import make_slimevolley_env, run_slimevolley_episode
from hl_benchmark.slimevolley.opponents import make_slimevolley_opponent


SHORT_SEEDS = list(range(12000, 12016))
FULL_SEEDS = list(range(12000, 12050))
SCREEN_OPPONENTS = ["builtin", "improved-v3", "improved-v4", "improved-v5", "improved-v6"]
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
class RallySetupConfig:
    """Readable phase-controller bounds for one rally-setup candidate."""

    name: str
    label: str
    anchor_x: float
    hold_frames: int
    contact_x_min: float = -0.12
    contact_x_max: float = 0.62
    exit_ball_x: float = -0.06
    exit_ball_vx: float = 0.04
    max_ball_y: float = 1.35
    pressure_low: bool = False
    pressure_ball_x_min: float = -0.70
    pressure_ball_x_max: float = -0.02
    pressure_ball_y_min: float = 0.18
    pressure_ball_y_max: float = 0.58
    pressure_ball_vx_max: float = -0.12
    pressure_ball_vy_max: float = 0.18
    pressure_opponent_y_max: float = 0.24


SETUP_CONFIGS: dict[str, RallySetupConfig] = {
    "setup_anchor_035_10": RallySetupConfig(
        name="setup_anchor_035_10",
        label="structural/history: post-contact front anchor at x=0.35 for 10 frames",
        anchor_x=0.35,
        hold_frames=10,
    ),
    "setup_anchor_050_14": RallySetupConfig(
        name="setup_anchor_050_14",
        label="structural/history: slightly safer post-contact anchor at x=0.50 for 14 frames",
        anchor_x=0.50,
        hold_frames=14,
    ),
    "setup_anchor_035_pressure": RallySetupConfig(
        name="setup_anchor_035_pressure",
        label="structural/history: front anchor plus low opponent-side pressure",
        anchor_x=0.35,
        hold_frames=10,
        pressure_low=True,
    ),
    "setup_anchor_050_pressure": RallySetupConfig(
        name="setup_anchor_050_pressure",
        label="structural/history: safer front anchor plus low opponent-side pressure",
        anchor_x=0.50,
        hold_frames=14,
        pressure_low=True,
    ),
}


class RallySetupPolicy(SlimeVolleyNetPressurePolicy):
    """Transient net-pressure wrapper with an explicit post-contact setup phase."""

    def __init__(self, config: RallySetupConfig) -> None:
        super().__init__()
        self._setup_config = config
        self._previous_values: np.ndarray | None = None
        self._setup_left = 0
        self.total_anchor_frames = 0
        self.total_pressure_frames = 0
        self.total_contact_events = 0

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._previous_values = None
        self._setup_left = 0
        self.total_anchor_frames = 0
        self.total_pressure_frames = 0
        self.total_contact_events = 0

    def _update_setup_phase(self, values: np.ndarray) -> None:
        cfg = self._setup_config
        if self._previous_values is None:
            self._previous_values = values.copy()
            return

        previous = self._previous_values
        own_vx_flip = previous[6] > 0.08 and values[6] < -0.08
        own_upward_flip = previous[7] < -0.10 and values[7] > 0.04
        near_own_contact = cfg.contact_x_min <= values[4] <= cfg.contact_x_max and values[5] <= cfg.max_ball_y
        if near_own_contact and (own_vx_flip or own_upward_flip):
            self._setup_left = cfg.hold_frames
            self.total_contact_events += 1
        elif self._setup_left > 0:
            self._setup_left -= 1
        self._previous_values = values.copy()

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        self._update_setup_phase(values)
        action = super().act(obs)
        if self._last_diagnostics.get("mode") == "rally_serve":
            return action

        cfg = self._setup_config
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy, _opp_x, opp_y = values[:10]
        if self._setup_left <= 0:
            return action
        if ball_x >= cfg.exit_ball_x or ball_vx >= cfg.exit_ball_vx:
            return action

        if (
            cfg.pressure_low
            and cfg.pressure_ball_x_min <= ball_x <= cfg.pressure_ball_x_max
            and cfg.pressure_ball_y_min <= ball_y <= cfg.pressure_ball_y_max
            and ball_vx <= cfg.pressure_ball_vx_max
            and ball_vy <= cfg.pressure_ball_vy_max
            and opp_y <= cfg.pressure_opponent_y_max
        ):
            pressure_action = _with_jump(ACTION_FORWARD.copy(), True)
            self.total_pressure_frames += 1
            return self._record_diagnostics(
                mode=f"{cfg.name}_pressure",
                action=pressure_action,
                target_x=float(ball_x),
                reason=cfg.label,
            )

        anchor_action = _with_jump(_move_toward(float(x), cfg.anchor_x, self._config.x_margin), False)
        self.total_anchor_frames += 1
        return self._record_diagnostics(
            mode=cfg.name,
            action=anchor_action,
            target_x=cfg.anchor_x,
            reason=cfg.label,
        )

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["rally_setup_probe"] = self._setup_config.__dict__
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in SETUP_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return RallySetupPolicy(SETUP_CONFIGS[candidate])


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int], *, trace_window: int) -> dict[str, Any]:
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

    label = (
        "reference"
        if candidate == "net_pressure_reference"
        else "neural comparator"
        if candidate == "baseline_rnn"
        else SETUP_CONFIGS[candidate].label
    )
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
        "anchor_frames": int(getattr(policy, "total_anchor_frames", 0)),
        "pressure_frames": int(getattr(policy, "total_pressure_frames", 0)),
        "contact_events": int(getattr(policy, "total_contact_events", 0)),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
    }


def run_phase(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *SETUP_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn", "setup_anchor_050_pressure"]
    else:
        raise ValueError(f"unknown phase {phase!r}")

    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(
                candidate,
                opponent,
                seeds,
                trace_window=trace_window if opponent in {"builtin", "improved-v5", "improved-v6"} else 0,
            )
            rows.append(row)
            print(
                f"{phase:6s} {candidate:28s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} anchors={row['anchor_frames']} pressures={row['pressure_frames']}",
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
    parser.add_argument("--trace-window", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_5_rally_setup_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only rally-setup probe",
        "holdout_audit_used": False,
        "phase_result": run_phase(args.phase, args.candidate, trace_window=args.trace_window),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if isinstance(existing, dict) and "runs" in existing:
            existing["runs"].append(payload)
            payload_to_write = existing
        else:
            payload_to_write = {"runs": [existing, payload]}
    else:
        payload_to_write = {"runs": [payload]}
    args.output.write_text(json.dumps(payload_to_write, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.output}", flush=True)


if __name__ == "__main__":
    main()
