from __future__ import annotations

from pathlib import Path
import sys

import pytest

import hl_benchmark.artifact_audit as artifact_audit_module
import hl_benchmark.evaluate as evaluate_module
import hl_benchmark.report as report_module
import hl_benchmark.summarize as summarize_module
from hl_benchmark.artifact_audit import audit_environment_artifacts, render_audit_text
from hl_benchmark.artifacts import env_ledger_path, env_report_path, env_summary_path
from hl_benchmark.deepdive_report import render_deepdive_report
from hl_benchmark.ledger import (
    append_entry,
    make_trial_entry,
    read_entries,
    validate_entry,
    write_summary_csv,
)
from hl_benchmark.evaluate import resolve_evaluation_paths
from hl_benchmark.report import render_report, resolve_report_paths
from hl_benchmark.summarize import resolve_summary_paths


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
    summary_text = summary_path.read_text(encoding="utf-8")
    assert "CartPole-v1" in summary_text
    assert "tests_pass_fail" in summary_text.splitlines()[0]
    assert "not_recorded" in summary_text

    report = render_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
    )
    assert "Heuristic Learning Benchmark Report" in report
    assert "Quantitative Results" in report
    assert "Cost Accounting" in report
    assert report_path.exists()


def test_resolve_evaluation_paths_can_use_per_environment_artifacts(tmp_path: Path) -> None:
    legacy_ledger = tmp_path / "legacy" / "trials.jsonl"
    legacy_summary = tmp_path / "legacy" / "summary.csv"
    ledger_path, summary_path = resolve_evaluation_paths(
        env_id="CartPole-v1",
        ledger_path=legacy_ledger,
        summary_path=legacy_summary,
        env_artifacts=False,
    )
    assert ledger_path == legacy_ledger
    assert summary_path == legacy_summary

    ledger_path, summary_path = resolve_evaluation_paths(
        env_id="CartPole-v1",
        ledger_path=None,
        summary_path=None,
        env_artifacts=True,
    )
    assert ledger_path == env_ledger_path("CartPole-v1")
    assert summary_path == env_summary_path("CartPole-v1")
    assert ledger_path.as_posix().endswith("experiments/cartpole/results/trials.jsonl")
    assert summary_path.as_posix().endswith("experiments/cartpole/results/summary.csv")


def test_evaluate_cli_env_artifacts_routes_single_env_outputs(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_evaluate_policy(**kwargs):
        captured.update(kwargs)
        return {"pass_fail": "pass"}

    monkeypatch.setattr(evaluate_module, "evaluate_policy", fake_evaluate_policy)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.evaluate",
            "--env",
            "CartPole-v1",
            "--policy",
            "initial",
            "--split",
            "smoke",
            "--env-artifacts",
        ],
    )

    evaluate_module.main()

    assert captured["env_id"] == "CartPole-v1"
    assert captured["policy_name"] == "initial"
    assert captured["split"] == "smoke"
    assert captured["ledger_path"] == env_ledger_path("CartPole-v1")
    assert captured["summary_path"] == env_summary_path("CartPole-v1")



def test_resolve_summary_paths_can_use_per_environment_artifacts(tmp_path: Path) -> None:
    legacy_ledger = tmp_path / "legacy" / "trials.jsonl"
    legacy_summary = tmp_path / "legacy" / "summary.csv"
    ledger_path, summary_path = resolve_summary_paths(
        env_id=None,
        ledger_path=legacy_ledger,
        summary_path=legacy_summary,
        env_artifacts=False,
    )
    assert ledger_path == legacy_ledger
    assert summary_path == legacy_summary

    ledger_path, summary_path = resolve_summary_paths(
        env_id="CartPole-v1",
        ledger_path=None,
        summary_path=None,
        env_artifacts=True,
    )
    assert ledger_path == env_ledger_path("CartPole-v1")
    assert summary_path == env_summary_path("CartPole-v1")

    with pytest.raises(ValueError, match="--env is required"):
        resolve_summary_paths(
            env_id=None,
            ledger_path=None,
            summary_path=None,
            env_artifacts=True,
        )


