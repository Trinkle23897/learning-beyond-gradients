"""MountainCar heuristic policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, ClassVar

import numpy as np

from .base import BasePolicy


@dataclass(frozen=True)
class MountainCarConfig:
    goal_commit_position: float = -0.20
    goal_commit_velocity: float = 0.000
    left_wall_position: float = -1.05
    coast_velocity_window: float = 0.000
    planner_grid_size: int = 301
    planner_horizon: int = 200


class MountainCarPolicy(BasePolicy):
    """Energy pumping and a transparent finite-horizon planner for MountainCar."""

    _planner_cache: ClassVar[dict[tuple[int, int], np.ndarray]] = {}
    _position_min: ClassVar[float] = -1.2
    _position_max: ClassVar[float] = 0.6
    _velocity_min: ClassVar[float] = -0.07
    _velocity_max: ClassVar[float] = 0.07
    _goal_position: ClassVar[float] = 0.5

    def __init__(
        self,
        config: MountainCarConfig | None = None,
        *,
        structural: bool = False,
    ) -> None:
        self._config = config or MountainCarConfig()
        self._structural = structural
        self.policy_name = "improved" if structural else "initial"
        self._step = 0

    def reset(self, seed: int | None = None) -> None:
        del seed
        self._step = 0

    @classmethod
    def _build_planner(cls, grid_size: int, horizon: int) -> np.ndarray:
        key = (grid_size, horizon)
        cached = cls._planner_cache.get(key)
        if cached is not None:
            return cached

        positions = np.linspace(cls._position_min, cls._position_max, grid_size, dtype=np.float32)
        velocities = np.linspace(cls._velocity_min, cls._velocity_max, grid_size, dtype=np.float32)
        position_grid, velocity_grid = np.meshgrid(positions, velocities, indexing="ij")
        next_value = np.zeros((grid_size, grid_size), dtype=np.float32)
        action_table = np.zeros((horizon, grid_size, grid_size), dtype=np.uint8)
        position_scale = (grid_size - 1) / (cls._position_max - cls._position_min)
        velocity_scale = (grid_size - 1) / (cls._velocity_max - cls._velocity_min)

        for step in range(horizon - 1, -1, -1):
            action_values = []
            for action in (0, 1, 2):
                next_velocity = velocity_grid + (action - 1) * 0.001 - 0.0025 * np.cos(3.0 * position_grid)
                next_velocity = np.clip(next_velocity, cls._velocity_min, cls._velocity_max)
                next_position = np.clip(position_grid + next_velocity, cls._position_min, cls._position_max)
                next_velocity = np.where(
                    (next_position <= cls._position_min) & (next_velocity < 0.0),
                    0.0,
                    next_velocity,
                )
                position_index = np.rint((next_position - cls._position_min) * position_scale).astype(np.int32)
                velocity_index = np.rint((next_velocity - cls._velocity_min) * velocity_scale).astype(np.int32)
                value = -1.0 + next_value[position_index, velocity_index]
                value = np.where(next_position >= cls._goal_position, -1.0, value)
                action_values.append(value)

            stacked = np.stack(action_values, axis=0)
            best_action = np.argmax(stacked, axis=0).astype(np.uint8)
            action_table[step] = best_action
            next_value = np.take_along_axis(stacked, best_action[None, :, :], axis=0)[0]

        cls._planner_cache[key] = action_table
        return action_table

    def _planner_action(self, position: float, velocity: float) -> int:
        cfg = self._config
        grid_size = max(51, int(cfg.planner_grid_size))
        horizon = max(1, int(cfg.planner_horizon))
        action_table = self._build_planner(grid_size, horizon)
        position_index = int(round((position - self._position_min) / (self._position_max - self._position_min) * (grid_size - 1)))
        velocity_index = int(round((velocity - self._velocity_min) / (self._velocity_max - self._velocity_min) * (grid_size - 1)))
        position_index = max(0, min(grid_size - 1, position_index))
        velocity_index = max(0, min(grid_size - 1, velocity_index))
        step_index = min(self._step, horizon - 1)
        return int(action_table[step_index, position_index, velocity_index])

    def act(self, obs: Any) -> int:
        position, velocity = np.asarray(obs, dtype=float)[:2]
        if self._structural:
            action = self._planner_action(float(position), float(velocity))
            self._step += 1
            return action
        return 2 if velocity >= 0.0 else 0

    def config(self) -> dict[str, Any]:
        return asdict(self._config) | {"structural_model_based_planner": self._structural}
