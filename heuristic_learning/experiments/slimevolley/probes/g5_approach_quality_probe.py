"""Development-only pre-contact approach probes for SlimeVolley generation 5.

Prior generation-5 probes showed that final-frame low-contact jump changes do
not close the hard archived-opponent gap. This script moves one step earlier:
it diagnoses approach quality several frames before low front-court terminal
windows and screens small structural rules that alter approach movement before
contact, not the terminal contact frame itself.

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
    ACTION_FORWARD,
    ACTION_NOOP,
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyNetPressurePolicy,
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
class ApproachConfig:
    """Readable bounds for one pre-contact approach rule."""

    name: str
    label: str
    action_style: str
    ball_x_min: float = 0.02
    ball_x_max: float = 0.52
    ball_y_min: float = 0.36
    ball_y_max: float = 0.92
    ball_vy_max: float = -0.32
    dx_min: float = 0.16
    dx_max: float = 0.62
    agent_y_max: float = 0.55
    suppress_existing_jump: bool = True


APPROACH_CONFIGS: dict[str, ApproachConfig] = {
    "approach_drive_jump": ApproachConfig(
        name="approach_drive_jump",
        label="structural: earlier forward+jump while still behind descending front-low ball",
        action_style="forward_jump",
        ball_y_min=0.44,
        ball_y_max=0.90,
        ball_vy_max=-0.50,
        dx_min=0.22,
        dx_max=0.78,
        suppress_existing_jump=False,
    ),
    "approach_vertical_jump": ApproachConfig(
        name="approach_vertical_jump",
        label="structural: earlier vertical jump when moderately aligned before front-low contact",
        action_style="noop_jump",
        ball_y_min=0.44,
        ball_y_max=0.90,
        ball_vy_max=-0.50,
        dx_min=0.14,
        dx_max=0.42,
        suppress_existing_jump=False,
    ),
    "approach_drive_nojump": ApproachConfig(
        name="approach_drive_nojump",
        label="structural: close front-low approach gap with forward/no-jump before contact",
        action_style="forward_nojump",
    ),
    "approach_far_drive_nojump": ApproachConfig(
        name="approach_far_drive_nojump",
        label="structural: far-behind front-low approach drive/no-jump",
        action_style="forward_nojump",
        ball_y_min=0.42,
        ball_y_max=0.78,
        ball_vy_max=-0.50,
        dx_min=0.54,
        dx_max=0.86,
    ),
    "approach_far_preserve_nojump": ApproachConfig(
        name="approach_far_preserve_nojump",
        label="structural: far-behind front-low approach preserve movement/no-jump",
        action_style="base_nojump",
        ball_y_min=0.42,
        ball_y_max=0.78,
        ball_vy_max=-0.50,
        dx_min=0.54,
        dx_max=0.86,
    ),
    "approach_far_vertical_set": ApproachConfig(
        name="approach_far_vertical_set",
        label="structural: far-behind front-low approach hold/no-jump",
        action_style="noop_nojump",
        ball_y_min=0.42,
        ball_y_max=0.78,
        ball_vy_max=-0.50,
        dx_min=0.54,
        dx_max=0.86,
    ),
    "approach_preserve_nojump": ApproachConfig(
        name="approach_preserve_nojump",
        label="structural: suppress premature jump while preserving base approach movement",
        action_style="base_nojump",
    ),
    "approach_vertical_set": ApproachConfig(
        name="approach_vertical_set",
        label="structural: stop horizontal drift before front-low contact",
        action_style="noop_nojump",
        dx_min=0.10,
        dx_max=0.34,
    ),
    "approach_rear_brake": ApproachConfig(
        name="approach_rear_brake",
        label="structural: brake rearward when close to low front-court contact",
        action_style="back_nojump",
        dx_min=0.08,
        dx_max=0.28,
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
        0.02 <= ball_x <= 0.42
        and 0.14 <= ball_y <= 0.42
        and ball_vy <= -0.70
        and abs(agent_x - ball_x) <= 0.42
    )


def _state_from_frame(frame: dict[str, Any]) -> dict[str, float]:
    state = frame.get("state", {})
    return state if isinstance(state, dict) else {}


class ApproachQualityPolicy(SlimeVolleyNetPressurePolicy):
    """Transient wrapper that changes approach before low front-court contact."""

    def __init__(self, config: ApproachConfig) -> None:
        super().__init__()
        self._approach_config = config
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

        cfg = self._approach_config
        x, agent_y, _vx, _vy, ball_x, ball_y, _ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        approach_window = (
            cfg.ball_x_min <= ball_x <= cfg.ball_x_max
            and cfg.ball_y_min <= ball_y <= cfg.ball_y_max
            and ball_vy <= cfg.ball_vy_max
            and cfg.dx_min <= dx <= cfg.dx_max
            and agent_y <= cfg.agent_y_max
        )
        if not approach_window:
            return action
        if cfg.suppress_existing_jump and action[2] > 0:
            # This is intentionally an approach rule, not another terminal-frame
            # contact override; avoid overriding base emergency jumps.
            return action

        self.total_candidate_frames += 1
        if cfg.action_style == "forward_nojump":
            override = ACTION_FORWARD.copy()
        elif cfg.action_style == "forward_jump":
            override = _with_jump(ACTION_FORWARD.copy(), True)
        elif cfg.action_style == "base_nojump":
            override = action.copy()
            override[2] = 0
        elif cfg.action_style == "noop_nojump":
            override = ACTION_NOOP.copy()
        elif cfg.action_style == "noop_jump":
            override = _with_jump(ACTION_NOOP.copy(), True)
        elif cfg.action_style == "back_nojump":
            override = ACTION_BACKWARD.copy()
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
        values["approach_quality_probe"] = self._approach_config.__dict__
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in APPROACH_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return ApproachQualityPolicy(APPROACH_CONFIGS[candidate])


def trace_diagnostics() -> dict[str, Any]:
    """Summarize approach frames before low front-court point events."""

    rows: list[dict[str, Any]] = []
    offsets = (16, 12, 8, 4)
    for policy_name in ["net_pressure_reference", "baseline_rnn"]:
        for opponent_name in HARD_OPPONENTS:
            env = make_slimevolley_env()
            policy = _policy_for_candidate(policy_name)
            opponent = make_slimevolley_opponent(opponent_name)
            samples: dict[int, list[dict[str, float | str]]] = {offset: [] for offset in offsets}
            event_counts: Counter[str] = Counter()
            action_counts: Counter[str] = Counter()
            try:
                for seed in SHORT_SEEDS:
                    episode = run_slimevolley_episode(
                        env=env,
                        policy=policy,
                        opponent=opponent,
                        seed=seed,
                        trace_window=48,
                    )
                    for event in episode.point_events:
                        trace = list(event.get("pre_event_trace", []))
                        low_indexes = [idx for idx, frame in enumerate(trace) if _low_contact_frame(frame)]
                        if not low_indexes:
                            continue
                        event_outcome = str(event.get("outcome", "unknown"))
                        event_counts[event_outcome] += 1
                        low_idx = low_indexes[-1]
                        for offset in offsets:
                            approach_idx = max(0, low_idx - offset)
                            frame = trace[approach_idx]
                            state = _state_from_frame(frame)
                            if not state:
                                continue
                            agent_x = float(state.get("agent_x", 0.0))
                            ball_x = float(state.get("ball_x", 0.0))
                            action_key = str(frame.get("action", ""))
                            action_counts[f"{event_outcome}:{offset}:{action_key}"] += 1
                            samples[offset].append(
                                {
                                    "outcome": event_outcome,
                                    "dx": agent_x - ball_x,
                                    "abs_dx": abs(agent_x - ball_x),
                                    "agent_x": agent_x,
                                    "agent_y": float(state.get("agent_y", 0.0)),
                                    "agent_vx": float(state.get("agent_vx", 0.0)),
                                    "ball_x": ball_x,
                                    "ball_y": float(state.get("ball_y", 0.0)),
                                    "ball_vx": float(state.get("ball_vx", 0.0)),
                                    "ball_vy": float(state.get("ball_vy", 0.0)),
                                    "jump": float(action_key.endswith("1")),
                                    "forward": float(action_key[:1] == "1"),
                                }
                            )
            finally:
                env.close()

            offset_summary: dict[str, dict[str, float | int | None]] = {}
            for offset, values in samples.items():
                offset_summary[str(offset)] = {
                    "count": len(values),
                    "mean_dx": float(np.mean([item["dx"] for item in values])) if values else None,
                    "mean_abs_dx": float(np.mean([item["abs_dx"] for item in values])) if values else None,
                    "mean_agent_y": float(np.mean([item["agent_y"] for item in values])) if values else None,
                    "mean_ball_y": float(np.mean([item["ball_y"] for item in values])) if values else None,
                    "mean_ball_vy": float(np.mean([item["ball_vy"] for item in values])) if values else None,
                    "jump_rate": float(np.mean([item["jump"] for item in values])) if values else None,
                    "forward_rate": float(np.mean([item["forward"] for item in values])) if values else None,
                }
            rows.append(
                {
                    "policy": policy_name,
                    "opponent": opponent_name,
                    "seeds": f"{SHORT_SEEDS[0]}..{SHORT_SEEDS[-1]}",
                    "low_contact_events": dict(sorted(event_counts.items())),
                    "offset_summary": offset_summary,
                    "action_counts": dict(action_counts.most_common(20)),
                }
            )
            print(
                f"diagnose {policy_name:22s} vs {opponent_name:11s} "
                f"events={dict(event_counts)} offset8={offset_summary['8']}",
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
        else APPROACH_CONFIGS[candidate].label
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
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *APPROACH_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn", "approach_drive_nojump"]
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
                f"{phase:8s} {candidate:28s} vs {opponent:11s} "
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
        default=Path("experiments/slimevolley/results/generation_5_approach_quality_probe.json"),
    )
    args = parser.parse_args()
    phase_result = (
        trace_diagnostics()
        if args.phase == "diagnose"
        else run_screen(args.phase, args.candidate, trace_window=args.trace_window)
    )
    payload = {
        "protocol": "generation-5 development-only pre-contact approach diagnostic/probe",
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
