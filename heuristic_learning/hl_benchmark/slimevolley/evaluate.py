"""Opponent-aware SlimeVolley evaluation harness."""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import numpy as np

from hl_benchmark.artifacts import env_ledger_path, env_summary_path
from hl_benchmark.envs import get_seeds
from hl_benchmark.ledger import append_entry, make_trial_entry, write_summary_csv
from hl_benchmark.policies import make_policy
from hl_benchmark.policies.base import BasePolicy
from hl_benchmark.policies.slimevolley import SlimeVolleyRandomPolicy
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID, dependency_versions, make_slimevolley_env, run_slimevolley_episode
from hl_benchmark.slimevolley.opponents import OPPONENT_POOL, make_slimevolley_opponent


EnvFactory = Callable[[], Any]
RESERVED_EVALUATION_SPLITS = {"holdout", "audit"}


def ensure_slimevolley_evaluation_split_allowed(
    split: str,
    *,
    allow_reserved_split: bool = False,
) -> None:
    """Reject accidental direct use of final/audit seed splits."""

    if split in RESERVED_EVALUATION_SPLITS and not allow_reserved_split:
        raise ValueError(
            "direct SlimeVolley evaluation may not use holdout or audit seeds; "
            "use slimevolley-final-eval for final holdout evidence or set "
            "allow_reserved_split=True only inside an audited harness"
        )


def _load_config(config_json: str | None) -> dict[str, Any] | None:
    if not config_json:
        return None
    maybe_path = Path(config_json)
    if maybe_path.exists():
        return json.loads(maybe_path.read_text(encoding="utf-8"))
    return json.loads(config_json)


def _score_stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"mean": None, "std": None, "median": None, "min": None, "max": None}
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(array.mean()),
        "std": float(array.std(ddof=0)),
        "median": float(np.median(array)),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def _make_policy(policy_name: str, *, action_space: Any | None, config: dict[str, Any] | None) -> BasePolicy:
    if policy_name == "random":
        return SlimeVolleyRandomPolicy()
    return make_policy(SLIMEVOLLEY_ENV_ID, policy_name, action_space=action_space, config=config)


def _merge_counts(target: Counter[str], values: dict[str, int]) -> None:
    for key, count in values.items():
        target[key] += int(count)


