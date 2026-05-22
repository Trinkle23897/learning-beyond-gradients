"""Reproducible fixed-seed evaluation harness."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from .envs import benchmark_env_ids, get_seeds, make_env
from .ledger import (
    DEFAULT_LEDGER_PATH,
    DEFAULT_SUMMARY_PATH,
    append_entry,
    make_trial_entry,
    write_summary_csv,
)
from .policies import make_policy


DEFAULT_POLICIES = ["random", "initial", "improved"]


def _load_config(config_json: str | None) -> dict[str, Any] | None:
    if not config_json:
        return None
    maybe_path = Path(config_json)
    if maybe_path.exists():
        return json.loads(maybe_path.read_text(encoding="utf-8"))
    return json.loads(config_json)


def _score_stats(scores: list[float]) -> dict[str, float | None]:
    if not scores:
        return {"mean": None, "std": None, "median": None, "min": None, "max": None}
    values = np.asarray(scores, dtype=float)
    return {
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "median": float(np.median(values)),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def evaluate_policy(
    *,
    env_id: str,
    policy_name: str,
    split: str = "dev",
    seed_start: int | None = None,
    episodes: int | None = None,
    config: dict[str, Any] | None = None,
    ledger_path: Path | None = DEFAULT_LEDGER_PATH,
    summary_path: Path | None = DEFAULT_SUMMARY_PATH,
    tests_run: list[str] | None = None,
    change_summary: str = "Evaluation run.",
    failure_analysis: str = "No failure observed.",
    next_hypothesis: str = "Compare fixed-seed statistics against baselines.",
    change_type: str = "structural policy improvement",
    agent_iterations: int = 0,
    code_edits: int = 0,
) -> dict[str, Any]:
    """Evaluate one policy on one fixed seed range and optionally append a ledger entry."""

    seeds = get_seeds(split, seed_start=seed_start, episodes=episodes)
    scores: list[float] = []
    per_episode: list[dict[str, Any]] = []
    environment_steps = 0
    started = time.perf_counter()
    pass_fail = "pass"
    error: str | None = None
    policy_config: dict[str, Any] = config or {}

    try:
        env = make_env(env_id)
        try:
            policy = make_policy(env_id, policy_name, action_space=env.action_space, config=config)
            policy_config = policy.config()
            for seed in seeds:
                if hasattr(env.action_space, "seed"):
                    env.action_space.seed(seed)
                policy.reset(seed)
                obs, _info = env.reset(seed=seed)
                score = 0.0
                steps = 0
                terminated = False
                truncated = False
                while not (terminated or truncated):
                    action = policy.act(obs)
                    obs, reward, terminated, truncated, _info = env.step(action)
                    score += float(reward)
                    steps += 1
                scores.append(score)
                environment_steps += steps
                per_episode.append({"seed": seed, "score": score, "steps": steps})
        finally:
            env.close()
    except Exception as exc:
        pass_fail = "fail"
        error = f"{type(exc).__name__}: {exc}"
        failure_analysis = error

    wall_clock_seconds = time.perf_counter() - started
    entry = make_trial_entry(
        environment=env_id,
        policy_version=policy_name,
        config=policy_config,
        seed_split=split,
        seeds=seeds,
        episodes=len(scores) if pass_fail == "pass" else len(seeds),
        score_stats=_score_stats(scores),
        environment_steps=environment_steps,
        wall_clock_seconds=wall_clock_seconds,
        tests_run=tests_run or [],
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
    if ledger_path is not None:
        append_entry(ledger_path, entry)
        if summary_path is not None:
            write_summary_csv(ledger_path, summary_path)
    return entry


def evaluate_many(
    *,
    env_ids: list[str],
    policies: list[str],
    split: str,
    episodes: int | None,
    ledger_path: Path,
    summary_path: Path,
    tests_run: list[str],
    agent_iterations: int,
    code_edits: int,
) -> list[dict[str, Any]]:
    """Evaluate multiple environment/policy pairs."""

    entries: list[dict[str, Any]] = []
    for env_id in env_ids:
        for policy_name in policies:
            change_type = "logging/diagnostics change" if policy_name == "random" else "structural policy improvement"
            entry = evaluate_policy(
                env_id=env_id,
                policy_name=policy_name,
                split=split,
                episodes=episodes,
                ledger_path=ledger_path,
                summary_path=summary_path,
                tests_run=tests_run,
                change_summary=f"Evaluate {policy_name} on {env_id} using fixed {split} seeds.",
                failure_analysis="No failure observed.",
                next_hypothesis="Use aggregate statistics to identify structural policy failure modes.",
                change_type=change_type,
                agent_iterations=agent_iterations,
                code_edits=code_edits,
            )
            entries.append(entry)
            mean = entry["score_stats"]["mean"]
            print(
                f"{entry['pass_fail']:4s} {env_id:18s} {policy_name:8s} "
                f"mean={mean if mean is not None else 'n/a'} steps={entry['environment_steps']}"
            )
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="evaluate all registered environments")
    parser.add_argument("--env", dest="env_id", help="single Gymnasium environment id")
    parser.add_argument("--policy", default="initial", help="policy name for single-env mode")
    parser.add_argument("--policies", nargs="+", default=DEFAULT_POLICIES)
    parser.add_argument("--split", default="dev", choices=["dev", "holdout", "audit", "smoke"])
    parser.add_argument("--episodes", type=int, default=None, help="truncate the selected split")
    parser.add_argument("--seed-start", type=int, default=None, help="explicit seed range start")
    parser.add_argument("--config-json", default=None, help="JSON object or JSON file path")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument("--tests-run", default="", help="comma-separated test/check names")
    parser.add_argument("--change-summary", default="Evaluation run.")
    parser.add_argument("--failure-analysis", default="No failure observed.")
    parser.add_argument("--next-hypothesis", default="Compare fixed-seed statistics against baselines.")
    parser.add_argument("--change-type", default="structural policy improvement")
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    args = parser.parse_args()

    tests_run = [item for item in args.tests_run.split(",") if item]
    if args.all:
        evaluate_many(
            env_ids=benchmark_env_ids(),
            policies=args.policies,
            split=args.split,
            episodes=args.episodes,
            ledger_path=args.ledger,
            summary_path=args.summary,
            tests_run=tests_run,
            agent_iterations=args.agent_iterations,
            code_edits=args.code_edits,
        )
        return
    if not args.env_id:
        parser.error("--env is required unless --all is set")
    evaluate_policy(
        env_id=args.env_id,
        policy_name=args.policy,
        split=args.split,
        seed_start=args.seed_start,
        episodes=args.episodes,
        config=_load_config(args.config_json),
        ledger_path=args.ledger,
        summary_path=args.summary,
        tests_run=tests_run,
        change_summary=args.change_summary,
        failure_analysis=args.failure_analysis,
        next_hypothesis=args.next_hypothesis,
        change_type=args.change_type,
        agent_iterations=args.agent_iterations,
        code_edits=args.code_edits,
    )


if __name__ == "__main__":
    main()

