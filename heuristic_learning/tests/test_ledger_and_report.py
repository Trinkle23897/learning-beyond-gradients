from __future__ import annotations

from pathlib import Path

import pytest

from hl_benchmark.deepdive_report import render_deepdive_report
from hl_benchmark.ledger import (
    append_entry,
    make_trial_entry,
    read_entries,
    validate_entry,
    write_summary_csv,
)
from hl_benchmark.report import render_report


def sample_entry() -> dict:
    return make_trial_entry(
        environment="CartPole-v1",
        policy_version="initial",
        config={"pole_velocity_gain": 0.35},
        seed_split="smoke",
        seeds=[0, 1],
        episodes=2,
        score_stats={"mean": 12.0, "std": 1.0, "median": 12.0, "min": 11.0, "max": 13.0},
        environment_steps=24,
        wall_clock_seconds=0.01,
        tests_run=["pytest"],
        pass_fail="pass",
        change_summary="Test ledger entry.",
        failure_analysis="No failure observed.",
        next_hypothesis="Keep schema stable.",
        change_type="logging/diagnostics change",
        agent_iterations=1,
        code_edits=1,
        per_episode=[
            {"seed": 0, "score": 11.0, "steps": 11},
            {"seed": 1, "score": 13.0, "steps": 13},
        ],
    )


def test_ledger_schema_rejects_missing_field() -> None:
    entry = sample_entry()
    del entry["failure_analysis"]
    with pytest.raises(ValueError):
        validate_entry(entry)


def test_ledger_summary_and_report_generation(tmp_path: Path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    append_entry(ledger_path, sample_entry())

    entries = read_entries(ledger_path)
    assert len(entries) == 1

    write_summary_csv(ledger_path, summary_path)
    assert "CartPole-v1" in summary_path.read_text(encoding="utf-8")

    report = render_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
    )
    assert "Heuristic Learning Benchmark Report" in report
    assert "Quantitative Results" in report
    assert "Cost Accounting" in report
    assert report_path.exists()



def _append_score(
    ledger_path: Path,
    *,
    environment: str,
    policy_version: str,
    split: str,
    mean: float,
    pass_fail: str = "pass",
    change_type: str = "structural policy improvement",
) -> None:
    seeds = [1000, 1001] if split == "holdout" else [0, 1]
    append_entry(
        ledger_path,
        make_trial_entry(
            environment=environment,
            policy_version=policy_version,
            config={},
            seed_split=split,
            seeds=seeds,
            episodes=2,
            score_stats={"mean": mean, "std": 0.0, "median": mean, "min": mean, "max": mean},
            environment_steps=20,
            wall_clock_seconds=0.01,
            tests_run=["pytest"] if pass_fail == "pass" else [],
            pass_fail=pass_fail,
            change_summary="Synthetic test row.",
            failure_analysis="Synthetic non-pass row." if pass_fail != "pass" else "No failure observed.",
            next_hypothesis="Keep report stable.",
            change_type=change_type,
            agent_iterations=1,
            code_edits=1,
            per_episode=[
                {"seed": seeds[0], "score": mean, "steps": 10},
                {"seed": seeds[1], "score": mean, "steps": 10},
            ],
        ),
    )


def test_deepdive_report_generation_does_not_append_ledger(tmp_path: Path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "agent_deepdive_report.md"
    for environment, policy_version, mean, change_type in [
        ("CartPole-v1", "initial", 500.0, "structural policy improvement"),
        ("MountainCar-v0", "improved", -107.64, "structural policy improvement"),
        ("Acrobot-v1", "tree", -87.74, "structural policy improvement"),
        ("LunarLander-v3", "tuned", 274.877, "scalar/config tuning"),
        ("BipedalWalker-v3", "improved", 294.426, "structural policy improvement"),
    ]:
        _append_score(
            ledger_path,
            environment=environment,
            policy_version=policy_version,
            split="holdout",
            mean=mean,
            change_type=change_type,
        )
    _append_score(
        ledger_path,
        environment="BipedalWalker-v3",
        policy_version="improved-v0-rejected",
        split="dev",
        mean=-138.0,
        pass_fail="partial",
        change_type="invalid/rolled back",
    )
    before = ledger_path.read_text(encoding="utf-8")

    report = render_deepdive_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=report_path,
    )

    assert ledger_path.read_text(encoding="utf-8") == before
    assert "Agent Deep-Dive Report" in report
    assert "Strict benchmark targets met: 4/5" in report
    assert "5% tolerance targets met: 5/5" in report
    assert "Deep-RL comparisons are secondary comparators" in report
    assert "BipedalWalker-v3" in report
    assert "partial: 1" in report
    assert report_path.exists()
