"""Custom-active SlimeVolley registration.

SlimeVolley uses the legacy Gym API and an adversarial opponent protocol, so it
runs through a custom harness instead of the generic Gymnasium aggregate
evaluator. The registry points at ``hl_benchmark.custom_envs.slimevolley`` so
future custom environments follow the same package layout; that bridge delegates
to the established ``hl_benchmark.slimevolley`` implementation for compatibility.
"""

from __future__ import annotations

from .base import EnvSpec, EnvironmentRegistration


REGISTRATION = EnvironmentRegistration(
    key="slimevolley",
    status="custom_active",
    policy_module="hl_benchmark.policies.slimevolley",
    custom_module="hl_benchmark.custom_envs.slimevolley",
    suite_order=100,
    spec=EnvSpec(
        env_id="SlimeVolley-v0",
        category="competitive_control",
        observation_summary=(
            "Agent-centric continuous state for the player, opponent, ball position, "
            "and ball velocity as exposed by slimevolleygym."
        ),
        action_summary="Multi-binary movement/jump controls in the original Gym API.",
        reward_interpretation=(
            "Point/life-difference reward in a two-player volleyball duel; exact "
            "semantics must be verified against the installed slimevolleygym version."
        ),
        episode_length=3000,
        success_target=0.0,
        initial_policy=(
            "Modest handwritten controller: track the ball, defend a home position, "
            "jump near likely contact, and avoid overcommitting."
        ),
        known_failure_modes=(
            "Mistimed jumps on high arcs.",
            "Weak serve behavior.",
            "Overfitting to the built-in opponent.",
            "Regression against archived policy versions.",
        ),
        docs_url="https://github.com/hardmaru/slimevolleygym",
    ),
    notes=(
        "Runnably custom-active through hl_benchmark.custom_envs.slimevolley commands.",
        "The bridge delegates to hl_benchmark.slimevolley to preserve existing imports.",
        "Excluded from benchmark_env_ids() because it requires a legacy Gym adapter and opponent protocol.",
        "Artifacts live under experiments/slimevolley/.",
    ),
)
