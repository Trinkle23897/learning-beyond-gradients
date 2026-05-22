"""Policy factory for benchmark environments."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .acrobot import AcrobotConfig, AcrobotDecisionTreePolicy, AcrobotPolicy
from .base import BasePolicy, RandomPolicy
from .bipedal_walker import BipedalWalkerConfig, BipedalWalkerPolicy
from .cartpole import CartPoleConfig, CartPolePolicy
from .lunar_lander import LunarLanderConfig, LunarLanderPolicy
from .mountain_car import MountainCarConfig, MountainCarPolicy


def _config_from_dict(config_type: type[Any], values: dict[str, Any] | None) -> Any:
    base = config_type()
    if not values:
        return base
    valid = {key: value for key, value in values.items() if hasattr(base, key)}
    return replace(base, **valid)


def make_policy(
    env_id: str,
    policy_name: str,
    *,
    action_space: Any | None = None,
    config: dict[str, Any] | None = None,
) -> BasePolicy:
    """Build a policy by environment and version name."""

    if policy_name == "random":
        if action_space is None:
            raise ValueError("random policy requires an action_space")
        return RandomPolicy(action_space)

    tuned = policy_name == "tuned"
    structural = policy_name == "improved"
    if policy_name not in {"initial", "improved", "tuned", "tree"}:
        raise ValueError(f"unknown policy {policy_name!r}")

    if env_id == "CartPole-v1":
        return CartPolePolicy(
            _config_from_dict(CartPoleConfig, config),
            structural=structural and not tuned,
        )
    if env_id == "MountainCar-v0":
        return MountainCarPolicy(
            _config_from_dict(MountainCarConfig, config),
            structural=structural and not tuned,
        )
    if env_id == "Acrobot-v1":
        if policy_name == "tree":
            return AcrobotDecisionTreePolicy()
        acrobot_structural = structural and not tuned
        acrobot_config = (
            None if config is None and acrobot_structural else _config_from_dict(AcrobotConfig, config)
        )
        return AcrobotPolicy(
            acrobot_config,
            structural=acrobot_structural,
        )
    if env_id == "LunarLander-v3":
        return LunarLanderPolicy(
            _config_from_dict(LunarLanderConfig, config),
            structural=structural and not tuned,
        )
    if env_id == "BipedalWalker-v3":
        return BipedalWalkerPolicy(
            _config_from_dict(BipedalWalkerConfig, config),
            structural=structural and not tuned,
        )
    raise ValueError(f"no policy registered for {env_id!r}")
