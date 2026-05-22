"""Shared policy interfaces and helpers."""

from __future__ import annotations

from typing import Any


def _clip(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return float(min(high, max(low, value)))


class BasePolicy:
    """Small policy interface shared by all handwritten policies."""

    policy_name = "base"

    def reset(self, seed: int | None = None) -> None:
        del seed

    def act(self, obs: Any) -> Any:
        raise NotImplementedError

    def config(self) -> dict[str, Any]:
        return {}


class RandomPolicy(BasePolicy):
    """Random baseline policy using an environment action space."""

    policy_name = "random"

    def __init__(self, action_space: Any) -> None:
        self._action_space = action_space

    def reset(self, seed: int | None = None) -> None:
        if hasattr(self._action_space, "seed"):
            self._action_space.seed(seed)

    def act(self, obs: Any) -> Any:
        del obs
        return self._action_space.sample()
