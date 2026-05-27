"""Shared policy interfaces and helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import Any


def _clip(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return float(min(high, max(low, value)))


def config_from_dict(config_type: type[Any], values: dict[str, Any] | None) -> Any:
    """Build a dataclass config while ignoring unknown scalar-search fields."""

    base = config_type()
    if not values:
        return base
    valid = {key: value for key, value in values.items() if hasattr(base, key)}
    return replace(base, **valid)


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
