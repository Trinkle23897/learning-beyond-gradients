"""Scalar/config search baseline for SlimeVolley.

This module intentionally tunes only numeric `SlimeVolleyConfig` fields and uses
only development-compatible seed splits. It evaluates candidates through the
opponent-aware SlimeVolley harness so gains cannot be confused with structural
policy edits.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_results_dir, env_ledger_path, env_summary_path
from hl_benchmark.search import candidate_configs, ensure_search_split_allowed
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID
from hl_benchmark.slimevolley.evaluate import EnvFactory, evaluate_slimevolley
from hl_benchmark.slimevolley.opponents import OPPONENT_POOL


DEFAULT_SEARCH_OPPONENTS = ("builtin", "random", "initial", "improved-v0", "improved-v3", "improved-v4", "improved-v5", "improved-v6")


def _entry_selection_score(entry: dict[str, Any], std_penalty: float) -> float | None:
    if entry.get("pass_fail") != "pass":
        return None
    mean = entry.get("score_stats", {}).get("mean")
    if mean is None:
        return None
    std = entry.get("score_stats", {}).get("std") or 0.0
    return float(mean) - std_penalty * float(std)


def _aggregate_score(entries: list[dict[str, Any]], std_penalty: float) -> float | None:
    scores = [_entry_selection_score(entry, std_penalty) for entry in entries]
    valid_scores = [score for score in scores if score is not None]
    if len(valid_scores) != len(entries):
        return None
    return sum(valid_scores) / len(valid_scores)


def search_slimevolley_configs(
    *,
    split: str = "dev",
    opponents: tuple[str, ...] = DEFAULT_SEARCH_OPPONENTS,
    max_candidates: int = 8,
    episodes: int | None = None,
    seed_start: int | None = None,
    std_penalty: float = 0.0,
    ledger_path: Path | None = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    summary_path: Path | None = env_summary_path(SLIMEVOLLEY_ENV_ID),
    output_path: Path | None = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json",
    tests_run: list[str] | None = None,
    tests_pass_fail: str = "not_recorded",
    agent_iterations: int = 0,
    code_edits: int = 0,
    env_factory: EnvFactory | None = None,
) -> dict[str, Any] | None:
    """Run bounded scalar search over SlimeVolley heuristic config values."""

    ensure_search_split_allowed(split)
    unknown = sorted(set(opponents) - set(OPPONENT_POOL))
    if unknown:
        raise ValueError(f"unknown SlimeVolley opponents for search: {unknown}")

    candidates = candidate_configs(SLIMEVOLLEY_ENV_ID, max_candidates=max_candidates)
    best: dict[str, Any] | None = None
    best_score: float | None = None
    for index, config in enumerate(candidates, start=1):
        entries: list[dict[str, Any]] = []
        for opponent_name in opponents:
            entry = evaluate_slimevolley(
                policy_name="tuned",
                opponent_name=opponent_name,
                split=split,
                seed_start=seed_start,
                episodes=episodes,
                config=config,
                ledger_path=ledger_path,
                summary_path=summary_path,
                tests_run=tests_run or [],
                tests_pass_fail=tests_pass_fail,
                change_summary=(
                    f"SlimeVolley scalar search candidate {index}/{len(candidates)} "
                    f"against {opponent_name}; no structural policy code changed."
                ),
                failure_analysis="No failure observed.",
                next_hypothesis=(
                    "Select scalar config on development seeds using average opponent score "
                    f"with mean - {std_penalty:g} * std per opponent."
                ),
                change_type="scalar/config tuning",
                agent_iterations=agent_iterations,
                code_edits=code_edits,
                env_factory=env_factory,
            )
            entries.append(entry)
        aggregate = _aggregate_score(entries, std_penalty)
        if aggregate is not None and (best_score is None or aggregate > best_score):
            best_score = aggregate
            best = {
                "environment": SLIMEVOLLEY_ENV_ID,
                "split": split,
                "opponents": list(opponents),
                "candidate_index": index,
                "candidate_count": len(candidates),
                "selection_score": aggregate,
                "std_penalty": std_penalty,
                "config": config,
                "entry_timestamps": [entry.get("timestamp") for entry in entries],
                "opponent_means": {
                    entry.get("opponent_name", "unknown"): entry.get("score_stats", {}).get("mean")
                    for entry in entries
                },
            }
        print(
            f"candidate={index:02d}/{len(candidates):02d} aggregate="
            f"{aggregate if aggregate is not None else 'n/a'} config={config}"
        )

    if best is not None and output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(best, indent=2, sort_keys=True), encoding="utf-8")
        print(f"best SlimeVolley scalar config: score={best['selection_score']:.6g} output={output_path}")
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="dev", choices=["dev", "smoke", "holdout", "audit"])
    parser.add_argument("--opponents", nargs="+", default=list(DEFAULT_SEARCH_OPPONENTS), choices=sorted(OPPONENT_POOL))
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument("--std-penalty", type=float, default=0.0)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--summary", type=Path, default=env_summary_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--output", type=Path, default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json")
    parser.add_argument("--tests-run", default="")
    parser.add_argument("--tests-pass-fail", choices=("pass", "fail", "not_recorded"), default="not_recorded")
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    args = parser.parse_args()

    tests_run = [item for item in args.tests_run.split(",") if item]
    search_slimevolley_configs(
        split=args.split,
        opponents=tuple(args.opponents),
        max_candidates=args.max_candidates,
        episodes=args.episodes,
        seed_start=args.seed_start,
        std_penalty=args.std_penalty,
        ledger_path=args.ledger,
        summary_path=args.summary,
        output_path=args.output,
        tests_run=tests_run,
        tests_pass_fail=args.tests_pass_fail,
        agent_iterations=args.agent_iterations,
        code_edits=args.code_edits,
    )


if __name__ == "__main__":
    main()