def test_summarize_cli_env_artifacts_regenerates_per_env_summary(monkeypatch, capsys) -> None:
    captured: dict[str, Path] = {}

    def fake_write_summary_csv(ledger_path: Path, summary_path: Path) -> None:
        captured["ledger_path"] = ledger_path
        captured["summary_path"] = summary_path

    monkeypatch.setattr(summarize_module, "write_summary_csv", fake_write_summary_csv)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.summarize",
            "--env",
            "CartPole-v1",
            "--env-artifacts",
        ],
    )

    summarize_module.main()

    assert captured["ledger_path"] == env_ledger_path("CartPole-v1")
    assert captured["summary_path"] == env_summary_path("CartPole-v1")
    assert env_summary_path("CartPole-v1").as_posix() in capsys.readouterr().out


def test_resolve_report_paths_can_use_per_environment_artifacts(tmp_path: Path) -> None:
    legacy_ledger = tmp_path / "legacy" / "trials.jsonl"
    legacy_summary = tmp_path / "legacy" / "summary.csv"
    legacy_report = tmp_path / "legacy" / "final_report.md"
    ledger_path, summary_path, report_path = resolve_report_paths(
        env_id=None,
        ledger_path=legacy_ledger,
        summary_path=legacy_summary,
        report_path=legacy_report,
        env_artifacts=False,
    )
    assert ledger_path == legacy_ledger
    assert summary_path == legacy_summary
    assert report_path == legacy_report

    ledger_path, summary_path, report_path = resolve_report_paths(
        env_id="CartPole-v1",
        ledger_path=None,
        summary_path=None,
        report_path=None,
        env_artifacts=True,
    )
    assert ledger_path == env_ledger_path("CartPole-v1")
    assert summary_path == env_summary_path("CartPole-v1")
    assert report_path == env_report_path("CartPole-v1")

    with pytest.raises(ValueError, match="--env is required"):
        resolve_report_paths(
            env_id=None,
            ledger_path=None,
            summary_path=None,
            report_path=None,
            env_artifacts=True,
        )


def test_report_cli_env_artifacts_routes_single_env_outputs(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}

    def fake_render_report(
        *,
        ledger_path: Path,
        summary_path: Path,
        report_path: Path,
        env_id: str | None = None,
    ) -> str:
        captured["ledger_path"] = ledger_path
        captured["summary_path"] = summary_path
        captured["report_path"] = report_path
        captured["env_id"] = env_id
        return "report"

    monkeypatch.setattr(report_module, "render_report", fake_render_report)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.report",
            "--env",
            "CartPole-v1",
            "--env-artifacts",
        ],
    )

    report_module.main()

    assert captured["ledger_path"] == env_ledger_path("CartPole-v1")
    assert captured["summary_path"] == env_summary_path("CartPole-v1")
    assert captured["report_path"] == env_report_path("CartPole-v1")
    assert captured["env_id"] == "CartPole-v1"
    assert env_report_path("CartPole-v1").as_posix() in capsys.readouterr().out


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


def test_render_report_can_scope_to_single_environment(tmp_path: Path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    _append_score(
        ledger_path,
        environment="CartPole-v1",
        policy_version="initial",
        split="holdout",
        mean=475.0,
    )
    _append_score(
        ledger_path,
        environment="CartPole-v1",
        policy_version="improved",
        split="holdout",
        mean=500.0,
    )
    _append_score(
        ledger_path,
        environment="MountainCar-v0",
        policy_version="initial",
        split="holdout",
        mean=-200.0,
    )

    report = render_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        env_id="CartPole-v1",
    )

    assert "# Heuristic Learning Benchmark Report: CartPole-v1" in report
    assert "### CartPole-v1" in report
    assert "### MountainCar-v0" not in report
    assert "MountainCar" not in report
    assert "| CartPole-v1 |" in report
    assert "| MountainCar-v0 |" not in report
    assert "1/1 environments" in report
    assert report_path.exists()


def test_generic_env_artifact_audit_validates_summary_and_scoped_report(tmp_path: Path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    _append_score(
        ledger_path,
        environment="CartPole-v1",
        policy_version="initial",
        split="holdout",
        mean=475.0,
    )
    write_summary_csv(ledger_path, summary_path)
    render_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        env_id="CartPole-v1",
    )

    result = audit_environment_artifacts(
        "CartPole-v1",
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
    )

    assert result["pass_fail"] == "pass"
    assert result["ledger_rows"] == 1
    assert result["summary_rows"] == 1
    assert result["summary_content_checked"] is True
    assert result["report_content_checked"] is True
    assert all(value != "missing" for value in result["artifact_hashes"].values())
    assert "Generic environment artifact audit: pass" in render_audit_text(result)


