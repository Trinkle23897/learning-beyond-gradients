"""MountainCar benchmark registration."""

from __future__ import annotations

from .base import EnvSpec, EnvironmentRegistration


REGISTRATION = EnvironmentRegistration(
    key="mountain_car",
    policy_module="hl_benchmark.policies.mountain_car",
    suite_order=20,
    spec=EnvSpec(
        env_id="MountainCar-v0",
        category="classic_control",
        observation_summary="2 floats: position and velocity.",
        action_summary="Discrete push left, no push, or push right.",
        reward_interpretation="Reward -1 per step until the car reaches the goal.",
        episode_length=200,
        success_target=-110.0,
        initial_policy="Energy pumping by pushing in the direction of velocity.",
        known_failure_modes=(
            "Wastes momentum near the left wall.",
            "Can reverse too early near the goal approach.",
        ),
        docs_url="https://gymnasium.farama.org/environments/classic_control/mountain_car/",
    ),
)
