"""Final holdout evaluator for the SlimeVolley experiment.

This module is intentionally separate from development evaluation and scalar
search. It refuses to run when holdout rows already exist unless explicitly
overridden, so the reserved seed split remains auditable.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_results_dir, env_ledger_path, env_summary_path
from hl_benchmark.ledger import read_entries
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID
from hl_benchmark.slimevolley.evaluate import EnvFactory, evaluate_slimevolley
from hl_benchmark.slimevolley.opponents import OPPONENT_POOL


DEFAULT_HOLDOUT_POLICIES = ("random", "initial", "tuned", "improved", "improved-tuned", "baseline-rnn")
DEFAULT_HOLDOUT_OPPONENTS = ("builtin", "random", "initial", "improved-v0", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6")
VALID_HOLDOUT_POLICIES = (
    "random",
    "initial",
    "tuned",
    "improved",
    "improved-tuned",
    "improved-v0",
    "improved-v1",
    "improved-v2",
    "improved-v3",
    "improved-v4",
    "improved-v5",
    "improved-v6",
    "attack",
    "rally-serve",
    "net-pressure",
    "temporal",
    "planner",
    "teacher-assisted",
    "baseline-rnn",
)


def holdout_entries(ledger_path: Path = env_ledger_path(SLIMEVOLLEY_ENV_ID)) -> list[dict[str, Any]]:
    """Return existing SlimeVolley holdout rows from a ledger."""

    return [
        entry for entry in read_entries(ledger_path)
        if entry.get("environment") == SLIMEVOLLEY_ENV_ID
        and entry.get("seed_range", {}).get("split") == "holdout"
    ]


def _load_best_tuned_config(best_config_path: Path) -> dict[str, Any]:
    if not best_config_path.exists():
        raise FileNotFoundError(
            f"tuned policy requested, but scalar-search artifact is missing: {best_config_path}"
        )
    payload = json.loads(best_config_path.read_text(encoding="utf-8"))
    config = payload.get("config")
    if not isinstance(config, dict):
        raise ValueError(f"scalar-search artifact {best_config_path} does not contain a config object")
    return config


def _cell_summary(entry: dict[str, Any]) -> dict[str, Any]:
    wld = entry.get("win_loss_draw", {})
    return {
        "timestamp": entry.get("timestamp"),
        "policy": entry.get("policy_version"),
        "opponent": entry.get("opponent_name"),
        "mean": entry.get("score_stats", {}).get("mean"),
        "std": entry.get("score_stats", {}).get("std"),
        "wins": wld.get("wins"),
        "losses": wld.get("losses"),
        "draws": wld.get("draws"),
        "win_rate": wld.get("win_rate"),
        "episodes": entry.get("episodes"),
        "environment_steps": entry.get("environment_steps"),
        "pass_fail": entry.get("pass_fail"),
    }


def run_slimevolley_holdout(
    *,
    policies: tuple[str, ...] = DEFAULT_HOLDOUT_POLICIES,
    opponents: tuple[str, ...] = DEFAULT_HOLDOUT_OPPONENTS,
    episodes: int | None = None,
    seed_start: int | None = None,
    ledger_path: Path | None = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    summary_path: Path | None = env_summary_path(SLIMEVOLLEY_ENV_ID),
    output_path: Path | None = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json",
    best_config_path: Path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json",
    allow_existing: bool = False,
    tests_run: list[str] | None = None,
    tests_pass_fail: str = "not_recorded",
    agent_iterations: int = 0,
    code_edits: int = 0,
    env_factory: EnvFactory | None = None,
) -> dict[str, Any]:
    """Run final fixed holdout evaluations without using the results for tuning."""

    unknown_policies = sorted(set(policies) - set(VALID_HOLDOUT_POLICIES))
    if unknown_policies:
        raise ValueError(f"unknown holdout policies: {unknown_policies}")
    unknown_opponents = sorted(set(opponents) - set(OPPONENT_POOL))
    if unknown_opponents:
        raise ValueError(f"unknown holdout opponents: {unknown_opponents}")
    if ledger_path is not None:
        existing = holdout_entries(ledger_path)
        if existing and not allow_existing:
            raise ValueError(
                f"holdout ledger already contains {len(existing)} rows; pass --allow-existing only for an audited repeat"
            )

    tuned_config: dict[str, Any] | None = None
    if "tuned" in policies:
        tuned_config = _load_best_tuned_config(best_config_path)

    entries: list[dict[str, Any]] = []
    total_matchups = len(policies) * len(opponents)
    matchup_index = 0
    for policy_name in policies:
        for opponent_name in opponents:
            matchup_index += 1
            config = tuned_config if policy_name == "tuned" else None
            entry = evaluate_slimevolley(
                policy_name=policy_name,
                opponent_name=opponent_name,
                split="holdout",
                seed_start=seed_start,
                episodes=episodes,
                config=config,
                ledger_path=ledger_path,
                summary_path=summary_path,
                tests_run=tests_run or [],
                tests_pass_fail=tests_pass_fail,
                change_summary=(
                    f"Final SlimeVolley holdout matchup {matchup_index}/{total_matchups}: "
                    f"{policy_name} vs {opponent_name}. This row must not be used for tuning."
                ),
                failure_analysis=(
                    "Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal."
                ),
                next_hypothesis=(
                    "Do not tune on holdout results. Use them only for the final conclusion and future fresh experiments."
                ),
                change_type="evaluation-harness change",
                agent_iterations=agent_iterations,
                code_edits=code_edits,
                env_factory=env_factory,
                allow_reserved_split=True,
            )
            entries.append(entry)
            mean = entry.get("score_stats", {}).get("mean")
            wld = entry.get("win_loss_draw", {})
            print(
                f"{entry.get('pass_fail', ''):4s} holdout {policy_name} vs {opponent_name} "
                f"mean={mean if mean is not None else 'n/a'} "
                f"wins={wld.get('wins', 0)} losses={wld.get('losses', 0)} draws={wld.get('draws', 0)}"
            )

    payload = {
        "environment": SLIMEVOLLEY_ENV_ID,
        "split": "holdout",
        "seed_start": seed_start,
        "episodes_per_matchup": entries[0].get("episodes") if entries else 0,
        "policies": list(policies),
        "opponents": list(opponents),
        "matchup_count": len(entries),
        "pass_fail": "pass" if all(entry.get("pass_fail") == "pass" for entry in entries) else "fail",
        "entry_timestamps": [entry.get("timestamp") for entry in entries],
        "cells": [_cell_summary(entry) for entry in entries],
        "anti_tuning_note": "Holdout rows are final evaluation evidence and must not be used for further policy tuning.",
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"holdout artifact: {output_path}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policies", nargs="+", default=list(DEFAULT_HOLDOUT_POLICIES), choices=list(VALID_HOLDOUT_POLICIES))
    parser.add_argument("--opponents", nargs="+", default=list(DEFAULT_HOLDOUT_OPPONENTS), choices=sorted(OPPONENT_POOL))
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--summary", type=Path, default=env_summary_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--output", type=Path, default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json")
    parser.add_argument("--best-config", type=Path, default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json")
    parser.add_argument("--allow-existing", action="store_true")
    parser.add_argument("--tests-run", default="")
    parser.add_argument("--tests-pass-fail", choices=("pass", "fail", "not_recorded"), default="not_recorded")
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    args = parser.parse_args()

    tests_run = [item for item in args.tests_run.split(",") if item]
    run_slimevolley_holdout(
        policies=tuple(args.policies),
        opponents=tuple(args.opponents),
        episodes=args.episodes,
        seed_start=args.seed_start,
        ledger_path=args.ledger,
        summary_path=args.summary,
        output_path=args.output,
        best_config_path=args.best_config,
        allow_existing=args.allow_existing,
        tests_run=tests_run,
        tests_pass_fail=args.tests_pass_fail,
        agent_iterations=args.agent_iterations,
        code_edits=args.code_edits,
    )


if __name__ == "__main__":
    main()
