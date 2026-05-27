"""Development-only context-conditioned reset macro probes for generation 5.

This probe tests whether the fixed teacher-derived reset macro becomes less
brittle when it is gated by the previous point context. It uses generation-5
development seeds only and writes append-only JSON artifacts; it does not edit
maintained policies or ledgers.
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

ACTION_BOTH = np.asarray([1, 1, 0], dtype=np.int8)
TEACHER_110_6 = [ACTION_BOTH.copy() for _ in range(6)]
TEACHER_110_10 = [ACTION_BOTH.copy() for _ in range(10)]
TEACHER_110_14 = [ACTION_BOTH.copy() for _ in range(14)]
TEACHER_110_6_101_4 = [ACTION_BOTH.copy() for _ in range(6)] + [_with_jump(ACTION_FORWARD.copy(), True) for _ in range(4)]


@dataclass(frozen=True)
class ContextResetConfig:
    """Transparent context gate for a reset macro."""

    name: str
    label: str
    macro: list[np.ndarray]
    trigger: str


CONTEXT_CONFIGS: dict[str, ContextResetConfig] = {
    "ctx_own_low_110_10": ContextResetConfig(
        name="ctx_own_low_110_10",
        label="teacher 110x10 only after likely own-side low/rear point loss",
        macro=TEACHER_110_10,
        trigger="own_low_or_rear",
    ),
    "ctx_own_low_110_6": ContextResetConfig(
        name="ctx_own_low_110_6",
        label="teacher 110x6 only after likely own-side low/rear point loss",
        macro=TEACHER_110_6,
        trigger="own_low_or_rear",
    ),
    "ctx_own_low_110_14": ContextResetConfig(
        name="ctx_own_low_110_14",
        label="teacher 110x14 only after likely own-side low/rear point loss",
        macro=TEACHER_110_14,
        trigger="own_low_or_rear",
    ),
    "ctx_own_low_110_6_101_4": ContextResetConfig(
        name="ctx_own_low_110_6_101_4",
        label="teacher 110x6 then 101x4 after likely own-side low/rear point loss",
        macro=TEACHER_110_6_101_4,
        trigger="own_low_or_rear",
    ),
    "ctx_opponent_low_110_10": ContextResetConfig(
        name="ctx_opponent_low_110_10",
        label="teacher 110x10 only after likely opponent-side point win",
        macro=TEACHER_110_10,
        trigger="opponent_low",
    ),
    "ctx_any_low_110_10": ContextResetConfig(
        name="ctx_any_low_110_10",
        label="teacher 110x10 after any low terminal point context, not episode start",
        macro=TEACHER_110_10,
        trigger="any_low_terminal",
    ),
    "ctx_rear_wall_110_10": ContextResetConfig(
        name="ctx_rear_wall_110_10",
        label="teacher 110x10 only after likely rear-wall own-side terminal context",
        macro=TEACHER_110_10,
        trigger="rear_wall_terminal",
    ),
}


def _is_reset_state(values: np.ndarray) -> bool:
    return abs(float(values[4])) <= 0.28 and float(values[5]) >= 1.35 and abs(float(values[6])) <= 0.55


def _classify_low_frame(values: np.ndarray) -> str | None:
    ball_x = float(values[4])
    ball_y = float(values[5])
    ball_vx = float(values[6])
    ball_vy = float(values[7])
    low_or_wall = ball_y <= 0.48 or (abs(ball_x) >= 2.05 and ball_y <= 0.82)
    if not low_or_wall:
        return None
    if ball_x >= 1.70:
        return "rear_wall_terminal"
    if ball_x >= 0.10:
        return "own_low_or_rear"
    if ball_x <= -0.10:
        return "opponent_low"
    if abs(ball_vy) > 0.15 or abs(ball_vx) > 0.15:
        return "any_low_terminal"
    return None


def _context_label(history: list[np.ndarray]) -> str:
    if not history:
        return "episode_start"
    for values in reversed(history[-90:]):
        label = _classify_low_frame(values)
        if label is not None:
            return label
    lowest = min(history[-90:], key=lambda item: float(item[5]))
    if float(lowest[5]) <= 0.78 and abs(float(lowest[4])) >= 0.45:
        return _classify_low_frame(lowest) or "any_low_terminal"
    return "non_terminal_high"


def _trigger_matches(trigger: str, context: str) -> bool:
    if trigger == context:
        return True
    if trigger == "own_low_or_rear" and context == "rear_wall_terminal":
        return True
    if trigger == "any_low_terminal" and context in {"own_low_or_rear", "rear_wall_terminal", "opponent_low", "any_low_terminal"}:
        return True
    return False


class ContextResetPolicy(SlimeVolleyNetPressurePolicy):
    """Transient net-pressure wrapper with previous-point reset macro gating."""

    def __init__(self, config: ContextResetConfig) -> None:
        super().__init__()
        self._context_config = config
        self._macro = [np.asarray(action, dtype=np.int8).copy() for action in config.macro]
        self._macro_index = 0
        self._reset_cooldown = 0
        self._recent_non_reset_values: deque[np.ndarray] = deque(maxlen=90)
        self.total_macro_starts = 0
        self.total_macro_frames = 0
        self.total_reset_events = 0
        self.context_counts: Counter[str] = Counter()
        self.macro_context_counts: Counter[str] = Counter()

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._macro_index = 0
        self._reset_cooldown = 0
        self._recent_non_reset_values.clear()

    def _maybe_start_macro(self, values: np.ndarray) -> None:
        if self._reset_cooldown > 0 or not _is_reset_state(values):
            return
        context = _context_label(list(self._recent_non_reset_values))
        self.context_counts[context] += 1
        self.total_reset_events += 1
        self._reset_cooldown = len(self._macro) + 12
        if _trigger_matches(self._context_config.trigger, context):
            self._macro_index = len(self._macro)
            self.total_macro_starts += 1
            self.macro_context_counts[context] += 1

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        reset_now = _is_reset_state(values)
        self._maybe_start_macro(values)
        if self._macro_index > 0:
            action = self._macro[len(self._macro) - self._macro_index].copy()
            self._macro_index -= 1
            self._reset_cooldown -= 1
            self._steps += 1
            self.total_macro_frames += 1
            return self._record_diagnostics(
                mode=self._context_config.name,
                action=action,
                target_x=float(values[4]),
                reason=self._context_config.label,
            )
        self._reset_cooldown -= 1
        action = super().act(obs)
        if not reset_now:
            self._recent_non_reset_values.append(values.copy())
        return action

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["context_reset_probe"] = {
            "candidate": self._context_config.name,
            "label": self._context_config.label,
            "trigger": self._context_config.trigger,
            "macro": ["".join(str(int(v > 0)) for v in action[:3]) for action in self._macro],
        }
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in CONTEXT_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return ContextResetPolicy(CONTEXT_CONFIGS[candidate])


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
    label = "reference" if candidate == "net_pressure_reference" else "neural comparator" if candidate == "baseline_rnn" else CONTEXT_CONFIGS[candidate].label
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
        "reset_events": int(getattr(policy, "total_reset_events", 0)),
        "macro_starts": int(getattr(policy, "total_macro_starts", 0)),
        "macro_frames": int(getattr(policy, "total_macro_frames", 0)),
        "context_counts": dict(sorted(getattr(policy, "context_counts", {}).items())),
        "macro_context_counts": dict(sorted(getattr(policy, "macro_context_counts", {}).items())),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
    }


def run_phase(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *CONTEXT_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn", "ctx_own_low_110_10"]
    else:
        raise ValueError(f"unknown phase {phase!r}")
    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(candidate, opponent, seeds, trace_window=trace_window if opponent == "builtin" else 0)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:26s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} macro={row['macro_starts']}/{row['macro_frames']} reset={row['reset_events']}",
                flush=True,
            )
    return {"phase": phase, "seed_list": seeds, "opponents": opponents, "candidates": selected, "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["screen", "full"], default="screen")
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--trace-window", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_5_context_reset_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only context-conditioned reset macro probe",
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
