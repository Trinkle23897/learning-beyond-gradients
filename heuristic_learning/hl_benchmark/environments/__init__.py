"""Per-environment registrations for the heuristic benchmark."""

from __future__ import annotations

import importlib
import pkgutil

from .base import (
    CUSTOM_ACTIVE_STATUS,
    GENERIC_ACTIVE_STATUS,
    PLANNED_STATUS,
    EnvSpec,
    EnvironmentRegistration,
)


_SKIP_DISCOVERY_MODULES = {"base"}


def _registration_sort_key(registration: EnvironmentRegistration) -> tuple[int, str]:
    return (registration.suite_order, registration.key)


def _iter_registration_module_names() -> tuple[str, ...]:
    """Return importable environment registration module names in this package."""

    names = []
    for module_info in pkgutil.iter_modules(__path__):
        name = module_info.name
        if name.startswith("_") or name in _SKIP_DISCOVERY_MODULES:
            continue
        names.append(name)
    return tuple(sorted(names))


def _load_registration(module_name: str) -> EnvironmentRegistration | None:
    module = importlib.import_module(f"{__name__}.{module_name}")
    registration = getattr(module, "REGISTRATION", None)
    if registration is None:
        return None
    if not isinstance(registration, EnvironmentRegistration):
        raise TypeError(
            f"{module.__name__}.REGISTRATION must be an EnvironmentRegistration"
        )
    return registration


def _duplicate_values(values: tuple[str, ...]) -> tuple[str, ...]:
    """Return duplicated values from a small registration field list."""

    return tuple(sorted(value for value in set(values) if values.count(value) > 1))


def _registration_collision_errors(
    registrations: tuple[EnvironmentRegistration, ...],
) -> tuple[str, ...]:
    """Return duplicate identifiers that would make the suite ambiguous."""

    checks = (
        (
            "environment ids",
            tuple(registration.spec.env_id for registration in registrations),
        ),
        (
            "environment keys",
            tuple(registration.key for registration in registrations),
        ),
        (
            "artifact slugs",
            tuple(registration.slug for registration in registrations),
        ),
        (
            "custom module roots",
            tuple(
                registration.custom_module_root
                for registration in registrations
                if registration.custom_module is not None
                or registration.status == CUSTOM_ACTIVE_STATUS
            ),
        ),
    )
    errors: list[str] = []
    for label, values in checks:
        duplicates = _duplicate_values(values)
        if duplicates:
            errors.append(f"duplicate {label}: {', '.join(duplicates)}")
    return tuple(errors)


def discover_registrations() -> tuple[EnvironmentRegistration, ...]:
    """Discover all environment modules that expose a REGISTRATION object."""

    registrations = tuple(
        registration
        for module_name in _iter_registration_module_names()
        if (registration := _load_registration(module_name)) is not None
    )
    collision_errors = _registration_collision_errors(registrations)
    if collision_errors:
        raise ValueError("; ".join(collision_errors))
    return tuple(sorted(registrations, key=_registration_sort_key))


ALL_REGISTRATIONS: tuple[EnvironmentRegistration, ...] = discover_registrations()

ACTIVE_REGISTRATIONS: tuple[EnvironmentRegistration, ...] = tuple(
    registration
    for registration in ALL_REGISTRATIONS
    if registration.status == GENERIC_ACTIVE_STATUS
)

CUSTOM_ACTIVE_REGISTRATIONS: tuple[EnvironmentRegistration, ...] = tuple(
    registration
    for registration in ALL_REGISTRATIONS
    if registration.status == CUSTOM_ACTIVE_STATUS
)

PLANNED_REGISTRATIONS: tuple[EnvironmentRegistration, ...] = tuple(
    registration
    for registration in ALL_REGISTRATIONS
    if registration.status == PLANNED_STATUS
)


def active_env_specs() -> dict[str, EnvSpec]:
    """Return specs that participate in default aggregate benchmark commands."""

    return {
        registration.spec.env_id: registration.spec
        for registration in ACTIVE_REGISTRATIONS
    }


def custom_active_env_specs() -> dict[str, EnvSpec]:
    """Return specs that run through environment-specific custom commands."""

    return {
        registration.spec.env_id: registration.spec
        for registration in CUSTOM_ACTIVE_REGISTRATIONS
    }


def planned_env_specs() -> dict[str, EnvSpec]:
    """Return specs for registered environments that are not runnable yet."""

    return {
        registration.spec.env_id: registration.spec
        for registration in PLANNED_REGISTRATIONS
    }


def known_env_specs() -> dict[str, EnvSpec]:
    """Return generic-active, custom-active, and planned environment specs."""

    return {
        registration.spec.env_id: registration.spec
        for registration in ALL_REGISTRATIONS
    }


def registration_for(env_id: str) -> EnvironmentRegistration:
    """Return registration metadata for any known environment id."""

    for registration in ALL_REGISTRATIONS:
        if registration.spec.env_id == env_id:
            return registration
    raise KeyError(f"unregistered environment: {env_id}")
