"""BipedalWalker heuristic policies."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .base import BasePolicy, _clip


@dataclass(frozen=True)
class BipedalWalkerConfig:
    gait_period: int = 48
    hip_amplitude: float = 0.65
    knee_drive: float = 0.80
    stance_knee: float = -0.35
    hull_angle_gain: float = 0.80
    hull_velocity_gain: float = 0.18
    recovery_angle: float = 0.45
    recovery_knee: float = 0.90
    walker_speed: float = 0.275
    walker_action_scale: float = 0.53
    walker_hip_gain: float = 0.90
    walker_hip_damping: float = 0.25
    walker_knee_gain: float = 4.00
    walker_knee_damping: float = 0.25
    walker_hull_angle_gain: float = 0.90
    walker_hull_angular_velocity_gain: float = 2.10
    walker_vertical_damping: float = 15.00
    walker_support_knee_angle: float = 0.10
    walker_support_increment: float = 0.03
    walker_moving_hip_target: float = 1.10
    walker_moving_knee_target: float = -0.60
    walker_put_down_hip_target: float = 0.10
    walker_push_off_knee_target: float = 1.00
    walker_support_behind_threshold: float = 0.10
    walker_push_off_knee_switch: float = 0.88
    walker_overspeed_switch: float = 1.20


class BipedalWalkerPolicy(BasePolicy):
    """Transparent gait controllers for BipedalWalker."""

    STAY_ON_ONE_LEG = 1
    PUT_OTHER_DOWN = 2
    PUSH_OFF = 3

    def __init__(
        self,
        config: BipedalWalkerConfig | None = None,
        *,
        structural: bool = False,
    ) -> None:
        self._config = config or BipedalWalkerConfig()
        self._structural = structural
        self.policy_name = "improved" if structural else "initial"
        self._step = 0
        self._walker_state = self.STAY_ON_ONE_LEG
        self._moving_leg = 0
        self._supporting_leg = 1
        self._supporting_knee_angle = self._config.walker_support_knee_angle

    def reset(self, seed: int | None = None) -> None:
        del seed
        self._step = 0
        self._walker_state = self.STAY_ON_ONE_LEG
        self._moving_leg = 0
        self._supporting_leg = 1
        self._supporting_knee_angle = self._config.walker_support_knee_angle

    def _state_machine_action(self, values: np.ndarray) -> np.ndarray:
        cfg = self._config
        moving_base = 4 + 5 * self._moving_leg
        supporting_base = 4 + 5 * self._supporting_leg
        hip_target: list[float | None] = [None, None]
        knee_target: list[float | None] = [None, None]
        hip_todo = [0.0, 0.0]
        knee_todo = [0.0, 0.0]

        if self._walker_state == self.STAY_ON_ONE_LEG:
            hip_target[self._moving_leg] = cfg.walker_moving_hip_target
            knee_target[self._moving_leg] = cfg.walker_moving_knee_target
            self._supporting_knee_angle += cfg.walker_support_increment
            if values[2] > cfg.walker_speed:
                self._supporting_knee_angle += cfg.walker_support_increment
            self._supporting_knee_angle = min(
                self._supporting_knee_angle, cfg.walker_support_knee_angle
            )
            knee_target[self._supporting_leg] = self._supporting_knee_angle
            if values[supporting_base] < cfg.walker_support_behind_threshold:
                self._walker_state = self.PUT_OTHER_DOWN

        if self._walker_state == self.PUT_OTHER_DOWN:
            hip_target[self._moving_leg] = cfg.walker_put_down_hip_target
            knee_target[self._moving_leg] = cfg.walker_support_knee_angle
            knee_target[self._supporting_leg] = self._supporting_knee_angle
            if values[moving_base + 4] > 0.5:
                self._walker_state = self.PUSH_OFF
                self._supporting_knee_angle = min(
                    values[moving_base + 2], cfg.walker_support_knee_angle
                )

        if self._walker_state == self.PUSH_OFF:
            knee_target[self._moving_leg] = self._supporting_knee_angle
            knee_target[self._supporting_leg] = cfg.walker_push_off_knee_target
            if (
                values[supporting_base + 2] > cfg.walker_push_off_knee_switch
                or values[2] > cfg.walker_overspeed_switch * cfg.walker_speed
            ):
                self._walker_state = self.STAY_ON_ONE_LEG
                self._moving_leg = 1 - self._moving_leg
                self._supporting_leg = 1 - self._moving_leg

        if hip_target[0] is not None:
            hip_todo[0] = cfg.walker_hip_gain * (hip_target[0] - values[4]) - cfg.walker_hip_damping * values[5]
        if hip_target[1] is not None:
            hip_todo[1] = cfg.walker_hip_gain * (hip_target[1] - values[9]) - cfg.walker_hip_damping * values[10]
        if knee_target[0] is not None:
            knee_todo[0] = cfg.walker_knee_gain * (knee_target[0] - values[6]) - cfg.walker_knee_damping * values[7]
        if knee_target[1] is not None:
            knee_todo[1] = cfg.walker_knee_gain * (knee_target[1] - values[11]) - cfg.walker_knee_damping * values[12]

        hull_todo = cfg.walker_hull_angle_gain * (0.0 - values[0]) - cfg.walker_hull_angular_velocity_gain * values[1]
        hip_todo[0] -= hull_todo
        hip_todo[1] -= hull_todo
        knee_todo[0] -= cfg.walker_vertical_damping * values[3]
        knee_todo[1] -= cfg.walker_vertical_damping * values[3]

        action = cfg.walker_action_scale * np.asarray(
            [hip_todo[0], knee_todo[0], hip_todo[1], knee_todo[1]], dtype=float
        )
        return np.clip(action, -1.0, 1.0).astype(np.float32)

    def act(self, obs: Any) -> np.ndarray:
        values = np.asarray(obs, dtype=float)
        cfg = self._config

        if self._structural:
            return self._state_machine_action(values)

        hull_angle = float(values[0]) if values.size > 0 else 0.0
        hull_angular_velocity = float(values[1]) if values.size > 1 else 0.0
        phase = 2.0 * math.pi * (self._step % max(cfg.gait_period, 2)) / max(cfg.gait_period, 2)
        self._step += 1
        s = math.sin(phase)
        hull_correction = -cfg.hull_angle_gain * hull_angle - cfg.hull_velocity_gain * hull_angular_velocity
        left_swing = s > 0.0
        left_hip = _clip(-cfg.hip_amplitude * s + hull_correction)
        right_hip = _clip(cfg.hip_amplitude * s + hull_correction)
        left_knee = cfg.knee_drive if left_swing else cfg.stance_knee
        right_knee = cfg.stance_knee if left_swing else cfg.knee_drive
        return np.asarray(
            [
                _clip(left_hip),
                _clip(left_knee),
                _clip(right_hip),
                _clip(right_knee),
            ],
            dtype=np.float32,
        )

    def config(self) -> dict[str, Any]:
        return asdict(self._config) | {"structural_state_machine_walker": self._structural}
