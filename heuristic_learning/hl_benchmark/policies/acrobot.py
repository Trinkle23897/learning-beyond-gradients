"""Acrobot heuristic and transparent tree policies."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from .base import BasePolicy


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


class AcrobotDecisionTreePolicy(BasePolicy):
    """Explicit decision tree distilled from the recorded PPO Acrobot comparator."""

    policy_name = "tree"

    def __init__(self, artifact_path: Path | None = None) -> None:
        path = artifact_path or Path(__file__).resolve().parents[2] / "results" / "acrobot_tree_policy.json"
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
