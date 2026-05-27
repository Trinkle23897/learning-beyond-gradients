"""Development-only post-contact gate probes for SlimeVolley generation 4.

This script is intentionally outside the maintained policy module. It evaluates
transient structural candidates on fixed development seeds only and writes a
JSON artifact for later notes/reporting.
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
    SlimeVolleyRallyServePolicy,
    _clip,
    _move_toward,
    _state,
    _with_jump,
)
from hl_benchmark.slimevolley.adapter import make_slimevolley_env, run_slimevolley_episode
from hl_benchmark.slimevolley.opponents import make_slimevolley_opponent


SHORT_SEEDS = list(range(9000, 9016))
FULL_SEEDS = list(range(9000, 9050))
SHORT_OPPONENTS = ["builtin", "improved-v4", "improved-v6"]
FULL_POOL = ["builtin", "random", "initial", "improved-v0", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6"]


def action_key(action: Any) -> str:
    values = np.asarray(action if action is not None else [0, 0, 0], dtype=int).reshape(-1)[:3]
    return "".join(str(int(value > 0)) for value in values)


class PostContactBase(SlimeVolleyRallyServePolicy):
    """Rally-serve wrapper with short ball-history contact features."""

    probe_name = "post_contact_base"
    probe_label = "structural/history probe"

    def __init__(self) -> None:
        super().__init__()
        self.total_override_frames = 0
        self._prev_values: np.ndarray | None = None
        self._history: deque[np.ndarray] = deque(maxlen=6)
        self._recent_own_contact = 999
        self._recent_opponent_contact = 999
        self._recent_upward_flip = 999
        self._consecutive_low_frames = 0
        self._episode_override_frames = 0

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._prev_values = None
        self._history.clear()
        self._recent_own_contact = 999
        self._recent_opponent_contact = 999
        self._recent_upward_flip = 999
        self._consecutive_low_frames = 0
        self._episode_override_frames = 0

    def _update_history(self, values: np.ndarray) -> None:
        if self._prev_values is None:
            self._recent_own_contact += 1
            self._recent_opponent_contact += 1
            self._recent_upward_flip += 1
        else:
            prev = self._prev_values
            own_vx_flip = prev[6] > 0.08 and values[6] < -0.08 and values[4] > -0.05
            own_vy_flip = prev[7] < -0.10 and values[7] > 0.04 and values[4] > -0.05 and values[5] < 1.05
            opponent_vx_flip = prev[6] < -0.08 and values[6] > 0.08 and values[4] < 0.85
            if own_vx_flip or own_vy_flip:
                self._recent_own_contact = 0
            else:
                self._recent_own_contact += 1
            if opponent_vx_flip:
                self._recent_opponent_contact = 0
            else:
                self._recent_opponent_contact += 1
            if own_vy_flip:
                self._recent_upward_flip = 0
            else:
                self._recent_upward_flip += 1

        if values[5] <= 0.58 and values[7] < -0.12:
            self._consecutive_low_frames += 1
        else:
            self._consecutive_low_frames = 0
        self._history.append(values.copy())
        self._prev_values = values.copy()

    def _base_action(self, obs: Any) -> tuple[np.ndarray, np.ndarray, str]:
        values = _state(obs)
        self._update_history(values)
        action = super().act(obs)
        mode = str(self._last_diagnostics.get("mode", "unknown"))
        return values, action, mode

    def _low_rescue_action(self, values: np.ndarray, *, force_jump: bool | None = None) -> np.ndarray:
        cfg = self._config
        x, _y, _vx, _vy, ball_x, _ball_y, ball_vx, _ball_vy = values[:8]
        target_x = _clip(ball_x + cfg.low_ball_rescue_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        action = _move_toward(x, target_x, cfg.x_margin)
        jump = abs(ball_x - x) <= cfg.low_ball_rescue_x_window if force_jump is None else force_jump
        return _with_jump(action, jump)

    def _post_contact_low(self) -> bool:
        return min(self._recent_own_contact, self._recent_upward_flip) <= 2 and self._consecutive_low_frames >= 2

    def _override(self, *, mode: str, action: np.ndarray, target_x: float | None, reason: str) -> np.ndarray:
        self.total_override_frames += 1
        self._episode_override_frames += 1
        return self._record_diagnostics(mode=mode, action=action, target_x=target_x, reason=reason)


class GateGroundedLowReceive(PostContactBase):
    probe_name = "pc_gate_grounded_low_receive"
    probe_label = "structural/history: two-frame contact gate for grounded_low_receive"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode = self._base_action(obs)
        if mode == "grounded_low_receive" and not self._post_contact_low():
            return self._override(
                mode="pc_gate_restore_grounded_low_jump",
                action=self._low_rescue_action(values),
                target_x=float(values[4]),
                reason="grounded_low_receive without two-frame post-contact low evidence; restore low-rescue jump gate",
            )
        return action


class GateLowReceiveAndLateGuard(PostContactBase):
    probe_name = "pc_gate_low_receive_and_late_guard"
    probe_label = "structural/history: two-frame contact gate for grounded and late low guards"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode = self._base_action(obs)
        if mode in {"grounded_low_receive", "late_low_ball_guard"} and not self._post_contact_low():
            return self._override(
                mode="pc_gate_restore_low_guard_jump",
                action=self._low_rescue_action(values),
                target_x=float(values[4]),
                reason="low guard without repeated post-contact low evidence; restore low-rescue jump gate",
            )
        return action


class FrontPostContactConversion(PostContactBase):
    probe_name = "pc_front_conversion"
    probe_label = "structural/history: near-net post-contact conversion"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode = self._base_action(obs)
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        front_post_contact = (
            mode != "rally_serve"
            and min(self._recent_own_contact, self._recent_upward_flip) <= 2
            and -0.08 <= ball_x <= 0.48
            and 0.24 <= ball_y <= 0.82
            and ball_vx < -0.04
            and ball_vy <= 0.12
            and -0.05 <= dx <= 0.70
        )
        if front_post_contact:
            return self._override(
                mode="pc_front_conversion",
                action=_with_jump(ACTION_FORWARD.copy(), True),
                target_x=float(ball_x),
                reason="recent contact-like flip near net; drive forward+jump to convert low front opportunity",
            )
        return action


class OutboundPostContactRecover(PostContactBase):
    probe_name = "pc_outbound_recover"
    probe_label = "structural/history: post-own-contact outbound low-ball recovery"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode = self._base_action(obs)
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, _ball_vy = values[:8]
        outbound_low = (
            mode in {"low_ball_rescue", "grounded_low_receive", "late_low_ball_guard", "rear_wall_low_jump", "rear_wall_press"}
            and self._recent_own_contact <= 3
            and 0.0 <= ball_x <= 0.90
            and ball_y <= 0.58
            and ball_vx < -0.25
        )
        if outbound_low:
            return self._override(
                mode="pc_outbound_recover",
                action=_move_toward(float(x), self._config.defensive_home_x, self._config.x_margin),
                target_x=self._config.defensive_home_x,
                reason="recent own contact produced outbound low ball; avoid risky second touch and recover",
            )
        return action


class ConservativePostContactGate(PostContactBase):
    probe_name = "pc_conservative_combined"
    probe_label = "structural/history: conservative low-guard gate plus narrow front conversion"

    def act(self, obs: Any) -> np.ndarray:
        values, action, mode = self._base_action(obs)
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        if mode == "grounded_low_receive" and not self._post_contact_low():
            return self._override(
                mode="pc_conservative_restore_grounded",
                action=self._low_rescue_action(values),
                target_x=float(ball_x),
                reason="conservative post-contact gate restores low-rescue jump outside repeated low-contact context",
            )
        narrow_front_contact = (
            mode in {"low_ball_rescue", "grounded_low_receive", "intercept"}
            and min(self._recent_own_contact, self._recent_upward_flip) <= 2
            and -0.04 <= ball_x <= 0.34
            and 0.32 <= ball_y <= 0.72
            and ball_vx < -0.10
            and ball_vy <= 0.04
            and 0.02 <= x - ball_x <= 0.48
        )
        if narrow_front_contact:
            return self._override(
                mode="pc_conservative_front_conversion",
                action=_with_jump(ACTION_FORWARD.copy(), True),
                target_x=float(ball_x),
                reason="narrow two-frame front-contact window; forward+jump conversion attempt",
            )
        return action


CANDIDATES: dict[str, tuple[str, Callable[[], Any]]] = {
    "rally_reference": ("reference", SlimeVolleyRallyServePolicy),
    "baseline_rnn": ("neural comparator", SlimeVolleyBuiltInRnnPolicy),
    GateGroundedLowReceive.probe_name: (GateGroundedLowReceive.probe_label, GateGroundedLowReceive),
    GateLowReceiveAndLateGuard.probe_name: (GateLowReceiveAndLateGuard.probe_label, GateLowReceiveAndLateGuard),
    FrontPostContactConversion.probe_name: (FrontPostContactConversion.probe_label, FrontPostContactConversion),
    OutboundPostContactRecover.probe_name: (OutboundPostContactRecover.probe_label, OutboundPostContactRecover),
    ConservativePostContactGate.probe_name: (ConservativePostContactGate.probe_label, ConservativePostContactGate),
}


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int], *, trace_window: int = 0) -> dict[str, Any]:
    label, factory = CANDIDATES[candidate]
    env = make_slimevolley_env()
    policy = factory()
    opponent = make_slimevolley_opponent(opponent_name)
    scores: list[float] = []
    outcomes: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    terminal_modes: Counter[str] = Counter()
    steps = 0
    point_won = 0
    point_lost = 0
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
            steps += int(episode.steps)
            action_counts.update(episode.action_counts)
            for event in episode.point_events:
                if event.get("outcome") == "point_won":
                    point_won += 1
                elif event.get("outcome") == "point_lost":
                    point_lost += 1
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
        "point_won": point_won,
        "point_lost": point_lost,
        "override_frames": int(getattr(policy, "total_override_frames", 0)),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
        "scores": scores,
    }


def run_phase(phase: str, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SHORT_OPPONENTS
        candidates = list(CANDIDATES)
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        candidates = [
            "rally_reference",
            "baseline_rnn",
            "pc_gate_grounded_low_receive",
            "pc_gate_low_receive_and_late_guard",
            "pc_front_conversion",
            "pc_outbound_recover",
            "pc_conservative_combined",
        ]
    else:
        raise ValueError(f"unknown phase {phase!r}")

    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        for opponent in opponents:
            row = evaluate_candidate(candidate, opponent, seeds, trace_window=trace_window if opponent == "builtin" else 0)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:34s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} overrides={row['override_frames']}",
                flush=True,
            )
    return {"phase": phase, "seed_list": seeds, "opponents": opponents, "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["screen", "full"], default="screen")
    parser.add_argument("--trace-window", type=int, default=24)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_4_post_contact_gate_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-4 development-only post-contact gate probe",
        "holdout_audit_used": False,
        "phase_result": run_phase(args.phase, trace_window=args.trace_window),
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
