"""Development-only teacher-derived serve macro probes for generation 5.

The probe uses baseline-rnn development traces only to propose fixed,
transparent serve/reset macros. The maintained heuristic never calls the neural
policy at runtime.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
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
ACTION_BOTH_JUMP = np.asarray([1, 1, 1], dtype=np.int8)
ACTION_JUMP_ONLY = np.asarray([0, 0, 1], dtype=np.int8)


MACROS: dict[str, tuple[str, list[np.ndarray]]] = {
    "serve_110_6": ("teacher-derived reset macro: six frames of 110", [ACTION_BOTH] * 6),
    "serve_110_10": ("teacher-derived reset macro: ten frames of 110", [ACTION_BOTH] * 10),
    "serve_110_14": ("teacher-derived reset macro: fourteen frames of 110", [ACTION_BOTH] * 14),
    "serve_110_6_101_4": (
        "teacher-derived reset macro: six frames of 110 then four frames of 101",
        [ACTION_BOTH] * 6 + [_with_jump(ACTION_FORWARD.copy(), True)] * 4,
    ),
    "serve_110_3_101_5": (
        "teacher-derived reset macro: three frames of 110 then five frames of 101",
        [ACTION_BOTH] * 3 + [_with_jump(ACTION_FORWARD.copy(), True)] * 5,
    ),
    "serve_110_alt_jump": (
        "teacher-derived reset macro: repeated 110 with sparse jump-only beats",
        [ACTION_BOTH, ACTION_BOTH, ACTION_BOTH, ACTION_BOTH_JUMP, ACTION_JUMP_ONLY] * 2,
    ),
}


def _is_reset_state(values: np.ndarray) -> bool:
    return abs(float(values[4])) <= 0.28 and float(values[5]) >= 1.35 and abs(float(values[6])) <= 0.55


class TeacherServeMacroPolicy(SlimeVolleyNetPressurePolicy):
    """Transient net-pressure wrapper with a fixed serve/reset macro."""

    def __init__(self, candidate: str) -> None:
        super().__init__()
        self._candidate = candidate
        self._label, macro = MACROS[candidate]
        self._macro = [np.asarray(action, dtype=np.int8).copy() for action in macro]
        self._macro_index = 0
        self._cooldown = 0
        self.total_macro_frames = 0
        self.total_macro_starts = 0

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._macro_index = 0
        self._cooldown = 0

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        if self._cooldown <= 0 and _is_reset_state(values):
            self._macro_index = len(self._macro)
            self._cooldown = len(self._macro) + 10
            self.total_macro_starts += 1
        if self._macro_index > 0:
            action = self._macro[len(self._macro) - self._macro_index].copy()
            self._macro_index -= 1
            self._cooldown -= 1
            self._steps += 1
            self.total_macro_frames += 1
            return self._record_diagnostics(
                mode=self._candidate,
                action=action,
                target_x=float(values[4]),
                reason=self._label,
            )
        self._cooldown -= 1
        return super().act(obs)

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["teacher_serve_probe"] = {
            "candidate": self._candidate,
            "label": self._label,
            "macro": ["".join(str(int(v > 0)) for v in action[:3]) for action in self._macro],
        }
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in MACROS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return TeacherServeMacroPolicy(candidate)


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
    label = "reference" if candidate == "net_pressure_reference" else "neural comparator" if candidate == "baseline_rnn" else MACROS[candidate][0]
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
        "macro_starts": int(getattr(policy, "total_macro_starts", 0)),
        "macro_frames": int(getattr(policy, "total_macro_frames", 0)),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
    }


def run_phase(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *MACROS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn", "serve_110_10"]
    else:
        raise ValueError(f"unknown phase {phase!r}")
    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(candidate, opponent, seeds, trace_window=trace_window if opponent == "builtin" else 0)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:24s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} macro={row['macro_starts']}/{row['macro_frames']}",
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
        default=Path("experiments/slimevolley/results/generation_5_teacher_serve_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only teacher-derived serve macro probe",
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
