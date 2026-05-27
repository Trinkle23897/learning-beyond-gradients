from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

import hl_benchmark.search as search_module
from hl_benchmark.artifacts import env_ledger_path, env_summary_path
from hl_benchmark.ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH
from hl_benchmark.search import (
    candidate_configs,
    ensure_search_split_allowed,
    resolve_search_paths,
    search_best_path,
)


def test_search_rejects_reserved_splits() -> None:
    for split in ["holdout", "audit"]:
        with pytest.raises(ValueError):
            ensure_search_split_allowed(split)


def test_search_spaces_are_bounded() -> None:
    for env_id in [
        "CartPole-v1",
        "MountainCar-v0",
        "Acrobot-v1",
        "LunarLander-v3",
        "BipedalWalker-v3",
    ]:
        candidates = candidate_configs(env_id, max_candidates=32)
        assert 1 <= len(candidates) <= 32
        assert all(isinstance(candidate, dict) for candidate in candidates)


def test_candidate_configs_dispatches_to_policy_module(monkeypatch) -> None:
    fake_policy_module = SimpleNamespace(
        candidate_configs=lambda *, max_candidates: [
            {"candidate": index} for index in range(max_candidates + 2)
        ]
    )
    monkeypatch.setattr(
        search_module,
        "registration_for",
        lambda _env_id: SimpleNamespace(policy_module="fake.policy"),
    )
    monkeypatch.setattr(
        search_module.importlib,
        "import_module",
        lambda module_name: fake_policy_module,
    )

    configs = candidate_configs("FakeEnv-v0", max_candidates=3)

    assert configs == [{"candidate": 0}, {"candidate": 1}, {"candidate": 2}]


def test_search_paths_can_use_per_environment_artifacts(tmp_path: Path) -> None:
    legacy_output = tmp_path / "legacy_best.json"
    ledger_path, summary_path, output_path = resolve_search_paths(
        "CartPole-v1",
        split="dev",
        ledger_path=None,
        summary_path=None,
        output_path=legacy_output,
        env_artifacts=False,
    )
    assert ledger_path == DEFAULT_LEDGER_PATH
    assert summary_path == DEFAULT_SUMMARY_PATH
    assert output_path == legacy_output
    assert search_best_path("CartPole-v1").as_posix().endswith(
        "results/search_best_CartPole-v1.json"
    )

    ledger_path, summary_path, output_path = resolve_search_paths(
        "CartPole-v1",
        split="dev",
        ledger_path=None,
        summary_path=None,
        output_path=None,
        env_artifacts=True,
    )
    assert ledger_path == env_ledger_path("CartPole-v1")
    assert summary_path == env_summary_path("CartPole-v1")
    assert output_path.as_posix().endswith(
        "experiments/cartpole/results/search_best_dev.json"
    )


def test_search_cli_env_artifacts_routes_each_env_to_own_outputs(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run_search(**kwargs):
        calls.append(kwargs)
        return {"pass_fail": "pass"}

    monkeypatch.setattr(
        search_module,
        "benchmark_env_ids",
        lambda: ["CartPole-v1", "MountainCar-v0"],
    )
    monkeypatch.setattr(search_module, "run_search", fake_run_search)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.search",
            "--all",
            "--split",
            "dev",
            "--max-candidates",
            "2",
            "--env-artifacts",
        ],
    )

    search_module.main()

    assert [call["env_id"] for call in calls] == ["CartPole-v1", "MountainCar-v0"]
    assert calls[0]["ledger_path"] == env_ledger_path("CartPole-v1")
    assert calls[0]["summary_path"] == env_summary_path("CartPole-v1")
    assert calls[0]["output_path"].as_posix().endswith(
        "experiments/cartpole/results/search_best_dev.json"
    )
    assert calls[1]["ledger_path"] == env_ledger_path("MountainCar-v0")
    assert calls[1]["summary_path"] == env_summary_path("MountainCar-v0")
    assert calls[1]["output_path"].as_posix().endswith(
        "experiments/mountain_car/results/search_best_dev.json"
    )

