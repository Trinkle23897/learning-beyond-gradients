from __future__ import annotations

from hl_benchmark import rl_baseline


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
