"""LunarLander heuristic policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .base import BasePolicy, _clip


@dataclass(frozen=True)
class LunarLanderConfig:
    angle_x_gain: float = 0.50
    angle_vx_gain: float = 1.00
    angle_target_limit: float = 0.40
    hover_x_gain: float = 0.55
    angle_control_gain: float = 0.50
    angular_velocity_gain: float = 1.00
    hover_y_gain: float = 0.50
    vertical_velocity_gain: float = 0.50
    engine_deadband: float = 0.05
    contact_descent_gain: float = 0.65
    low_altitude_y: float = 0.20


class LunarLanderPolicy(BasePolicy):
    """PD-style LunarLander controller based on the Gym heuristic family."""

    def __init__(
        self,
        config: LunarLanderConfig | None = None,
        *,
        structural: bool = False,
    ) -> None:
        self._config = config or LunarLanderConfig()
        self._structural = structural
        self.policy_name = "improved" if structural else "initial"

    def act(self, obs: Any) -> int:
        x, y, vx, vy, angle, angular_velocity, left_contact, right_contact = np.asarray(
            obs, dtype=float
        )[:8]
        cfg = self._config
        angle_target = cfg.angle_x_gain * x + cfg.angle_vx_gain * vx
        angle_target = _clip(angle_target, -cfg.angle_target_limit, cfg.angle_target_limit)
        hover_target = cfg.hover_x_gain * abs(x)
        angle_todo = (
            cfg.angle_control_gain * (angle_target - angle)
            - cfg.angular_velocity_gain * angular_velocity
        )
        hover_todo = cfg.hover_y_gain * (hover_target - y) - cfg.vertical_velocity_gain * vy

        if left_contact or right_contact:
            angle_todo = -cfg.angular_velocity_gain * angular_velocity
            hover_todo = -cfg.contact_descent_gain * vy

        if self._structural:
            both_contact = bool(left_contact and right_contact)
            one_contact = bool(left_contact != right_contact)
            if both_contact:
                return 0
            if one_contact and abs(angle) > 0.05:
                return 3 if angle < 0.0 else 1
            if y < cfg.low_altitude_y and abs(vx) < 0.08 and abs(angle) < 0.10:
                angle_todo *= 0.55
                hover_todo += 0.04

        if hover_todo > abs(angle_todo) and hover_todo > cfg.engine_deadband:
            return 2
        if angle_todo < -cfg.engine_deadband:
            return 3
        if angle_todo > cfg.engine_deadband:
            return 1
        return 0

    def config(self) -> dict[str, Any]:
        return asdict(self._config) | {"structural_contact_landing_mode": self._structural}
