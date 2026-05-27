"""Development-only phase-pressure probes for SlimeVolley generation 5.

This script evaluates transient structural candidates around the generation-5
`net-pressure` probe. It uses generation-5 development seeds only and writes an
append-only JSON artifact; it does not edit maintained policies or ledgers.
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
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyNetPressurePolicy,
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
class PhasePressureConfig:
    """Readable bounds for an opponent-side low-pressure phase rule."""

    name: str
    label: str
    ball_x_min: float = -0.85
    ball_x_max: float = -0.02
    ball_y_min: float = 0.18
    ball_y_max: float = 0.54
    ball_vx_max: float = -0.15
    ball_vy_max: float = 0.16
    opponent_y_max: float = 0.20
    opponent_x_min: float | None = None
    opponent_x_max: float | None = None
    require_recent_own_contact: bool = False
    recent_contact_window: int = 6
    require_two_frame_opponent_side: bool = False
    require_agent_grounded: bool = False


PHASE_CONFIGS: dict[str, PhasePressureConfig] = {
    "phase_posture_refined": PhasePressureConfig(
        name="phase_posture_refined",
        label="structural: low opponent-side pressure with stricter opponent posture",
        ball_y_max=0.50,
        opponent_y_max=0.18,
    ),
    "phase_posture_low": PhasePressureConfig(
        name="phase_posture_low",
        label="structural: low-height preserving opponent-side pressure",
        ball_y_max=0.46,
        opponent_y_max=0.20,
    ),
    "phase_posture_back": PhasePressureConfig(
        name="phase_posture_back",
        label="structural: opponent-side pressure only when opponent is deeper",
        ball_y_max=0.58,
        opponent_y_max=0.24,
        opponent_x_min=0.76,
    ),
    "phase_posture_front": PhasePressureConfig(
        name="phase_posture_front",
        label="structural: opponent-side pressure only when opponent is front/low",
        ball_y_max=0.54,
        opponent_y_max=0.22,
        opponent_x_max=0.72,
    ),
    "phase_recent_own": PhasePressureConfig(
        name="phase_recent_own",
        label="structural/history: pressure only after recent own contact",
        ball_y_max=0.56,
        opponent_y_max=0.22,
        require_recent_own_contact=True,
    ),
    "phase_two_frame": PhasePressureConfig(
        name="phase_two_frame",
        label="structural/history: pressure after two opponent-side frames",
        ball_y_max=0.56,
        opponent_y_max=0.22,
        require_two_frame_opponent_side=True,
    ),
    "phase_two_frame_back": PhasePressureConfig(
        name="phase_two_frame_back",
        label="structural/history: two-frame pressure only when opponent is deeper",
        ball_y_max=0.58,
        opponent_y_max=0.24,
        opponent_x_min=0.76,
        require_two_frame_opponent_side=True,
    ),
    "phase_two_frame_midback": PhasePressureConfig(
        name="phase_two_frame_midback",
        label="structural/history: two-frame pressure when opponent is mid/deep",
        ball_y_max=0.56,
        opponent_y_max=0.22,
        opponent_x_min=0.62,
        require_two_frame_opponent_side=True,
    ),
    "phase_two_frame_strict": PhasePressureConfig(
        name="phase_two_frame_strict",
        label="structural/history: stricter two-frame low continuing pressure",
        ball_y_max=0.50,
        ball_vx_max=-0.20,
        opponent_y_max=0.20,
        require_two_frame_opponent_side=True,
    ),
    "phase_grounded": PhasePressureConfig(
        name="phase_grounded",
        label="structural: pressure only while agent is grounded",
        ball_y_max=0.56,
        opponent_y_max=0.22,
        require_agent_grounded=True,
    ),
}


def _action_key(action: Any) -> str:
    values = np.asarray(action if action is not None else [0, 0, 0], dtype=int).reshape(-1)[:3]
    return "".join(str(int(value > 0)) for value in values)


class PhasePressurePolicy(SlimeVolleyNetPressurePolicy):
    """Transient wrapper that adds a phase-gated opponent-side pressure rule."""

    def __init__(self, config: PhasePressureConfig) -> None:
        super().__init__()
        self._phase_config = config
        self.total_override_frames = 0
        self._history: deque[np.ndarray] = deque(maxlen=5)
        self._previous_values: np.ndarray | None = None
        self._recent_own_contact = 999
        self._opponent_side_frames = 0

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._history.clear()
        self._previous_values = None
        self._recent_own_contact = 999
        self._opponent_side_frames = 0

    def _update_phase_features(self, values: np.ndarray) -> float:
        if self._previous_values is None:
            self._recent_own_contact += 1
        else:
            prev = self._previous_values
            own_vx_flip = prev[6] > 0.08 and values[6] < -0.08 and values[4] > -0.10
            own_vy_flip = prev[7] < -0.10 and values[7] > 0.04 and values[4] > -0.10 and values[5] < 1.05
            self._recent_own_contact = 0 if own_vx_flip or own_vy_flip else self._recent_own_contact + 1
        if values[4] < -0.02:
            self._opponent_side_frames += 1
        else:
            self._opponent_side_frames = 0

        window = [*self._history, values]
        span = max(1, len(window) - 1)
        stacked_ball_vx = float((window[-1][4] - window[0][4]) / span)
        self._history.append(values.copy())
        self._previous_values = values.copy()
        return stacked_ball_vx

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        stacked_ball_vx = self._update_phase_features(values)
        action = super().act(obs)
        if self._last_diagnostics.get("mode") == "rally_serve":
            return action

        cfg = self._phase_config
        x, y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy, opp_x, opp_y = values[:10]
        del x
        if cfg.opponent_x_min is not None and opp_x < cfg.opponent_x_min:
            return action
        if cfg.opponent_x_max is not None and opp_x > cfg.opponent_x_max:
            return action
        if cfg.require_recent_own_contact and self._recent_own_contact > cfg.recent_contact_window:
            return action
        if cfg.require_two_frame_opponent_side and self._opponent_side_frames < 2:
            return action
        if cfg.require_agent_grounded and y > 0.32:
            return action

        should_pressure = (
            cfg.ball_x_min <= ball_x <= cfg.ball_x_max
            and cfg.ball_y_min <= ball_y <= cfg.ball_y_max
            and min(ball_vx, stacked_ball_vx) <= cfg.ball_vx_max
            and ball_vy <= cfg.ball_vy_max
            and opp_y <= cfg.opponent_y_max
        )
        if should_pressure:
            pressure_action = _with_jump(ACTION_FORWARD.copy(), True)
            self.total_override_frames += 1
            return self._record_diagnostics(
                mode=cfg.name,
                action=pressure_action,
                target_x=float(ball_x),
                reason=cfg.label,
            )
        return action

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["phase_pressure_probe"] = self._phase_config.__dict__
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in PHASE_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return PhasePressurePolicy(PHASE_CONFIGS[candidate])


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
        else PHASE_CONFIGS[candidate].label
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
        "override_frames": int(getattr(policy, "total_override_frames", 0)),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
    }


def run_phase(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *PHASE_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn", "phase_posture_refined"]
    else:
        raise ValueError(f"unknown phase {phase!r}")

    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(candidate, opponent, seeds, trace_window=trace_window if opponent == "builtin" else 0)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:28s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} overrides={row['override_frames']}",
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
        default=Path("experiments/slimevolley/results/generation_5_phase_pressure_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only phase-pressure probe",
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
