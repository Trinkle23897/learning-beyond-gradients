"""Round-robin tournament runner for SlimeVolley policy versions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_results_dir, env_ledger_path, env_summary_path
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID
from hl_benchmark.slimevolley.evaluate import (
    EnvFactory,
    evaluate_slimevolley,
    ensure_slimevolley_evaluation_split_allowed,
)


DEFAULT_TOURNAMENT_PARTICIPANTS = ("random", "initial", "improved-v0", "improved-v1", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6", "improved", "improved-tuned", "attack")
VALID_TOURNAMENT_PARTICIPANTS = (*DEFAULT_TOURNAMENT_PARTICIPANTS, "temporal", "planner", "teacher-assisted", "baseline-rnn")


def _score_mean(entry: dict[str, Any]) -> float | None:
    value = entry.get("score_stats", {}).get("mean")
    return None if value is None else float(value)


def _cell_summary(entry: dict[str, Any]) -> dict[str, Any]:
    wld = entry.get("win_loss_draw", {})
    return {
        "policy": entry.get("policy_version"),
        "opponent": entry.get("opponent_name"),
        "split": entry.get("seed_range", {}).get("split"),
        "episodes": entry.get("episodes"),
        "mean": _score_mean(entry),
        "std": entry.get("score_stats", {}).get("std"),
        "wins": wld.get("wins"),
        "losses": wld.get("losses"),
        "draws": wld.get("draws"),
        "win_rate": wld.get("win_rate"),
        "environment_steps": entry.get("environment_steps"),
        "pass_fail": entry.get("pass_fail"),
        "timestamp": entry.get("timestamp"),
    }


def _standings(participants: tuple[str, ...], entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for participant in participants:
        participant_entries = [entry for entry in entries if entry.get("policy_version") == participant]
        pass_entries = [entry for entry in participant_entries if entry.get("pass_fail") == "pass"]
        means = [_score_mean(entry) for entry in pass_entries]
        valid_means = [value for value in means if value is not None]
        wins = sum(int(entry.get("win_loss_draw", {}).get("wins") or 0) for entry in pass_entries)
        losses = sum(int(entry.get("win_loss_draw", {}).get("losses") or 0) for entry in pass_entries)
        draws = sum(int(entry.get("win_loss_draw", {}).get("draws") or 0) for entry in pass_entries)
        total_finished = wins + losses + draws
        rows.append(
            {
                "policy": participant,
                "cells": len(participant_entries),
                "passing_cells": len(pass_entries),
                "mean_score_across_opponents": (
                    sum(valid_means) / len(valid_means) if valid_means else None
                ),
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "win_rate": wins / total_finished if total_finished else None,
                "environment_steps": sum(int(entry.get("environment_steps") or 0) for entry in pass_entries),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            row["mean_score_across_opponents"] is not None,
            row["mean_score_across_opponents"] if row["mean_score_across_opponents"] is not None else float("-inf"),
            row["win_rate"] if row["win_rate"] is not None else float("-inf"),
        ),
        reverse=True,
    )


def run_slimevolley_tournament(
    *,
    split: str = "dev",
    participants: tuple[str, ...] = DEFAULT_TOURNAMENT_PARTICIPANTS,
    episodes: int | None = None,
    seed_start: int | None = None,
    ledger_path: Path | None = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    summary_path: Path | None = env_summary_path(SLIMEVOLLEY_ENV_ID),
    output_path: Path | None = None,
    tests_run: list[str] | None = None,
    tests_pass_fail: str = "not_recorded",
    agent_iterations: int = 0,
    code_edits: int = 0,
    max_steps: int | None = None,
    env_factory: EnvFactory | None = None,
) -> dict[str, Any]:
    """Run a fixed-seed round-robin tournament across SlimeVolley policy versions."""

    unknown = sorted(set(participants) - set(VALID_TOURNAMENT_PARTICIPANTS))
    if unknown:
        raise ValueError(
            f"unknown SlimeVolley tournament participants: {unknown}; "
            f"expected subset of {sorted(VALID_TOURNAMENT_PARTICIPANTS)}"
        )
    if not participants:
        raise ValueError("at least one tournament participant is required")
    ensure_slimevolley_evaluation_split_allowed(split)
    if output_path is None:
        output_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / f"round_robin_{split}.json"

    entries: list[dict[str, Any]] = []
    total_matchups = len(participants) * len(participants)
    matchup_index = 0
    for policy_name in participants:
        for opponent_name in participants:
            matchup_index += 1
            entry = evaluate_slimevolley(
                policy_name=policy_name,
                opponent_name=opponent_name,
                split=split,
                seed_start=seed_start,
                episodes=episodes,
                ledger_path=ledger_path,
                summary_path=summary_path,
                tests_run=tests_run or [],
                tests_pass_fail=tests_pass_fail,
                change_summary=(
                    f"SlimeVolley round-robin tournament matchup {matchup_index}/{total_matchups}: "
                    f"{policy_name} vs {opponent_name}; no policy code changed."
                ),
                failure_analysis="No failure observed.",
                next_hypothesis=(
                    "Use round-robin standings to detect exploitability and regressions across archived policy versions."
                ),
                change_type="evaluation-harness change",
                agent_iterations=agent_iterations,
                code_edits=code_edits,
                max_steps=max_steps,
                env_factory=env_factory,
            )
            entries.append(entry)
            mean = entry.get("score_stats", {}).get("mean")
            wld = entry.get("win_loss_draw", {})
            print(
                f"{entry.get('pass_fail', ''):4s} {policy_name} vs {opponent_name} "
                f"mean={mean if mean is not None else 'n/a'} "
                f"wins={wld.get('wins', 0)} losses={wld.get('losses', 0)} draws={wld.get('draws', 0)}"
            )

    payload = {
        "environment": SLIMEVOLLEY_ENV_ID,
        "split": split,
        "participants": list(participants),
        "episodes_per_matchup": entries[0].get("episodes") if entries else 0,
        "matchup_count": len(entries),
        "pass_fail": "pass" if all(entry.get("pass_fail") == "pass" for entry in entries) else "fail",
        "entry_timestamps": [entry.get("timestamp") for entry in entries],
        "standings": _standings(participants, entries),
        "cells": [_cell_summary(entry) for entry in entries],
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"round-robin tournament artifact: {output_path}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="dev", choices=["dev", "smoke", "holdout", "audit"])
    parser.add_argument("--participants", nargs="+", default=list(DEFAULT_TOURNAMENT_PARTICIPANTS), choices=list(VALID_TOURNAMENT_PARTICIPANTS))
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--summary", type=Path, default=env_summary_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--tests-run", default="")
    parser.add_argument("--tests-pass-fail", choices=("pass", "fail", "not_recorded"), default="not_recorded")
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=None)
    args = parser.parse_args()

    tests_run = [item for item in args.tests_run.split(",") if item]
    run_slimevolley_tournament(
        split=args.split,
        participants=tuple(args.participants),
        episodes=args.episodes,
        seed_start=args.seed_start,
        ledger_path=args.ledger,
        summary_path=args.summary,
        output_path=args.output,
        tests_run=tests_run,
        tests_pass_fail=args.tests_pass_fail,
        agent_iterations=args.agent_iterations,
        code_edits=args.code_edits,
        max_steps=args.max_steps,
    )


if __name__ == "__main__":
    main()
