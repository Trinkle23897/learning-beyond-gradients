"""Development-only rollout-search probes for SlimeVolley generation 5.

This probe tests a stronger transparent heuristic class than the previous
one-branch rules: short-horizon simulator search over a small fixed action
set. It uses the cloneable SlimeVolley `Game` object during evaluation, so it
is explicitly a privileged model-based diagnostic. It is not promotion evidence
unless a later policy implements the same idea through the normal observation
interface and passes the fixed development opponent pool.

Only generation-5 development seeds are used. The script writes an append-only
JSON artifact and does not edit maintained policies or canonical ledgers.
"""

from __future__ import annotations

import argparse
import copy
import json
import time
from collections import Counter
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
from hl_benchmark.slimevolley.adapter import make_slimevolley_env, reset_slimevolley_env, step_slimevolley_env
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

ACTION_CANDIDATES: dict[str, np.ndarray] = {
    "000": ACTION_NOOP.copy(),
    "100": ACTION_FORWARD.copy(),
    "010": ACTION_BACKWARD.copy(),
    "001": ACTION_JUMP.copy(),
    "101": _with_jump(ACTION_FORWARD.copy(), True),
    "011": _with_jump(ACTION_BACKWARD.copy(), True),
    "111": np.asarray([1, 1, 1], dtype=np.int8),
}


@dataclass(frozen=True)
class RolloutSearchConfig:
    """Readable bounds for one short-horizon rollout-search candidate."""

    name: str
    label: str
    horizon: int
    macro_steps: int
    search_ball_y_max: float
    search_ball_x_min: float = -0.20
    search_ball_x_max: float = 1.70
    search_dx_max: float = 0.95
    search_low_y: float = 0.72
    decision_margin: float = 0.20
    require_near_or_low: bool = True
    terminal_only: bool = False
    terminal_override_threshold: float = 20.0


ROLLOUT_CONFIGS: dict[str, RolloutSearchConfig] = {
    "rollout_tactical_h18_m4": RolloutSearchConfig(
        name="rollout_tactical_h18_m4",
        label="model-based/privileged: 18-frame search, 4-frame macro, tactical low/near states",
        horizon=18,
        macro_steps=4,
        search_ball_y_max=1.20,
    ),
    "rollout_tactical_h30_m6": RolloutSearchConfig(
        name="rollout_tactical_h30_m6",
        label="model-based/privileged: 30-frame search, 6-frame macro, tactical low/near states",
        horizon=30,
        macro_steps=6,
        search_ball_y_max=1.35,
    ),
    "rollout_low_h24_m5": RolloutSearchConfig(
        name="rollout_low_h24_m5",
        label="model-based/privileged: 24-frame search only for lower ball states",
        horizon=24,
        macro_steps=5,
        search_ball_y_max=0.86,
        search_low_y=0.86,
    ),
    "rollout_terminal_h24_m4": RolloutSearchConfig(
        name="rollout_terminal_h24_m4",
        label="model-based/privileged: terminal-only 24-frame search for low near-contact states",
        horizon=24,
        macro_steps=4,
        search_ball_y_max=0.82,
        search_dx_max=0.55,
        search_low_y=0.82,
        decision_margin=1.0,
        terminal_only=True,
    ),
}


def _action_key(action: Any) -> str:
    return _action_key_for_policy(action)


def _copy_opponent(opponent: Any) -> Any:
    try:
        return copy.deepcopy(opponent)
    except Exception:
        return opponent


def _terminal_heuristic(game: Any) -> float:
    obs = game.agent_right.getObservation()
    values = _state(obs)
    x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy, opp_x, _opp_y, _opp_vx, _opp_vy = values

    score = 0.0
    if ball_x < 0.0:
        score += 1.4
        score += min(1.0, -ball_vx) * 0.5
        if ball_y <= 0.55 and ball_vy < 0.0:
            score += 1.3
        if opp_x > 1.25 and ball_x > -0.65:
            score += 0.4
    else:
        score -= 0.8
        score -= max(0.0, -ball_vy) * 0.35
        score -= min(1.0, abs(x - ball_x)) * 0.25
        if ball_y <= 0.55 and ball_vy < 0.0:
            score -= 1.4

    if ball_vy < -1e-6 and ball_y > 0.22:
        time_to_floor = min(0.9, (ball_y - 0.22) / abs(ball_vy))
        predicted_floor_x = ball_x + time_to_floor * ball_vx
        if predicted_floor_x < -0.05:
            score += 2.0
        elif predicted_floor_x > 0.05:
            score -= 2.0
    return float(score)


