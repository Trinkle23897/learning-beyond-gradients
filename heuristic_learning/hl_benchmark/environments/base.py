"""Shared environment registration types."""

from __future__ import annotations

from dataclasses import dataclass


GENERIC_ACTIVE_STATUS = "active"
CUSTOM_ACTIVE_STATUS = "custom_active"
PLANNED_STATUS = "planned"
VALID_STATUSES = {GENERIC_ACTIVE_STATUS, CUSTOM_ACTIVE_STATUS, PLANNED_STATUS}


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


@dataclass(frozen=True)
class EnvironmentRegistration:
    """Metadata needed to add one environment without changing core code.

    Status meanings:
    - ``active``: included in generic aggregate evaluator commands.
    - ``custom_active``: runnable through environment-specific commands, but not
      through the generic Gymnasium evaluator.
    - ``planned``: registered for docs/artifact paths, not yet runnable.
    """

    key: str
    spec: EnvSpec
    policy_module: str
    status: str = "active"
    suite_order: int = 1000
    artifact_slug: str | None = None
    custom_module: str | None = None
    optional_substitutions: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"unknown environment registration status: {self.status!r}"
            )
        if self.suite_order < 0:
            raise ValueError("suite_order must be non-negative")

    @property
    def slug(self) -> str:
        """Return the artifact directory slug for this environment."""

        return self.artifact_slug or self.key

    @property
    def custom_module_root(self) -> str:
        """Return the import root for custom-harness modules."""

        return self.custom_module or f"hl_benchmark.{self.slug}"
