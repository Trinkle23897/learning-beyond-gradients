"""Transparent handwritten policies used by the benchmark."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, ClassVar

import numpy as np


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
        cfg = self._config
        if self._structural:
            action = self._planner_action(float(position), float(velocity))
            self._step += 1
            return action
        return 2 if velocity >= 0.0 else 0

    def config(self) -> dict[str, Any]:
        return asdict(self._config) | {"structural_model_based_planner": self._structural}


@dataclass(frozen=True)
class AcrobotConfig:
    velocity_gain_1: float = 0.75
    velocity_gain_2: float = 1.00
    phase_gain: float = 0.50
    upright_height_switch: float = 1.25
    upright_phase_gain: float = 1.10
    upright_velocity_gain: float = 0.25
    recovery_step: int = 140
    recovery_height_threshold: float = 0.20
    recovery_kick_gain: float = 0.90
    recovery_period: int = 9


class AcrobotPolicy(BasePolicy):
    """Underactuated swing-up rule for Acrobot."""

    def __init__(self, config: AcrobotConfig | None = None, *, structural: bool = False) -> None:
        if config is None and structural:
            config = replace(
                AcrobotConfig(),
                velocity_gain_1=0.75,
                velocity_gain_2=1.80,
                phase_gain=0.80,
            )
        self._config = config or AcrobotConfig()
        self._structural = structural
        self.policy_name = "improved" if structural else "initial"
        self._step = 0

    def reset(self, seed: int | None = None) -> None:
        del seed
        self._step = 0

    def act(self, obs: Any) -> int:
        self._step += 1
        values = np.asarray(obs, dtype=float)
        theta_1 = math.atan2(values[1], values[0])
        theta_2 = math.atan2(values[3], values[2])
        theta_dot_1 = values[4]
        theta_dot_2 = values[5]
        cfg = self._config
        tip_height = -math.cos(theta_1) - math.cos(theta_1 + theta_2)
        if self._structural and tip_height > cfg.upright_height_switch:
            command = (
                cfg.upright_phase_gain * math.sin(theta_1 + theta_2)
                + cfg.upright_velocity_gain * (theta_dot_1 + theta_dot_2)
            )
            if abs(command) < 0.10:
                return 1
        else:
            command = (
                cfg.velocity_gain_1 * theta_dot_1
                + cfg.velocity_gain_2 * theta_dot_2
                + cfg.phase_gain * math.sin(theta_1 + theta_2)
            )
        if (
            self._structural
            and self._step > cfg.recovery_step
            and tip_height < cfg.recovery_height_threshold
        ):
            period = max(cfg.recovery_period, 2)
            phase = 2.0 * math.pi * (self._step % period) / period
            command += cfg.recovery_kick_gain * math.sin(phase)
        return 2 if command > 0.0 else 0

    def config(self) -> dict[str, Any]:
        return asdict(self._config) | {"structural_recovery_mode": self._structural}


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


class AcrobotDecisionTreePolicy(BasePolicy):
    """Explicit decision tree distilled from the recorded PPO Acrobot comparator."""

    policy_name = "tree"

    def __init__(self, artifact_path: Path | None = None) -> None:
        path = artifact_path or Path(__file__).resolve().parents[1] / "results" / "acrobot_tree_policy.json"
        artifact = json.loads(path.read_text(encoding="utf-8"))
        self._artifact_path = path
        self._children_left = artifact["children_left"]
        self._children_right = artifact["children_right"]
        self._feature = artifact["feature"]
        self._threshold = artifact["threshold"]
        self._value = artifact["value"]
        self._classes = artifact["classes"]
        self._metadata = artifact.get("metadata", {})

    def act(self, obs: Any) -> int:
        values = np.asarray(obs, dtype=float)
        node = 0
        while self._children_left[node] != -1:
            feature_index = self._feature[node]
            if values[feature_index] <= self._threshold[node]:
                node = self._children_left[node]
            else:
                node = self._children_right[node]
        counts = self._value[node]
        best_index = int(np.argmax(np.asarray(counts, dtype=float)))
        return int(self._classes[best_index])

    def config(self) -> dict[str, Any]:
        return {
            "policy_type": "acrobot_distilled_decision_tree",
            "artifact": str(self._artifact_path),
            "node_count": self._metadata.get("node_count"),
            "max_depth": self._metadata.get("max_depth"),
            "min_samples_leaf": self._metadata.get("min_samples_leaf"),
            "teacher_algorithm": self._metadata.get("teacher_algorithm"),
            "teacher_train_steps": self._metadata.get("teacher_train_steps"),
            "training_seeds": self._metadata.get("training_seeds"),
            "validation_seeds": self._metadata.get("validation_seeds"),
            "tree_validation_mean": self._metadata.get("tree_validation", {}).get("mean"),
            "teacher_validation_mean": self._metadata.get("teacher_validation", {}).get("mean"),
        }


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