def test_generic_env_artifact_audit_rejects_custom_environment_with_guidance(tmp_path: Path) -> None:
    result = audit_environment_artifacts(
        "SlimeVolley-v0",
        ledger_path=tmp_path / "trials.jsonl",
        summary_path=tmp_path / "summary.csv",
        report_path=tmp_path / "final_report.md",
    )

    assert result["pass_fail"] == "fail"
    issues = "\n".join(result["issues"])
    assert "got custom environment 'SlimeVolley-v0'" in issues
    assert "make custom-verify ENV=SlimeVolley-v0" in issues
    assert "environment-specific audit command" in issues


def test_generic_env_artifact_audit_reports_missing_generated_artifacts(tmp_path: Path) -> None:
    ledger_path = tmp_path / "missing" / "trials.jsonl"
    summary_path = tmp_path / "missing" / "summary.csv"
    report_path = tmp_path / "missing" / "final_report.md"

    result = audit_environment_artifacts(
        "CartPole-v1",
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
    )

    assert result["pass_fail"] == "fail"
    issues = "\n".join(result["issues"])
    assert f"missing ledger: {ledger_path}" in issues
    assert f"missing summary: {summary_path}" in issues
    assert f"missing report: {report_path}" in issues
    assert result["ledger_rows"] == 0
    assert result["summary_rows"] == 0
    assert result["summary_content_checked"] is False
    assert result["report_content_checked"] is False
    assert result["artifact_hashes"] == {
        "ledger": "missing",
        "summary": "missing",
        "report": "missing",
    }
    text = render_audit_text(result)
    assert "Generic environment artifact audit: fail" in text
    assert "Artifact hashes recorded: False" in text


def test_generic_env_artifact_audit_flags_mixed_or_stale_artifacts(tmp_path: Path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    _append_score(
        ledger_path,
        environment="CartPole-v1",
        policy_version="initial",
        split="holdout",
        mean=475.0,
    )
    _append_score(
        ledger_path,
        environment="MountainCar-v0",
        policy_version="initial",
        split="holdout",
        mean=-200.0,
    )
    write_summary_csv(ledger_path, summary_path)
    render_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
    )

    result = audit_environment_artifacts(
        "CartPole-v1",
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
    )

    assert result["pass_fail"] == "fail"
    issues = "\n".join(result["issues"])
    assert "ledger contains rows for other environments: MountainCar-v0" in issues
    assert "summary contains rows for other environments: MountainCar-v0" in issues
    assert "report missing scoped title" in issues
    assert "report includes other environment heading 'MountainCar-v0'" in issues
    assert "Generic environment artifact audit: fail" in render_audit_text(result)


def test_generic_env_artifact_audit_cli_writes_json_output(tmp_path: Path, monkeypatch, capsys) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    output_path = tmp_path / "audit_latest.json"
    _append_score(
        ledger_path,
        environment="CartPole-v1",
        policy_version="initial",
        split="holdout",
        mean=475.0,
    )
    write_summary_csv(ledger_path, summary_path)
    render_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        env_id="CartPole-v1",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.artifact_audit",
            "--env",
            "CartPole-v1",
            "--ledger",
            str(ledger_path),
            "--summary",
            str(summary_path),
            "--report",
            str(report_path),
            "--output",
            str(output_path),
            "--format",
            "json",
        ],
    )

    artifact_audit_module.main()

    assert output_path.exists()
    payload = output_path.read_text(encoding="utf-8")
    assert '"pass_fail": "pass"' in payload
    assert '"summary_content_checked": true' in capsys.readouterr().out


def test_generic_env_artifact_audit_cli_write_latest_uses_env_results_dir(
    tmp_path: Path,
    monkeypatch,
) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    env_results = tmp_path / "experiments" / "cartpole" / "results"
    _append_score(
        ledger_path,
        environment="CartPole-v1",
        policy_version="initial",
        split="holdout",
        mean=475.0,
    )
    write_summary_csv(ledger_path, summary_path)
    render_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        env_id="CartPole-v1",
    )
    monkeypatch.setattr(artifact_audit_module, "env_results_dir", lambda _env_id: env_results)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.artifact_audit",
            "--env",
            "CartPole-v1",
            "--ledger",
            str(ledger_path),
            "--summary",
            str(summary_path),
            "--report",
            str(report_path),
            "--write-latest",
        ],
    )

    artifact_audit_module.main()

    output_path = env_results / "audit_latest.json"
    assert output_path.exists()
    payload = output_path.read_text(encoding="utf-8")
    assert '"env_id": "CartPole-v1"' in payload
    assert '"pass_fail": "pass"' in payload


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
