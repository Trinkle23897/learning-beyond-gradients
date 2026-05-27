"""Development-only stacked low-receive probes for SlimeVolley generation 4.

This script is intentionally outside the maintained policy module. It tests
transient structural candidates on fixed development seeds only and writes an
append-only JSON artifact for audit notes.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any, Callable

import numpy as np

from hl_benchmark.policies.slimevolley import (
    ACTION_FORWARD,
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyPostContactPolicy,
    _state,
    _with_jump,
)
from hl_benchmark.slimevolley.adapter import make_slimevolley_env, run_slimevolley_episode
from hl_benchmark.slimevolley.opponents import make_slimevolley_opponent


SHORT_SEEDS = list(range(9000, 9016))
FULL_SEEDS = list(range(9000, 9050))
SCREEN_OPPONENTS = ["builtin", "improved-v4", "improved-v5", "improved-v6"]
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


def _action_key(action: Any) -> str:
    values = np.asarray(action if action is not None else [0, 0, 0], dtype=int).reshape(-1)[:3]
    return "".join(str(int(value > 0)) for value in values)


class StackedLowReceiveBase(SlimeVolleyPostContactPolicy):
    """Post-contact policy wrapper with explicit short-history low-receive features."""

    probe_name = "stacked_low_receive_base"
    probe_label = "structural/history reference"

    def __init__(self) -> None:
        super().__init__()
        self.total_override_frames = 0
        self._stack_history: deque[np.ndarray] = deque(maxlen=5)
        self._stack_prev_values: np.ndarray | None = None
        self._recent_own_vx_flip = 999
        self._recent_own_upward_flip = 999
        self._recent_opponent_vx_flip = 999

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._stack_history.clear()
        self._stack_prev_values = None
        self._recent_own_vx_flip = 999
        self._recent_own_upward_flip = 999
        self._recent_opponent_vx_flip = 999

    def _update_stacked_features(self, values: np.ndarray) -> tuple[float, float]:
        if self._stack_prev_values is None:
            self._recent_own_vx_flip += 1
            self._recent_own_upward_flip += 1
            self._recent_opponent_vx_flip += 1
        else:
            prev = self._stack_prev_values
            own_vx_flip = prev[6] > 0.08 and values[6] < -0.08 and values[4] > -0.10
            own_upward_flip = prev[7] < -0.10 and values[7] > 0.04 and values[4] > -0.10 and values[5] < 1.05
            opponent_vx_flip = prev[6] < -0.08 and values[6] > 0.08 and values[4] < 0.85
            self._recent_own_vx_flip = 0 if own_vx_flip else self._recent_own_vx_flip + 1
            self._recent_own_upward_flip = 0 if own_upward_flip else self._recent_own_upward_flip + 1
            self._recent_opponent_vx_flip = 0 if opponent_vx_flip else self._recent_opponent_vx_flip + 1

        window = [*self._stack_history, values]
        span = max(1, len(window) - 1)
        stacked_ball_vx = float((window[-1][4] - window[0][4]) / span)
        stacked_ball_vy = float((window[-1][5] - window[0][5]) / span)
        self._stack_history.append(values.copy())
        self._stack_prev_values = values.copy()
        return stacked_ball_vx, stacked_ball_vy

    def _has_recent_own_contact(self, window: int) -> bool:
        return min(self._recent_own_vx_flip, self._recent_own_upward_flip) <= window

    def _override(self, *, mode: str, action: np.ndarray, target_x: float, reason: str) -> np.ndarray:
        self.total_override_frames += 1
        return self._record_diagnostics(mode=mode, action=action, target_x=target_x, reason=reason)

    def _base(self, obs: Any) -> tuple[np.ndarray, np.ndarray, str, float, float]:
        values = _state(obs)
        stacked_ball_vx, stacked_ball_vy = self._update_stacked_features(values)
        action = super().act(obs)
        mode = str(self._last_diagnostics.get("mode", "unknown"))
        return values, action, mode, stacked_ball_vx, stacked_ball_vy


class TightFront101(StackedLowReceiveBase):
    probe_name = "stacked_front_101_tight"
    probe_label = "structural/history: tight post-contact front 101 conversion"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode, stacked_vx, _stacked_vy = self._base(obs)
        if mode == "rally_serve":
            return action
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        should_convert = (
            self._has_recent_own_contact(3)
            and -0.08 <= ball_x <= 0.50
            and 0.20 <= ball_y <= 0.75
            and min(ball_vx, stacked_vx) < -0.02
            and ball_vy <= 0.16
            and -0.05 <= dx <= 0.75
        )
        if should_convert:
            return self._override(
                mode="stacked_front_101_tight",
                action=_with_jump(ACTION_FORWARD.copy(), True),
                target_x=float(ball_x),
                reason="recent own-contact flip plus low front geometry; forward+jump conversion",
            )
        return action


class WideLow101(StackedLowReceiveBase):
    probe_name = "stacked_low_101_wide"
    probe_label = "structural/history: wider low own-side 101 conversion"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode, stacked_vx, _stacked_vy = self._base(obs)
        if mode == "rally_serve":
            return action
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        should_convert = (
            self._has_recent_own_contact(4)
            and 0.00 <= ball_x <= 0.85
            and 0.16 <= ball_y <= 0.62
            and min(ball_vx, stacked_vx) < 0.02
            and ball_vy <= 0.18
            and -0.08 <= dx <= 0.85
        )
        if should_convert:
            return self._override(
                mode="stacked_low_101_wide",
                action=_with_jump(ACTION_FORWARD.copy(), True),
                target_x=float(ball_x),
                reason="recent own-contact flip in low own-side receive; wider forward+jump conversion",
            )
        return action


class TightFrontBothJump(StackedLowReceiveBase):
    probe_name = "stacked_front_111_tight"
    probe_label = "structural/history: tight post-contact both-directions+jump conversion"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode, stacked_vx, _stacked_vy = self._base(obs)
        if mode == "rally_serve":
            return action
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        should_brace_jump = (
            self._has_recent_own_contact(3)
            and -0.08 <= ball_x <= 0.50
            and 0.20 <= ball_y <= 0.75
            and min(ball_vx, stacked_vx) < -0.02
            and ball_vy <= 0.16
            and -0.05 <= dx <= 0.75
        )
        if should_brace_jump:
            return self._override(
                mode="stacked_front_111_tight",
                action=ACTION_BOTH_JUMP.copy(),
                target_x=float(ball_x),
                reason="same gate as front 101, but tests the RNN-observed both-direction jump action",
            )
        return action


class TightFrontBothNoJump(StackedLowReceiveBase):
    probe_name = "stacked_front_110_tight"
    probe_label = "structural/history: tight post-contact both-directions brace"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode, stacked_vx, _stacked_vy = self._base(obs)
        if mode == "rally_serve":
            return action
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        should_brace = (
            self._has_recent_own_contact(3)
            and -0.08 <= ball_x <= 0.50
            and 0.20 <= ball_y <= 0.75
            and min(ball_vx, stacked_vx) < -0.02
            and ball_vy <= 0.16
            and -0.05 <= dx <= 0.75
        )
        if should_brace:
            return self._override(
                mode="stacked_front_110_tight",
                action=ACTION_BOTH.copy(),
                target_x=float(ball_x),
                reason="same gate as front 101, but tests the RNN-observed both-direction brace action",
            )
        return action


class ModeRewrite101(StackedLowReceiveBase):
    probe_name = "stacked_mode_rewrite_101"
    probe_label = "structural/history: rewrite existing low-receive modes to 101"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode, stacked_vx, _stacked_vy = self._base(obs)
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        should_rewrite = (
            mode in {"grounded_low_receive", "low_ball_rescue", "late_low_ball_guard"}
            and self._has_recent_own_contact(3)
            and 0.00 <= ball_x <= 0.68
            and 0.18 <= ball_y <= 0.64
            and min(ball_vx, stacked_vx) < 0.04
            and ball_vy <= 0.20
            and -0.08 <= dx <= 0.82
        )
        if should_rewrite:
            return self._override(
                mode="stacked_mode_rewrite_101",
                action=_with_jump(ACTION_FORWARD.copy(), True),
                target_x=float(ball_x),
                reason="existing low-receive branch plus recent contact history; convert with 101",
            )
        return action


class SplitFrontRear(StackedLowReceiveBase):
    probe_name = "stacked_split_front_rear"
    probe_label = "structural/history: front conversion, rear no-jump brace"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode, stacked_vx, _stacked_vy = self._base(obs)
        if mode == "rally_serve":
            return action
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        if (
            self._has_recent_own_contact(3)
            and -0.08 <= ball_x <= 0.42
            and 0.20 <= ball_y <= 0.72
            and min(ball_vx, stacked_vx) < -0.02
            and ball_vy <= 0.14
            and -0.05 <= dx <= 0.62
        ):
            return self._override(
                mode="stacked_split_front_101",
                action=_with_jump(ACTION_FORWARD.copy(), True),
                target_x=float(ball_x),
                reason="front half low contact; convert with 101",
            )
        if (
            mode in {"rear_wall_low_jump", "rear_wall_press", "low_ball_rescue"}
            and self._has_recent_own_contact(4)
            and ball_x >= 1.35
            and ball_y <= 0.62
            and ball_vx < -0.04
        ):
            return self._override(
                mode="stacked_split_rear_110",
                action=ACTION_BOTH.copy(),
                target_x=float(ball_x),
                reason="rear low post-contact state; brace instead of adding another jump",
            )
        return action


CANDIDATES: dict[str, tuple[str, Callable[[], Any]]] = {
    "post_contact_reference": ("reference", SlimeVolleyPostContactPolicy),
    "baseline_rnn": ("neural comparator", SlimeVolleyBuiltInRnnPolicy),
    TightFront101.probe_name: (TightFront101.probe_label, TightFront101),
    WideLow101.probe_name: (WideLow101.probe_label, WideLow101),
    TightFrontBothJump.probe_name: (TightFrontBothJump.probe_label, TightFrontBothJump),
    TightFrontBothNoJump.probe_name: (TightFrontBothNoJump.probe_label, TightFrontBothNoJump),
    ModeRewrite101.probe_name: (ModeRewrite101.probe_label, ModeRewrite101),
    SplitFrontRear.probe_name: (SplitFrontRear.probe_label, SplitFrontRear),
}


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int], *, trace_window: int) -> dict[str, Any]:
    label, factory = CANDIDATES[candidate]
    env = make_slimevolley_env()
    policy = factory()
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
        selected = candidates or list(CANDIDATES)
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["post_contact_reference", "baseline_rnn", "stacked_front_101_tight"]
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
    parser.add_argument("--trace-window", type=int, default=24)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_4_stacked_low_receive_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-4 development-only stacked low-receive probe",
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
