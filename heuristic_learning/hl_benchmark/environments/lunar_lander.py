"""LunarLander benchmark registration."""

from __future__ import annotations

from .base import EnvSpec, EnvironmentRegistration


REGISTRATION = EnvironmentRegistration(
    key="lunar_lander",
    policy_module="hl_benchmark.policies.lunar_lander",
    suite_order=40,
    spec=EnvSpec(
        env_id="LunarLander-v3",
        category="box2d",
        observation_summary="8 floats: position, velocity, angle, angular velocity, and leg contacts.",
        action_summary="Discrete no-op, left engine, main engine, or right engine.",
        reward_interpretation="Dense shaping for safe centered landing, fuel penalty, crash/landing terminal rewards.",
        episode_length=1000,
        success_target=200.0,
        initial_policy="PD-style hover and angle controller.",
        known_failure_modes=(
            "Burns fuel while correcting lateral error late in descent.",
            "Over-rotates when one leg contacts before the other.",
        ),
        docs_url="https://gymnasium.farama.org/environments/box2d/lunar_lander/",
    ),
)