def evaluate_slimevolley(
    *,
    policy_name: str,
    opponent_name: str,
    split: str = "dev",
    seed_start: int | None = None,
    episodes: int | None = None,
    config: dict[str, Any] | None = None,
    ledger_path: Path | None = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    summary_path: Path | None = env_summary_path(SLIMEVOLLEY_ENV_ID),
    tests_run: list[str] | None = None,
    tests_pass_fail: str = "not_recorded",
    change_summary: str = "SlimeVolley evaluation run.",
    failure_analysis: str = "No failure observed.",
    next_hypothesis: str = "Compare opponent-pool performance across fixed seeds.",
    change_type: str = "structural policy improvement",
    agent_iterations: int = 0,
    code_edits: int = 0,
    max_steps: int | None = None,
    trace_window: int = 0,
    env_factory: EnvFactory | None = None,
    allow_reserved_split: bool = False,
) -> dict[str, Any]:
    """Evaluate one SlimeVolley policy against one named opponent."""

    if opponent_name not in OPPONENT_POOL:
        raise ValueError(f"unknown SlimeVolley opponent {opponent_name!r}; expected one of {sorted(OPPONENT_POOL)}")
    ensure_slimevolley_evaluation_split_allowed(
        split,
        allow_reserved_split=allow_reserved_split,
    )
    seeds = get_seeds(split, seed_start=seed_start, episodes=episodes)
    opponent_spec = OPPONENT_POOL[opponent_name]
    started = time.perf_counter()
    scores: list[float] = []
    life_differences: list[float] = []
    per_episode: list[dict[str, Any]] = []
    environment_steps = 0
    outcomes: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    opponent_action_counts: Counter[str] = Counter()
    pass_fail = "pass"
    error: str | None = None
    policy_config: dict[str, Any] = config or {}
    opponent_config: dict[str, Any] = {"opponent": opponent_spec.__dict__}

    env = None
    try:
        env = env_factory() if env_factory is not None else make_slimevolley_env(SLIMEVOLLEY_ENV_ID)
        policy = _make_policy(policy_name, action_space=getattr(env, "action_space", None), config=config)
        opponent = make_slimevolley_opponent(opponent_name)
        policy_config = policy.config()
        opponent_config = opponent.config()
        for seed in seeds:
            episode = run_slimevolley_episode(
                env=env,
                policy=policy,
                opponent=opponent,
                seed=seed,
                max_steps=max_steps,
                trace_window=trace_window,
            )
            scores.append(float(episode.score))
            environment_steps += int(episode.steps)
            outcomes[episode.outcome] += 1
            if episode.life_difference is not None:
                life_differences.append(float(episode.life_difference))
            _merge_counts(action_counts, episode.action_counts)
            _merge_counts(opponent_action_counts, episode.opponent_action_counts)
            per_episode.append(episode.to_dict())
    except Exception as exc:
        pass_fail = "fail"
        error = f"{type(exc).__name__}: {exc}"
        failure_analysis = error
    finally:
        if env is not None:
            env.close()

    wall_clock_seconds = time.perf_counter() - started
    total_finished = max(1, sum(outcomes.values()))
    life_stats = _score_stats(life_differences)
    entry = make_trial_entry(
        environment=SLIMEVOLLEY_ENV_ID,
        policy_version=policy_name,
        config={
            "policy": policy_config,
            "opponent": opponent_config,
            "max_steps": max_steps,
            "trace_window": trace_window,
            "dependency_versions": dependency_versions(),
        },
        seed_split=split,
        seeds=seeds,
        episodes=len(scores) if pass_fail == "pass" else len(seeds),
        score_stats=_score_stats(scores),
        environment_steps=environment_steps,
        wall_clock_seconds=wall_clock_seconds,
        tests_run=tests_run or [],
        tests_pass_fail=tests_pass_fail,
        pass_fail=pass_fail,
        change_summary=change_summary,
        failure_analysis=failure_analysis,
        next_hypothesis=next_hypothesis,
        change_type=change_type,
        agent_iterations=agent_iterations,
        code_edits=code_edits,
        per_episode=per_episode,
        error=error,
    )
    entry.update(
        {
            "environment_id": SLIMEVOLLEY_ENV_ID,
            "environment_key": "slimevolley",
            "opponent_name": opponent_spec.name,
            "opponent_version": opponent_spec.version,
            "opponent_kind": opponent_spec.kind,
            "win_loss_draw": {
                "wins": int(outcomes.get("win", 0)),
                "losses": int(outcomes.get("loss", 0)),
                "draws": int(outcomes.get("draw", 0)),
                "win_rate": float(outcomes.get("win", 0)) / total_finished if scores else None,
            },
            "life_difference_stats": life_stats,
            "action_frequencies": dict(sorted(action_counts.items())),
            "opponent_action_frequencies": dict(sorted(opponent_action_counts.items())),
        }
    )
    if ledger_path is not None:
        append_entry(ledger_path, entry)
        if summary_path is not None:
            write_summary_csv(ledger_path, summary_path)
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default="initial", choices=["random", "initial", "improved", "improved-tuned", "attack", "rally-serve", "post-contact", "net-pressure", "temporal", "planner", "teacher-assisted", "tuned", "baseline-rnn", "improved-v0", "improved-v1", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6"])
    parser.add_argument("--opponent", default="builtin", choices=sorted(OPPONENT_POOL))
    parser.add_argument("--split", default="dev", choices=["dev", "holdout", "audit", "smoke"])
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument("--config-json", default=None)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--summary", type=Path, default=env_summary_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--tests-run", default="")
    parser.add_argument("--tests-pass-fail", choices=("pass", "fail", "not_recorded"), default="not_recorded")
    parser.add_argument("--change-summary", default="SlimeVolley evaluation run.")
    parser.add_argument("--failure-analysis", default="No failure observed.")
    parser.add_argument("--next-hypothesis", default="Compare opponent-pool performance across fixed seeds.")
    parser.add_argument("--change-type", default="structural policy improvement")
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--trace-window", type=int, default=0)
    parser.add_argument("--no-ledger", action="store_true")
    parser.add_argument(
        "--allow-reserved-split",
        action="store_true",
        help="Allow direct holdout/audit evaluation only for explicit audited reproductions.",
    )
    args = parser.parse_args()

    tests_run = [item for item in args.tests_run.split(",") if item]
    entry = evaluate_slimevolley(
        policy_name=args.policy,
        opponent_name=args.opponent,
        split=args.split,
        seed_start=args.seed_start,
        episodes=args.episodes,
        config=_load_config(args.config_json),
        ledger_path=None if args.no_ledger else args.ledger,
        summary_path=None if args.no_ledger else args.summary,
        tests_run=tests_run,
        tests_pass_fail=args.tests_pass_fail,
        change_summary=args.change_summary,
        failure_analysis=args.failure_analysis,
        next_hypothesis=args.next_hypothesis,
        change_type=args.change_type,
        agent_iterations=args.agent_iterations,
        code_edits=args.code_edits,
        max_steps=args.max_steps,
        trace_window=args.trace_window,
        allow_reserved_split=args.allow_reserved_split,
    )
    mean = entry["score_stats"]["mean"]
    wld = entry.get("win_loss_draw", {})
    print(
        f"{entry['pass_fail']:4s} SlimeVolley-v0 {args.policy} vs {args.opponent} "
        f"mean={mean if mean is not None else 'n/a'} "
        f"wins={wld.get('wins', 0)} losses={wld.get('losses', 0)} draws={wld.get('draws', 0)} "
        f"steps={entry['environment_steps']}"
    )


if __name__ == "__main__":
    main()
