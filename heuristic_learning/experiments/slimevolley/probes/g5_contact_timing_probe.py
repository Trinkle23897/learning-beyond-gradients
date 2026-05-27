"""Development-only contact-timing probes for SlimeVolley generation 5.

The previous generation-5 probes showed that post-contact macros and broad
front-net pressure did not close the hard archived-opponent gap. This script
keeps the next step narrow: inspect low front-court terminal traces, then screen
small structural jump/contact overrides around `net-pressure`.

Only generation-5 development seeds are used. The script writes an append-only
JSON artifact and does not edit maintained policies or canonical ledgers.
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
    ACTION_BACKWARD,
    ACTION_NOOP,
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyNetPressurePolicy,
    _action_key_for_policy,
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


@dataclass(frozen=True)
class ContactTimingConfig:
    """Readable bounds for one low-contact jump timing rule."""

    name: str
    label: str
    action_style: str
    require_positive_vx: bool = False
    ball_x_min: float = 0.04
    ball_x_max: float = 0.36
    ball_y_min: float = 0.16
    ball_y_max: float = 0.36
    ball_vy_max: float = -0.95
    dx_abs_max: float = 0.30
    min_agent_y_above_ball: float = 0.06
    allowed_modes: tuple[str, ...] = ("grounded_low_receive", "late_low_ball_guard", "low_ball_rescue")


CONTACT_CONFIGS: dict[str, ContactTimingConfig] = {
    "low_commit_jump": ContactTimingConfig(
        name="low_commit_jump",
        label="structural: keep base movement but jump on very low descending front receive",
        action_style="base_jump",
    ),
    "low_back_jump": ContactTimingConfig(
        name="low_back_jump",
        label="structural: backward+jump on very low descending front receive",
        action_style="back_jump",
    ),
    "low_noop_jump": ContactTimingConfig(
        name="low_noop_jump",
        label="structural: vertical jump on very low descending front receive",
        action_style="noop_jump",
    ),
    "low_positive_vx_jump": ContactTimingConfig(
        name="low_positive_vx_jump",
        label="structural/history: jump only when low ball is still moving rearward",
        action_style="base_jump",
        require_positive_vx=True,
    ),
    "low_positive_vx_back_jump": ContactTimingConfig(
        name="low_positive_vx_back_jump",
        label="structural/history: backward+jump only when low ball is still moving rearward",
        action_style="back_jump",
        require_positive_vx=True,
    ),
}


def _action_key(action: Any) -> str:
    values = np.asarray(action if action is not None else [0, 0, 0], dtype=int).reshape(-1)[:3]
    return "".join(str(int(value > 0)) for value in values)


def _low_contact_frame(frame: dict[str, Any]) -> bool:
    state = frame.get("state", {})
    if not isinstance(state, dict):
        return False
    ball_x = float(state.get("ball_x", 999.0))
    ball_y = float(state.get("ball_y", 999.0))
    ball_vy = float(state.get("ball_vy", 999.0))
    agent_x = float(state.get("agent_x", -999.0))
    return (
        0.02 <= ball_x <= 0.40
        and 0.14 <= ball_y <= 0.40
        and ball_vy <= -0.75
        and abs(agent_x - ball_x) <= 0.38
    )


class ContactTimingPolicy(SlimeVolleyNetPressurePolicy):
    """Transient wrapper with a narrow low-contact jump timing override."""

    def __init__(self, config: ContactTimingConfig) -> None:
        super().__init__()
        self._timing_config = config
        self.total_override_frames = 0
        self.total_candidate_frames = 0

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self.total_override_frames = 0
        self.total_candidate_frames = 0

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        action = super().act(obs)
        if self._last_diagnostics.get("mode") == "rally_serve":
            return action

        cfg = self._timing_config
        base_mode = str(self._last_diagnostics.get("mode", ""))
        if base_mode not in cfg.allowed_modes:
            return action

        x, agent_y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        low_contact_candidate = (
            cfg.ball_x_min <= ball_x <= cfg.ball_x_max
            and cfg.ball_y_min <= ball_y <= cfg.ball_y_max
            and ball_vy <= cfg.ball_vy_max
            and abs(x - ball_x) <= cfg.dx_abs_max
            and agent_y >= ball_y + cfg.min_agent_y_above_ball
            and (not cfg.require_positive_vx or ball_vx >= 0.0)
        )
        if not low_contact_candidate:
            return action

        self.total_candidate_frames += 1
        if cfg.action_style == "base_jump":
            override = action.copy()
            override[2] = 1
        elif cfg.action_style == "back_jump":
            override = _with_jump(ACTION_BACKWARD.copy(), True)
        elif cfg.action_style == "noop_jump":
            override = _with_jump(ACTION_NOOP.copy(), True)
        else:
            raise ValueError(f"unknown action style {cfg.action_style!r}")

        self.total_override_frames += 1
        return self._record_diagnostics(
            mode=cfg.name,
            action=override,
            target_x=float(ball_x),
            reason=cfg.label,
        )

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["contact_timing_probe"] = self._timing_config.__dict__
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in CONTACT_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return ContactTimingPolicy(CONTACT_CONFIGS[candidate])


def trace_diagnostics() -> dict[str, Any]:
    """Collect low-contact trace summaries for net-pressure and baseline-rnn."""

    rows: list[dict[str, Any]] = []
    for policy_name in ["net_pressure_reference", "baseline_rnn"]:
        for opponent_name in HARD_OPPONENTS:
            env = make_slimevolley_env()
            policy = _policy_for_candidate(policy_name)
            opponent = make_slimevolley_opponent(opponent_name)
            frame_counts: Counter[str] = Counter()
            event_counts: Counter[str] = Counter()
            mode_counts: Counter[str] = Counter()
            action_counts: Counter[str] = Counter()
            dx_values: list[float] = []
            ball_vx_values: list[float] = []
            ball_vy_values: list[float] = []
            try:
                for seed in SHORT_SEEDS:
                    episode = run_slimevolley_episode(
                        env=env,
                        policy=policy,
                        opponent=opponent,
                        seed=seed,
                        trace_window=32,
                    )
                    for event in episode.point_events:
                        event_outcome = str(event.get("outcome", "unknown"))
                        event_has_low_contact = False
                        for frame in event.get("pre_event_trace", []):
                            if not _low_contact_frame(frame):
                                continue
                            event_has_low_contact = True
                            action_key = str(frame.get("action", ""))
                            state = frame.get("state", {})
                            diagnostics = frame.get("policy_diagnostics", {})
                            mode = diagnostics.get("mode") if isinstance(diagnostics, dict) else None
                            action_counts[action_key] += 1
                            frame_counts[f"{event_outcome}:frames"] += 1
                            if action_key.endswith("1"):
                                frame_counts[f"{event_outcome}:jump_frames"] += 1
                            if isinstance(mode, str):
                                mode_counts[f"{event_outcome}:{mode}"] += 1
                            if isinstance(state, dict):
                                agent_x = float(state.get("agent_x", 0.0))
                                ball_x = float(state.get("ball_x", 0.0))
                                dx_values.append(agent_x - ball_x)
                                ball_vx_values.append(float(state.get("ball_vx", 0.0)))
                                ball_vy_values.append(float(state.get("ball_vy", 0.0)))
                        if event_has_low_contact:
                            event_counts[event_outcome] += 1
            finally:
                env.close()
            rows.append(
                {
                    "policy": policy_name,
                    "opponent": opponent_name,
                    "seeds": f"{SHORT_SEEDS[0]}..{SHORT_SEEDS[-1]}",
                    "low_contact_events": dict(sorted(event_counts.items())),
                    "low_contact_frames": dict(sorted(frame_counts.items())),
                    "action_counts": dict(action_counts.most_common()),
                    "mode_counts": dict(mode_counts.most_common(16)),
                    "mean_agent_minus_ball_x": float(np.mean(dx_values)) if dx_values else None,
                    "mean_ball_vx": float(np.mean(ball_vx_values)) if ball_vx_values else None,
                    "mean_ball_vy": float(np.mean(ball_vy_values)) if ball_vy_values else None,
                }
            )
            print(
                f"diagnose {policy_name:22s} vs {opponent_name:11s} "
                f"events={dict(event_counts)} frames={dict(frame_counts)} actions={dict(action_counts.most_common(4))}",
                flush=True,
            )
    return {
        "phase": "diagnose",
        "seed_list": SHORT_SEEDS,
        "opponents": HARD_OPPONENTS,
        "rows": rows,
    }


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int], *, trace_window: int) -> dict[str, Any]:
    env = make_slimevolley_env()
    policy = _policy_for_candidate(candidate)
    opponent = make_slimevolley_opponent(opponent_name)
    scores: list[float] = []
    outcomes: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    terminal_modes: Counter[str] = Counter()
    steps = 0
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
        else CONTACT_CONFIGS[candidate].label
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
        "override_frames": int(getattr(policy, "total_override_frames", 0)),
        "candidate_frames": int(getattr(policy, "total_candidate_frames", 0)),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
    }


def run_screen(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *CONTACT_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn", "low_positive_vx_jump"]
    else:
        raise ValueError(f"unknown screen phase {phase!r}")

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
                f"{phase:8s} {candidate:26s} vs {opponent:11s} "
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
    parser.add_argument("--phase", choices=["diagnose", "screen", "full"], default="diagnose")
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--trace-window", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_5_contact_timing_probe.json"),
    )
    args = parser.parse_args()
    phase_result = (
        trace_diagnostics()
        if args.phase == "diagnose"
        else run_screen(args.phase, args.candidate, trace_window=args.trace_window)
    )
    payload = {
        "protocol": "generation-5 development-only contact-timing diagnostic/probe",
        "holdout_audit_used": False,
        "phase_result": phase_result,
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
