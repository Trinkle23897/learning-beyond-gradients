"""Development-only observation-rule probes mined from rollout-search overrides.

The privileged rollout-search probe found a few terminal-only overrides that
improved generation-5 development subset rows, but simulator access is not a
valid maintained policy interface. This script tests small observation-only
rules that approximate the successful override states and explicitly reject the
bad far-behind vertical-jump pattern seen in `improved-v4`.

Only generation-5 development seeds are used. The script writes an append-only
JSON artifact and does not edit maintained policies or canonical ledgers.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.policies.slimevolley import (
    ACTION_BACKWARD,
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
ACTION_BACK_JUMP = _with_jump(ACTION_BACKWARD.copy(), True)


@dataclass(frozen=True)
class MinedRuleConfig:
    name: str
    label: str
    use_low_fast_noop: bool = False
    use_low_fast_vertical: bool = False
    use_near_net_vertical: bool = False
    use_near_net_back_jump: bool = False


MINED_CONFIGS: dict[str, MinedRuleConfig] = {
    "mined_low_fast_noop": MinedRuleConfig(
        name="mined_low_fast_noop",
        label="observation-only: suppress movement on low fast-descending near-front contact states",
        use_low_fast_noop=True,
    ),
    "mined_low_fast_vertical": MinedRuleConfig(
        name="mined_low_fast_vertical",
        label="observation-only: vertical jump on low fast-descending near-front contact states",
        use_low_fast_vertical=True,
    ),
    "mined_near_net_vertical": MinedRuleConfig(
        name="mined_near_net_vertical",
        label="observation-only: verticalize slow near-net return states mined from rollout search",
        use_near_net_vertical=True,
    ),
    "mined_near_net_back_jump": MinedRuleConfig(
        name="mined_near_net_back_jump",
        label="observation-only: backward+jump on slow near-net return states mined from rollout search",
        use_near_net_back_jump=True,
    ),
    "mined_combo_conservative": MinedRuleConfig(
        name="mined_combo_conservative",
        label="observation-only: low-fast noop plus strict near-net vertical rule",
        use_low_fast_noop=True,
        use_near_net_vertical=True,
    ),
}


def _action_key(action: Any) -> str:
    return _action_key_for_policy(action)


class RolloutMinedRulePolicy(SlimeVolleyNetPressurePolicy):
    """Transient observation-only approximation of useful rollout overrides."""

    def __init__(self, config: MinedRuleConfig) -> None:
        super().__init__()
        self._mined_config = config
        self.override_count = 0
        self.override_actions: Counter[str] = Counter()

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self.override_count = 0
        self.override_actions.clear()

    def _low_fast_contact(self, values: np.ndarray) -> bool:
        x, agent_y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        return (
            0.20 <= ball_x <= 0.62
            and 0.40 <= ball_y <= 0.64
            and 0.55 <= ball_vx <= 1.35
            and ball_vy <= -1.00
            and 0.10 <= dx <= 0.36
            and agent_y <= 0.36
        )

    def _near_net_return(self, values: np.ndarray) -> bool:
        x, agent_y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        # Exclude the repeated bad pattern: far behind a fast-rightward ball.
        bad_far_fast_vertical = ball_x > 0.02 and dx >= 0.45 and ball_vx >= 1.25
        return (
            -0.18 <= ball_x <= 0.05
            and 0.60 <= ball_y <= 0.86
            and 0.25 <= ball_vx <= 0.85
            and -0.55 <= ball_vy <= -0.15
            and 0.28 <= dx <= 0.52
            and agent_y <= 0.22
            and not bad_far_fast_vertical
        )

    def _record_override(self, *, mode: str, action: np.ndarray, reason: str) -> np.ndarray:
        self.override_count += 1
        self.override_actions[_action_key(action)] += 1
        return self._record_diagnostics(mode=mode, action=action, target_x=None, reason=reason)

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        action = super().act(obs)
        if self._last_diagnostics.get("mode") == "rally_serve":
            return action
        cfg = self._mined_config
        if self._low_fast_contact(values):
            if cfg.use_low_fast_noop:
                return self._record_override(
                    mode=cfg.name,
                    action=ACTION_NOOP.copy(),
                    reason="rollout-mined low fast contact: suppress lateral movement",
                )
            if cfg.use_low_fast_vertical:
                return self._record_override(
                    mode=cfg.name,
                    action=ACTION_JUMP.copy(),
                    reason="rollout-mined low fast contact: vertical jump",
                )
        if self._near_net_return(values):
            if cfg.use_near_net_vertical:
                return self._record_override(
                    mode=cfg.name,
                    action=ACTION_JUMP.copy(),
                    reason="rollout-mined near-net return: vertical jump",
                )
            if cfg.use_near_net_back_jump:
                return self._record_override(
                    mode=cfg.name,
                    action=ACTION_BACK_JUMP.copy(),
                    reason="rollout-mined near-net return: backward jump",
                )
        return action

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["rollout_mined_rule_probe"] = asdict(self._mined_config)
        values["privileged_source"] = "Derived from generation-5 rollout-search override diagnostics; runtime is observation-only."
        return values


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in MINED_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return RolloutMinedRulePolicy(MINED_CONFIGS[candidate])


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
        label = MINED_CONFIGS[candidate].label
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
        "candidate_config": asdict(MINED_CONFIGS[candidate]) if candidate in MINED_CONFIGS else None,
    }


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
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *MINED_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn"]
    else:
        raise ValueError(f"unknown phase {phase!r}")
    if seed_start is not None or episodes is not None:
        start = seed_start if seed_start is not None else seeds[0]
        count = episodes if episodes is not None else len(seeds)
        seeds = list(range(start, start + count))
    if opponents_override:
        opponents = opponents_override

    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(candidate, opponent, seeds, trace_window=trace_window if opponent == "builtin" else 0)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:28s} vs {opponent:11s} "
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
        default=Path("experiments/slimevolley/results/generation_5_rollout_mined_rule_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only observation-rule probe mined from rollout-search diagnostics",
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
