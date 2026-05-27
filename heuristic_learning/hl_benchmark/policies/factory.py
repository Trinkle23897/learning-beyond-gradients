"""Policy factory for benchmark environments."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any

from hl_benchmark.environments import ALL_REGISTRATIONS, registration_for

from .base import BasePolicy, RandomPolicy


def _policy_module(module_name: str) -> ModuleType:
    return importlib.import_module(module_name)


def _supported_policy_names(module: ModuleType) -> set[str]:
    names = getattr(module, "SUPPORTED_POLICY_NAMES", ())
    if isinstance(names, str):
        return {names}
    return {str(name) for name in names}


def _known_policy_names() -> set[str]:
    names: set[str] = set()
    for registration in ALL_REGISTRATIONS:
        try:
            module = _policy_module(registration.policy_module)
        except Exception:
            continue
        names.update(_supported_policy_names(module))
    return names


def _require_supported_policy(env_id: str, policy_name: str, supported: set[str]) -> None:
    if policy_name not in supported:
        supported_names = ", ".join(sorted(supported | {"random"}))
        raise ValueError(
            f"{env_id} does not support policy {policy_name!r}; expected one of {supported_names}"
        )


def make_policy(
    env_id: str,
    policy_name: str,
    *,
    action_space: Any | None = None,
    config: dict[str, Any] | None = None,
) -> BasePolicy:
    """Build a policy by environment and version name.

    Environment-specific policy construction lives in the module named by the
    environment registration's ``policy_module``. This keeps adding a new
    environment local to ``hl_benchmark/environments/<slug>.py`` and
    ``hl_benchmark/policies/<slug>.py`` instead of growing this factory.
    """

    if policy_name == "random":
        if action_space is None:
            raise ValueError("random policy requires an action_space")
        return RandomPolicy(action_space)

    if policy_name not in _known_policy_names():
        raise ValueError(f"unknown policy {policy_name!r}")

    try:
        registration = registration_for(env_id)
    except KeyError as exc:
        raise ValueError(f"no policy registered for {env_id!r}") from exc

    module = _policy_module(registration.policy_module)
    supported = _supported_policy_names(module)
    _require_supported_policy(env_id, policy_name, supported)

    module_factory = getattr(module, "make_policy", None)
    if not callable(module_factory):
        raise ValueError(
            f"policy module {registration.policy_module!r} does not expose callable make_policy()"
        )
    policy = module_factory(policy_name, config=config)
    if not isinstance(policy, BasePolicy):
        raise TypeError(
            f"policy module {registration.policy_module!r} returned {type(policy).__name__}, "
            "expected BasePolicy"
        )
    return policy
