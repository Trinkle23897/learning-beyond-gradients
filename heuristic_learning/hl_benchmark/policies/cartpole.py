"""CartPole heuristic policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .base import BasePolicy


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
