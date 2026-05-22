from __future__ import annotations

import pytest

from hl_benchmark.search import candidate_configs, ensure_search_split_allowed


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

