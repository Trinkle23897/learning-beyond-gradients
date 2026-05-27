"""CartPole heuristic policies."""

from __future__ import annotations

import itertools
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .base import BasePolicy, config_from_dict


@dataclass(frozen=True)
class CartPoleConfig:
    pole_angle_gain: float = 1.0
    pole_velocity_gain: float = 0.35
    cart_position_gain: float = 0.05
    cart_velocity_gain: float = 0.02
    center_position_gain: float = 1.0
    center_velocity_gain: float = 0.60
    center_angle_window: float = 0.03
    center_velocity_window: float = 0.20
    center_position_trigger: float = 1.00


class CartPolePolicy(BasePolicy):
    """Readable sign controller for CartPole."""

    def __init__(self, config: CartPoleConfig | None = None, *, structural: bool = False) -> None:
        self._config = config or CartPoleConfig()
        self._structural = structural
        self.policy_name = "improved" if structural else "initial"

    def act(self, obs: Any) -> int:
        x, x_dot, theta, theta_dot = np.asarray(obs, dtype=float)[:4]
        cfg = self._config
        if (
            self._structural
            and abs(x) > cfg.center_position_trigger
            and abs(theta) < cfg.center_angle_window
            and abs(theta_dot) < cfg.center_velocity_window
        ):
            # Structural guard: when the pole is safe, spend control authority recentering the cart.
            score = cfg.center_position_gain * x + cfg.center_velocity_gain * x_dot
            return 0 if score > 0.0 else 1
        score = (
            cfg.pole_angle_gain * theta
            + cfg.pole_velocity_gain * theta_dot
            + cfg.cart_position_gain * x
            + cfg.cart_velocity_gain * x_dot
        )
        return 1 if score > 0.0 else 0

    def config(self) -> dict[str, Any]:
        return asdict(self._config) | {"structural_center_guard": self._structural}


def candidate_configs(*, max_candidates: int = 32) -> list[dict[str, Any]]:
    """Return scalar-only CartPole configs for the generic search baseline."""

    candidates: list[dict[str, Any]] = []
    for pole_velocity_gain, cart_position_gain, cart_velocity_gain in itertools.product(
        [0.25, 0.35, 0.50, 0.70],
        [0.00, 0.03, 0.06, 0.10],
        [0.00, 0.02],
    ):
        candidates.append(
            {
                "pole_velocity_gain": pole_velocity_gain,
                "cart_position_gain": cart_position_gain,
                "cart_velocity_gain": cart_velocity_gain,
            }
        )
    return candidates[:max_candidates]


SUPPORTED_POLICY_NAMES = ("initial", "improved", "tuned")


def make_policy(
    policy_name: str,
    *,
    config: dict[str, Any] | None = None,
) -> BasePolicy:
    """Build a CartPolePolicy from this environment-local policy registry."""

    if policy_name not in SUPPORTED_POLICY_NAMES:
        raise ValueError(f"unsupported cartpole policy {policy_name!r}")
    return CartPolePolicy(
        config_from_dict(CartPoleConfig, config),
        structural=policy_name == "improved",
    )
