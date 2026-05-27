"""Acrobot benchmark registration."""

from __future__ import annotations

from .base import EnvSpec, EnvironmentRegistration


REGISTRATION = EnvironmentRegistration(
    key="acrobot",
    policy_module="hl_benchmark.policies.acrobot",
    suite_order=30,
    spec=EnvSpec(
        env_id="Acrobot-v1",
        category="classic_control",
        observation_summary="Cos/sin joint angles plus two joint angular velocities.",
        action_summary="Discrete negative, zero, or positive joint torque.",
        reward_interpretation="Reward -1 per step until the free end reaches the target height.",
        episode_length=500,
        success_target=-100.0,
        initial_policy="Swing-up torque rule based on link phase and angular velocity.",
        known_failure_modes=(
            "Pumps energy out of phase near the upright region.",
            "Cannot stabilize the final swing if both joints reverse at the wrong time.",
        ),
        docs_url="https://gymnasium.farama.org/environments/classic_control/acrobot/",
    ),
)
