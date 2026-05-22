"""Environment registry and runtime discovery for the benchmark."""

from __future__ import annotations

import importlib.metadata as metadata
import platform
import sys
from dataclasses import dataclass
from typing import Any


SEED_SPLITS: dict[str, range] = {
    "dev": range(0, 20),
    "holdout": range(1000, 1050),
    "audit": range(2000, 2050),
    "smoke": range(0, 2),
}


@dataclass(frozen=True)
class EnvSpec:
    """Static benchmark metadata for one environment."""

    env_id: str
    category: str
    observation_summary: str
    action_summary: str
    reward_interpretation: str
    episode_length: int
    success_target: float
    initial_policy: str
    known_failure_modes: tuple[str, ...]
    docs_url: str


ENV_SPECS: dict[str, EnvSpec] = {
    "CartPole-v1": EnvSpec(
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
    "MountainCar-v0": EnvSpec(
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
    "Acrobot-v1": EnvSpec(
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
    "LunarLander-v3": EnvSpec(
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
    "BipedalWalker-v3": EnvSpec(
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
}


OPTIONAL_SUBSTITUTIONS: dict[str, tuple[str, ...]] = {
    "BipedalWalker-v3": ("CarRacing-v3",),
}


def get_seeds(split: str, *, seed_start: int | None = None, episodes: int | None = None) -> list[int]:
    """Return deterministic seeds for a named split or explicit range."""

    if seed_start is not None:
        if episodes is None:
            raise ValueError("episodes must be set when seed_start is provided")
        return list(range(seed_start, seed_start + episodes))
    if split not in SEED_SPLITS:
        raise ValueError(f"unknown seed split {split!r}; expected one of {sorted(SEED_SPLITS)}")
    seeds = list(SEED_SPLITS[split])
    if episodes is not None:
        return seeds[:episodes]
    return seeds


def benchmark_env_ids() -> list[str]:
    """Return the canonical benchmark order."""

    return list(ENV_SPECS)


def spec_for(env_id: str) -> EnvSpec:
    """Return metadata for a registered environment."""

    if env_id not in ENV_SPECS:
        raise KeyError(f"unregistered environment: {env_id}")
    return ENV_SPECS[env_id]


def import_gymnasium() -> Any:
    """Import Gymnasium lazily so schema/report tests can run without it."""

    try:
        import gymnasium as gym
    except Exception as exc:  # pragma: no cover - exercised on dependency gaps
        raise RuntimeError(
            "Gymnasium is not available. Install this subproject with "
            "`python3 -m pip install -e .` from heuristic_learning/."
        ) from exc
    return gym


def make_env(env_id: str) -> Any:
    """Create a Gymnasium environment from the registry."""

    gym = import_gymnasium()
    return gym.make(env_id)


def check_env_available(env_id: str) -> tuple[bool, str]:
    """Return whether Gymnasium can instantiate an environment."""

    try:
        env = make_env(env_id)
        env.close()
    except Exception as exc:  # pragma: no cover - depends on local packages
        return False, f"{type(exc).__name__}: {exc}"
    return True, "available"


def discover_runtime_metadata() -> dict[str, Any]:
    """Collect package/runtime versions needed for auditability."""

    package_names = [
        "gymnasium",
        "box2d-py",
        "Box2D",
        "pygame",
        "pygame-ce",
        "swig",
        "numpy",
        "pandas",
        "pytest",
        "stable-baselines3",
        "torch",
    ]
    versions: dict[str, str] = {}
    for package_name in package_names:
        try:
            versions[package_name] = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            versions[package_name] = "not_installed"
    return {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "packages": versions,
    }