class RolloutSearchPolicy:
    """Transient search controller layered over net-pressure."""

    def __init__(self, config: RolloutSearchConfig) -> None:
        self.config = config
        self.base = SlimeVolleyNetPressurePolicy()
        self.steps = 0
        self.searches = 0
        self.overrides = 0
        self.action_scores: Counter[str] = Counter()
        self.action_choices: Counter[str] = Counter()
        self.override_events: list[dict[str, Any]] = []
        self.last_diagnostics: dict[str, Any] = {}

    def reset(self, seed: int | None = None) -> None:
        self.base.reset(seed)
        self.steps = 0
        self.searches = 0
        self.overrides = 0
        self.action_scores.clear()
        self.action_choices.clear()
        self.override_events = []
        self.last_diagnostics = {}

    def diagnostics(self) -> dict[str, Any]:
        return dict(self.last_diagnostics)

    def _should_search(self, values: np.ndarray) -> bool:
        cfg = self.config
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        if not cfg.search_ball_x_min <= ball_x <= cfg.search_ball_x_max:
            return False
        if ball_y > cfg.search_ball_y_max:
            return False
        ball_returning = ball_x > -0.10 or ball_vx > 0.02
        near = abs(x - ball_x) <= cfg.search_dx_max
        low = ball_y <= cfg.search_low_y and ball_vy < 0.08
        return ball_returning and (near or low if cfg.require_near_or_low else True)

    def _rollout_score(
        self,
        *,
        env: Any,
        candidate_action: np.ndarray,
        fallback_action: np.ndarray,
        opponent: Any,
        builtin_opponent: bool,
    ) -> float:
        game = copy.deepcopy(env.game)
        left_policy = copy.deepcopy(env.policy) if builtin_opponent else _copy_opponent(opponent)
        total = 0.0
        for step in range(self.config.horizon):
            if step < self.config.macro_steps:
                right_action = candidate_action
            else:
                right_action = fallback_action
            left_obs = game.agent_left.getObservation()
            if builtin_opponent:
                left_action = left_policy.predict(left_obs)
            else:
                left_action = left_policy.act(left_obs)
            game.agent_left.setAction(left_action)
            game.agent_right.setAction(right_action)
            reward = game.step()
            if reward != 0:
                return float(80.0 * reward - 0.05 * step)
            total += 0.02 * _terminal_heuristic(game)
        if self.config.terminal_only:
            return 0.0
        return float(total + _terminal_heuristic(game))

    def act(self, obs: Any, *, env: Any, opponent: Any, builtin_opponent: bool) -> np.ndarray:
        self.steps += 1
        values = _state(obs)
        base_action = self.base.act(obs)
        base_key = _action_key(base_action)
        self.last_diagnostics = self.base.diagnostics()
        if not self._should_search(values):
            return base_action

        scores = {
            key: self._rollout_score(
                env=env,
                candidate_action=action,
                fallback_action=base_action,
                opponent=opponent,
                builtin_opponent=builtin_opponent,
            )
            for key, action in ACTION_CANDIDATES.items()
        }
        self.searches += 1
        for key, value in scores.items():
            self.action_scores[key] += int(round(value * 1000))
        best_key, best_score = max(scores.items(), key=lambda item: item[1])
        base_score = scores.get(base_key, self._rollout_score(
            env=env,
            candidate_action=base_action,
            fallback_action=base_action,
            opponent=opponent,
            builtin_opponent=builtin_opponent,
        ))
        terminal_gate = (
            not self.config.terminal_only
            or best_score >= self.config.terminal_override_threshold
        )
        if best_key != base_key and terminal_gate and best_score >= base_score + self.config.decision_margin:
            self.overrides += 1
            self.action_choices[best_key] += 1
            chosen = ACTION_CANDIDATES[best_key].copy()
            self.override_events.append({
                "step": self.steps,
                "base_action": base_key,
                "chosen_action": best_key,
                "base_score": float(base_score),
                "best_score": float(best_score),
                "scores": {key: float(value) for key, value in scores.items()},
                "state": {
                    "agent_x": float(values[0]),
                    "agent_y": float(values[1]),
                    "agent_vx": float(values[2]),
                    "agent_vy": float(values[3]),
                    "ball_x": float(values[4]),
                    "ball_y": float(values[5]),
                    "ball_vx": float(values[6]),
                    "ball_vy": float(values[7]),
                    "opponent_x": float(values[8]),
                    "opponent_y": float(values[9]),
                    "opponent_vx": float(values[10]),
                    "opponent_vy": float(values[11]),
                    "agent_minus_ball_x": float(values[0] - values[4]),
                },
                "point_outcome": None,
            })
            self.last_diagnostics = {
                "mode": self.config.name,
                "action": best_key,
                "target_x": None,
                "reason": self.config.label,
                "rollout": {
                    "base_action": base_key,
                    "base_score": base_score,
                    "best_score": best_score,
                    "scores": scores,
                },
            }
            return chosen

        self.action_choices[base_key] += 1
        self.last_diagnostics = {
            **self.last_diagnostics,
            "rollout": {
                "candidate": self.config.name,
                "base_action": base_key,
                "best_action": best_key,
                "base_score": base_score,
                "best_score": best_score,
                "scores": scores,
                "kept_base": True,
            },
        }
        return base_action


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in ROLLOUT_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return RolloutSearchPolicy(ROLLOUT_CONFIGS[candidate])


