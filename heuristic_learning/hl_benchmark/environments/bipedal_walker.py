"""BipedalWalker benchmark registration."""

from __future__ import annotations

from .base import EnvSpec, EnvironmentRegistration


REGISTRATION = EnvironmentRegistration(
    key="bipedal_walker",
    policy_module="hl_benchmark.policies.bipedal_walker",
    suite_order=50,
    optional_substitutions=("CarRacing-v3",),
    spec=EnvSpec(
        env_id="BipedalWalker-v3",
        category="box2d",
        observation_summary="Hull state, joint states, leg contact flags, and lidar fractions.",
        action_summary="4 continuous motor commands for hips and knees.",
        reward_interpretation="Forward progress minus torque cost, with large penalty for falling.",
        episode_length=1600,
        success_target=300.0,
        initial_policy="Open-loop alternating gait with hull stabilization.",
        known_failure_modes=(
            "Falls after phase drift because the open-loop gait ignores foot contact.",
            "Trips when hull pitch exceeds the controller's recoverable range.",
        ),
        docs_url="https://gymnasium.farama.org/environments/box2d/bipedal_walker/",
    ),
)
