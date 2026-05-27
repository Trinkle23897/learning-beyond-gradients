from __future__ import annotations

from pathlib import Path
import sys

from hl_benchmark import rl_baseline
from hl_benchmark.artifacts import env_ledger_path, env_summary_path
from hl_benchmark.ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH


def test_rl_score_stats() -> None:
    stats = rl_baseline._score_stats([1.0, 2.0, 3.0])
    assert stats["mean"] == 2.0
    assert stats["median"] == 2.0
    assert stats["min"] == 1.0
    assert stats["max"] == 3.0


def test_rl_module_exposes_cli_training_function() -> None:
    assert callable(rl_baseline.train_evaluate_ppo)
    assert callable(rl_baseline.train_evaluate_sac)
    assert callable(rl_baseline.load_hf_baseline)


def test_rl_baseline_paths_can_use_per_environment_artifacts(tmp_path: Path) -> None:
    legacy_ledger = tmp_path / "legacy" / "trials.jsonl"
    legacy_summary = tmp_path / "legacy" / "summary.csv"
    ledger_path, summary_path = rl_baseline.resolve_rl_baseline_paths(
        env_id="CartPole-v1",
        ledger_path=legacy_ledger,
        summary_path=legacy_summary,
        env_artifacts=False,
    )
    assert ledger_path == legacy_ledger
    assert summary_path == legacy_summary

    ledger_path, summary_path = rl_baseline.resolve_rl_baseline_paths(
        env_id="CartPole-v1",
        ledger_path=None,
        summary_path=None,
        env_artifacts=False,
    )
    assert ledger_path == DEFAULT_LEDGER_PATH
    assert summary_path == DEFAULT_SUMMARY_PATH

    ledger_path, summary_path = rl_baseline.resolve_rl_baseline_paths(
        env_id="CartPole-v1",
        ledger_path=None,
        summary_path=None,
        env_artifacts=True,
    )
    assert ledger_path == env_ledger_path("CartPole-v1")
    assert summary_path == env_summary_path("CartPole-v1")


def test_rl_baseline_cli_env_artifacts_routes_single_env_outputs(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_train_evaluate_baseline(**kwargs):
        captured.update(kwargs)
        return {
            "pass_fail": "pass",
            "score_stats": {"mean": 12.5},
            "environment_steps": 123,
        }

    monkeypatch.setattr(
        rl_baseline,
        "train_evaluate_baseline",
        fake_train_evaluate_baseline,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.rl_baseline",
            "--env",
            "CartPole-v1",
            "--split",
            "smoke",
            "--algo",
            "ppo",
            "--train-steps",
            "100",
            "--env-artifacts",
        ],
    )

    rl_baseline.main()

    assert captured["env_id"] == "CartPole-v1"
    assert captured["split"] == "smoke"
    assert captured["algorithm"] == "ppo"
    assert captured["train_steps"] == 100
    assert captured["ledger_path"] == env_ledger_path("CartPole-v1")
    assert captured["summary_path"] == env_summary_path("CartPole-v1")