def _policy_diagnostics(policy: Any) -> dict[str, Any]:
    diagnostics = getattr(policy, "diagnostics", None)
    if not callable(diagnostics):
        return {}
    value = diagnostics()
    return value if isinstance(value, dict) else {}


def _run_episode(
    *,
    env: Any,
    policy: Any,
    opponent: Any,
    seed: int,
    builtin_opponent: bool,
) -> dict[str, Any]:
    if hasattr(env.action_space, "seed"):
        env.action_space.seed(seed)
    policy.reset(seed)
    opponent.reset(seed + 1)
    if builtin_opponent and hasattr(getattr(env, "policy", None), "reset"):
        env.policy.reset()
    obs, info = reset_slimevolley_env(env, seed)
    opponent_obs = info.get("otherObs", obs)
    score = 0.0
    steps = 0
    done = False
    lives = None
    opponent_lives = None
    outcomes = Counter()
    action_counts: Counter[str] = Counter()
    terminal_modes: Counter[str] = Counter()
    while not done:
        if isinstance(policy, RolloutSearchPolicy):
            action = policy.act(obs, env=env, opponent=opponent, builtin_opponent=builtin_opponent)
        else:
            action = policy.act(obs)
        diagnostics = _policy_diagnostics(policy)
        if builtin_opponent:
            opponent_action = None
        else:
            opponent_action = opponent.act(opponent_obs)
        action_counts[_action_key(action)] += 1
        obs, reward, done, info = step_slimevolley_env(env, action, opponent_action)
        if reward != 0:
            point_outcome = "point_won" if reward > 0 else "point_lost"
            outcomes[point_outcome] += 1
            if isinstance(policy, RolloutSearchPolicy):
                for event in policy.override_events:
                    if event.get("point_outcome") is None:
                        event["point_outcome"] = point_outcome
                        event["point_step"] = int(steps)
                        event["frames_to_point"] = int(policy.steps - int(event.get("step", policy.steps)))
            mode = diagnostics.get("mode")
            if mode:
                terminal_modes[str(mode)] += 1
        score += float(reward)
        steps += 1
        opponent_obs = info.get("otherObs", opponent_obs)
        lives = info.get("ale.lives", lives)
        opponent_lives = info.get("ale.otherLives", opponent_lives)
    if lives is not None and opponent_lives is not None and lives != opponent_lives:
        outcome = "win" if lives > opponent_lives else "loss"
    elif score > 0:
        outcome = "win"
    elif score < 0:
        outcome = "loss"
    else:
        outcome = "draw"
    return {
        "seed": seed,
        "score": score,
        "steps": steps,
        "outcome": outcome,
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
        "points_won": int(outcomes.get("point_won", 0)),
        "points_lost": int(outcomes.get("point_lost", 0)),
        "override_events": list(getattr(policy, "override_events", [])),
    }


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int]) -> dict[str, Any]:
    env = make_slimevolley_env()
    policy = _policy_for_candidate(candidate)
    opponent = make_slimevolley_opponent(opponent_name)
    builtin_opponent = bool(getattr(opponent, "uses_env_builtin", False))
    started = time.perf_counter()
    episodes: list[dict[str, Any]] = []
    total_searches = 0
    total_overrides = 0
    action_choices_total: Counter[str] = Counter()
    action_scores_total: Counter[str] = Counter()
    override_events_total: list[dict[str, Any]] = []
    try:
        for seed in seeds:
            episodes.append(
                _run_episode(
                    env=env,
                    policy=policy,
                    opponent=opponent,
                    seed=seed,
                    builtin_opponent=builtin_opponent,
                )
            )
            total_searches += int(getattr(policy, "searches", 0))
            total_overrides += int(getattr(policy, "overrides", 0))
            action_choices_total.update(getattr(policy, "action_choices", {}))
            action_scores_total.update(getattr(policy, "action_scores", {}))
            for event in episodes[-1].get("override_events", []):
                override_events_total.append({
                    "seed": seed,
                    "opponent": opponent_name,
                    **event,
                })
    finally:
        env.close()
    scores = [float(ep["score"]) for ep in episodes]
    outcome_counts = Counter(str(ep["outcome"]) for ep in episodes)
    action_counts: Counter[str] = Counter()
    terminal_modes: Counter[str] = Counter()
    for episode in episodes:
        action_counts.update(episode["action_counts"])
        terminal_modes.update(episode["terminal_modes"])
    if candidate == "net_pressure_reference":
        label = "reference"
    elif candidate == "baseline_rnn":
        label = "neural comparator"
    else:
        label = ROLLOUT_CONFIGS[candidate].label
    return {
        "candidate": candidate,
        "label": label,
        "opponent": opponent_name,
        "seeds": f"{seeds[0]}..{seeds[-1]}",
        "episodes": len(seeds),
        "mean": float(np.mean(scores)) if scores else None,
        "std": float(np.std(scores)) if scores else None,
        "wins": int(outcome_counts.get("win", 0)),
        "losses": int(outcome_counts.get("loss", 0)),
        "draws": int(outcome_counts.get("draw", 0)),
        "steps": int(sum(int(ep["steps"]) for ep in episodes)),
        "points_won": int(sum(int(ep["points_won"]) for ep in episodes)),
        "points_lost": int(sum(int(ep["points_lost"]) for ep in episodes)),
        "searches": total_searches,
        "overrides": total_overrides,
        "action_choices": dict(sorted(action_choices_total.items())),
        "action_score_sums_x1000": dict(sorted(action_scores_total.items())),
        "override_event_count": len(override_events_total),
        "override_events_sample": override_events_total[:200],
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
        "wall_clock_seconds": time.perf_counter() - started,
        "candidate_config": asdict(ROLLOUT_CONFIGS[candidate]) if candidate in ROLLOUT_CONFIGS else None,
    }


def run_phase(
    phase: str,
    candidates: list[str] | None,
    *,
    opponents_override: list[str] | None = None,
    seed_start: int | None = None,
    episodes: int | None = None,
) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *ROLLOUT_CONFIGS]
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
            row = evaluate_candidate(candidate, opponent, seeds)
            rows.append(row)
            print(
                f"{phase:6s} {candidate:28s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']} searches={row['searches']} overrides={row['overrides']} "
                f"seconds={row['wall_clock_seconds']:.2f}",
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
    parser.add_argument("--opponent", action="append", default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_5_rollout_search_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only privileged rollout-search probe",
        "holdout_audit_used": False,
        "promotion_status": "not_promotion_evidence_until_normal_policy_interface_and_fixed_pool_validation",
        "phase_result": run_phase(
            args.phase,
            args.candidate,
            opponents_override=args.opponent,
            seed_start=args.seed_start,
            episodes=args.episodes,
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
