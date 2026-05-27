"""Environment registry and runtime discovery for the benchmark.

The public API in this module is intentionally stable because evaluation,
search, reports, and older reproducibility notes import it directly. Static
environment metadata now lives in per-environment modules under
``hl_benchmark.environments`` so adding a new environment does not require
editing a large central spec table.
"""

from __future__ import annotations

import importlib.metadata as metadata
import platform
import sys
from typing import Any

from .environments import (
    active_env_specs,
    custom_active_env_specs,
    known_env_specs,
    planned_env_specs,
    registration_for,
)
from .environments.base import EnvSpec


SEED_SPLITS: dict[str, range] = {
    "dev": range(0, 20),
    "holdout": range(1000, 1050),
    "audit": range(2000, 2050),
    "smoke": range(0, 2),
}


ENV_SPECS: dict[str, EnvSpec] = active_env_specs()
CUSTOM_ENV_SPECS: dict[str, EnvSpec] = custom_active_env_specs()
PLANNED_ENV_SPECS: dict[str, EnvSpec] = planned_env_specs()
KNOWN_ENV_SPECS: dict[str, EnvSpec] = known_env_specs()


OPTIONAL_SUBSTITUTIONS: dict[str, tuple[str, ...]] = {
    registration.spec.env_id: registration.optional_substitutions
    for registration in (registration_for(env_id) for env_id in ENV_SPECS)
    if registration.optional_substitutions
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
    """Return the canonical active benchmark order."""

    return list(ENV_SPECS)


def custom_env_ids() -> list[str]:
    """Return environments with runnable custom harnesses outside eval-all."""

    return list(CUSTOM_ENV_SPECS)


def planned_env_ids() -> list[str]:
    """Return registered environments that are scaffolded but not runnable."""

    return list(PLANNED_ENV_SPECS)


def spec_for(env_id: str) -> EnvSpec:
    """Return metadata for any known registered environment."""

    if env_id not in KNOWN_ENV_SPECS:
        raise KeyError(f"unregistered environment: {env_id}")
    return KNOWN_ENV_SPECS[env_id]


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
    """Create a Gymnasium environment from the registry or a compatible env id."""

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
        "gym",
        "opencv-python",
        "slimevolleygym",
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
