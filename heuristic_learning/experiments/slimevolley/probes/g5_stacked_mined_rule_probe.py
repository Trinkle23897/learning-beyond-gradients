"""Development-only stacked-frame probes for rollout-mined SlimeVolley rules.

Earlier generation-5 probes found that a simple observation-only near-net
vertical jump could improve some archived-opponent rows, but it regressed other
rows and was not promotable. This script tests whether short stacked-frame
features can make that rule selective enough to preserve prior behavior.

Only generation-5 development seeds are used. Holdout and audit seeds are never
referenced here. The script writes an append-only JSON artifact and does not
edit maintained policies or canonical ledgers.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.policies.slimevolley import (
    ACTION_BACKWARD,
    ACTION_FORWARD,
    ACTION_JUMP,
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
SCREEN_OPPONENTS = ["builtin", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6"]
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

ACTION_FORWARD_JUMP = _with_jump(ACTION_FORWARD.copy(), True)
ACTION_BACK_JUMP = _with_jump(ACTION_BACKWARD.copy(), True)


@dataclass(frozen=True)
class StackedMinedConfig:
    """Readable bounds for a stacked-frame near-net override probe."""

    name: str
    label: str
    action_key: str
    ball_x_min: float = -0.16
    ball_x_max: float = 0.04
    ball_y_min: float = 0.60
    ball_y_max: float = 0.84
    ball_vx_min: float = 0.25
    ball_vx_max: float = 0.85
    ball_vy_min: float = -0.58
    ball_vy_max: float = -0.12
    dx_min: float = 0.30
    dx_max: float = 0.52
    agent_y_max: float = 0.24
    stacked_vx_min: float = 0.002
    stacked_vx_max: float = 0.090
    stacked_vy_max: float = -0.002
    stacked_span: int = 4
    require_history_frames: int = 3
    require_base_action: str | None = None
    require_base_mode: str | None = None
    reject_far_fast: bool = True
    cooldown_frames: int = 0


STACKED_CONFIGS: dict[str, StackedMinedConfig] = {
    "stacked_near_net_tight_vertical": StackedMinedConfig(
        name="stacked_near_net_tight_vertical",
        label="structural/history: tight near-net vertical jump only when stacked frames confirm slow rightward descent",
        action_key="001",
        ball_x_min=-0.14,
        ball_x_max=0.02,
        ball_y_max=0.80,
        ball_vx_max=0.76,
        ball_vy_min=-0.52,
        ball_vy_max=-0.18,
        dx_min=0.34,
        dx_max=0.50,
        cooldown_frames=4,
    ),
    "stacked_near_net_mode_vertical": StackedMinedConfig(
        name="stacked_near_net_mode_vertical",
        label="structural/history: verticalize near-net returns only from base intercept mode",
        action_key="001",
        ball_x_min=-0.18,
        ball_x_max=0.03,
        ball_y_max=0.84,
        require_base_mode="intercept",
        cooldown_frames=4,
    ),
    "stacked_near_net_base_jump_vertical": StackedMinedConfig(
        name="stacked_near_net_base_jump_vertical",
        label="structural/history: replace base forward-jump/back-jump with vertical near-net contact",
        action_key="001",
        require_base_action="101",
        cooldown_frames=4,
    ),
    "stacked_near_net_forward_jump": StackedMinedConfig(
        name="stacked_near_net_forward_jump",
        label="structural/history: keep pressure direction on near-net slow descending returns",
        action_key="101",
        ball_x_min=-0.12,
        ball_x_max=0.04,
        ball_y_min=0.58,
        ball_y_max=0.82,
        ball_vx_max=0.76,
        ball_vy_max=-0.14,
        dx_min=0.28,
        dx_max=0.48,
    ),
    "stacked_near_net_back_jump": StackedMinedConfig(
        name="stacked_near_net_back_jump",
        label="structural/history: yield space with backward+jump on slow near-net returns",
        action_key="011",
        ball_x_min=-0.14,
        ball_x_max=0.03,
        ball_y_max=0.82,
        ball_vx_max=0.72,
        ball_vy_min=-0.52,
        dx_min=0.34,
        dx_max=0.52,
        cooldown_frames=4,
    ),
}


def _action_from_key(key: str) -> np.ndarray:
    if key == "000":
        return ACTION_NOOP.copy()
    if key == "001":
        return ACTION_JUMP.copy()
    if key == "011":
        return ACTION_BACK_JUMP.copy()
    if key == "101":
        return ACTION_FORWARD_JUMP.copy()
    raise ValueError(f"unsupported action key {key!r}")


class StackedMinedRulePolicy(SlimeVolleyNetPressurePolicy):
    """Transient stacked-frame wrapper around the current net-pressure probe."""

    def __init__(self, config: StackedMinedConfig) -> None:
        super().__init__()
        self._stacked_config = config
        self._history: deque[np.ndarray] = deque(maxlen=max(2, config.stacked_span))
        self._cooldown = 0
        self.override_count = 0
        self.override_actions: Counter[str] = Counter()

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._history.clear()
        self._cooldown = 0
        self.override_count = 0
        self.override_actions.clear()

    def _stacked_motion(self, values: np.ndarray) -> tuple[int, float, float]:
        window = [*self._history, values]
        span = max(1, len(window) - 1)
        stacked_vx = float((window[-1][4] - window[0][4]) / span)
        stacked_vy = float((window[-1][5] - window[0][5]) / span)
        return len(window), stacked_vx, stacked_vy

    def _matches(self, values: np.ndarray, stacked_frames: int, stacked_vx: float, stacked_vy: float) -> bool:
        cfg = self._stacked_config
        x, agent_y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        if stacked_frames < cfg.require_history_frames:
            return False
        if cfg.reject_far_fast and ball_x > 0.02 and dx >= 0.45 and ball_vx >= 1.20:
            return False
        return (
            cfg.ball_x_min <= ball_x <= cfg.ball_x_max
            and cfg.ball_y_min <= ball_y <= cfg.ball_y_max
            and cfg.ball_vx_min <= ball_vx <= cfg.ball_vx_max
            and cfg.ball_vy_min <= ball_vy <= cfg.ball_vy_max
            and cfg.dx_min <= dx <= cfg.dx_max
            and agent_y <= cfg.agent_y_max
            and cfg.stacked_vx_min <= stacked_vx <= cfg.stacked_vx_max
            and stacked_vy <= cfg.stacked_vy_max
        )

    def _record_override(self, *, action: np.ndarray, stacked_vx: float, stacked_vy: float) -> np.ndarray:
        cfg = self._stacked_config
        self.override_count += 1
        self.override_actions[_action_key_for_policy(action)] += 1
        return self._record_diagnostics(
            mode=cfg.name,
            action=action,
            target_x=None,
            reason=f"{cfg.label}; stacked_vx={stacked_vx:.4f}, stacked_vy={stacked_vy:.4f}",
        )

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        stacked_frames, stacked_vx, stacked_vy = self._stacked_motion(values)
        action = super().act(obs)
        base_mode = str(self._last_diagnostics.get("mode", ""))
        base_key = _action_key_for_policy(action)
        cfg = self._stacked_config

        if self._cooldown > 0:
            self._cooldown -= 1

        self._history.append(values.copy())

        if base_mode == "rally_serve":
            return action
        if self._cooldown > 0:
            return action
        if cfg.require_base_action is not None and base_key != cfg.require_base_action:
            return action
        if cfg.require_base_mode is not None and base_mode != cfg.require_base_mode:
            return action
        if not self._matches(values, stacked_frames, stacked_vx, stacked_vy):
            return action

        if cfg.cooldown_frames > 0:
            self._cooldown = cfg.cooldown_frames
        return self._record_override(
            action=_action_from_key(cfg.action_key),
            stacked_vx=stacked_vx,
            stacked_vy=stacked_vy,
        )

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["stacked_mined_rule_probe"] = asdict(self._stacked_config)
        values["privileged_source"] = (
            "Derived from generation-5 rollout-search diagnostics; runtime uses only current and stacked observations."
        )
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in STACKED_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return StackedMinedRulePolicy(STACKED_CONFIGS[candidate])


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
    total_overrides = 0
    override_actions_total: Counter[str] = Counter()
    try:
        for seed in seeds:
            episode = run_slimevolley_episode(
                env=env,
                policy=policy,
                opponent=opponent,
                seed=seed,
                trace_window=trace_window,
            )
            total_overrides += int(getattr(policy, "override_count", 0))
            override_actions_total.update(getattr(policy, "override_actions", {}))
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

    if candidate == "net_pressure_reference":
        label = "reference"
    elif candidate == "baseline_rnn":
        label = "neural comparator"
    else:
        label = STACKED_CONFIGS[candidate].label
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
        "override_count": total_overrides,
        "override_actions": dict(sorted(override_actions_total.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
        "candidate_config": asdict(STACKED_CONFIGS[candidate]) if candidate in STACKED_CONFIGS else None,
    }


def _seed_range(start: int | None, episodes: int | None, default: list[int]) -> list[int]:
    if start is None and episodes is None:
        return default
    seed_start = default[0] if start is None else start
    count = len(default) if episodes is None else episodes
    seeds = list(range(seed_start, seed_start + count))
    if not all(12000 <= seed <= 12049 for seed in seeds):
        raise ValueError(f"generation-5 probe may only use development seeds 12000..12049, got {seeds[0]}..{seeds[-1]}")
    return seeds


def run_phase(
    phase: str,
    candidates: list[str] | None,
    *,
    opponents_override: list[str] | None = None,
    seed_start: int | None = None,
    episodes: int | None = None,
    trace_window: int = 0,
) -> dict[str, Any]:
    if phase == "screen":
        seeds = _seed_range(seed_start, episodes, SHORT_SEEDS)
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *STACKED_CONFIGS]
    elif phase == "full":
        seeds = _seed_range(seed_start, episodes, FULL_SEEDS)
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn"]
    else:
        raise ValueError(f"unknown phase {phase!r}")
    if opponents_override:
        opponents = opponents_override

    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(candidate, opponent, seeds, trace_window=trace_window if opponent == "builtin" else 0)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:34s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} overrides={row['override_count']} actions={row['override_actions']}",
                flush=True,
            )
    return {"phase": phase, "seed_list": seeds, "opponents": opponents, "candidates": selected, "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["screen", "full"], default="screen")
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--opponent", action="append", default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--trace-window", type=int, default=24)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_5_stacked_mined_rule_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only stacked-frame observation-rule probe",
        "holdout_audit_used": False,
        "phase_result": run_phase(
            args.phase,
            args.candidate,
            opponents_override=args.opponent,
            seed_start=args.seed_start,
            episodes=args.episodes,
            trace_window=args.trace_window,
        ),
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
