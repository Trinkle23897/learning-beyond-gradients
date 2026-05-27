"""CartPole benchmark registration."""

from __future__ import annotations

from .base import EnvSpec, EnvironmentRegistration


REGISTRATION = EnvironmentRegistration(
    key="cartpole",
    policy_module="hl_benchmark.policies.cartpole",
    suite_order=10,
    spec=EnvSpec(
        env_id="CartPole-v1",
        category="classic_control",
        observation_summary="4 floats: cart position/velocity and pole angle/angular velocity.",
        action_summary="Discrete left/right cart push.",
        reward_interpretation="Reward +1 per step while the pole remains balanced.",
        episode_length=500,
        success_target=475.0,
        initial_policy="Linear sign controller on pole angle and angular velocity.",
        known_failure_modes=(
            "Cart drifts to the track edge while pole is locally stable.",
            "Large angular velocity cannot be recovered by the simple sign rule.",
        ),
        docs_url="https://gymnasium.farama.org/environments/classic_control/cart_pole/",
    ),
)
