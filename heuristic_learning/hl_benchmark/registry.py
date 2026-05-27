"""Inspect registered benchmark environments."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import (
    PROJECT_ROOT,
    custom_harness_module_slug,
    environment_test_scaffold_path,
    expected_experiment_dirs,
    expected_experiment_files,
    expected_experiment_placeholder_files,
    experiment_artifact_layout_issues,
)
from hl_benchmark.environments import (
    ACTIVE_REGISTRATIONS,
    ALL_REGISTRATIONS,
    CUSTOM_ACTIVE_REGISTRATIONS,
    PLANNED_REGISTRATIONS,
    registration_for,
)
from hl_benchmark.environments.base import (
    CUSTOM_ACTIVE_STATUS,
    GENERIC_ACTIVE_STATUS,
    PLANNED_STATUS,
)


ExecutionKind = str
REQUIRED_RUNNABLE_POLICY_NAMES = ("initial", "improved", "tuned")
SCAFFOLD_SOURCE_MARKERS = (
    "Scaffold only; keep status planned",
    "TODO: record observation space",
    "TODO: replace with the initial readable heuristic",
    "TODO: implement",
    "define scalar search space",
    '"status": "scaffold"',
    "pytest.mark.skip",
)
PLANNED_TEST_SCAFFOLD_MARKERS = (
    "pytest.mark.skip",
    "make check-planned-envs",
    "test_planned_readiness_gate_before_promotion",
)
RUNNABLE_TEST_SCAFFOLD_MARKERS = (
    "pytest.mark.skip",
    "TODO: replace",
    "make check-promotion",
    "make check-planned-envs",
    "test_planned_readiness_gate_before_promotion",
)


def _planned_test_scaffold_markers(registration: Any) -> tuple[str, ...]:
    """Return required markers tying a planned test scaffold to its env."""

    env_id = registration.spec.env_id
    module_slug = custom_harness_module_slug(env_id)
    return (
        *PLANNED_TEST_SCAFFOLD_MARKERS,
        f'ENV_ID = "{env_id}"',
        f'MODULE_SLUG = "{module_slug}"',
        f"make check-env ENV={env_id}",
        f"make check-promotion ENV={env_id}",
    )


def execution_kind(status: str) -> ExecutionKind:
    """Return how a registration is expected to run."""

    if status == GENERIC_ACTIVE_STATUS:
        return "generic-eval-all"
    if status == CUSTOM_ACTIVE_STATUS:
        return "custom-harness"
    return "not-runnable"


def runnable_registrations() -> tuple[Any, ...]:
    """Return registrations that must have runnable artifact layouts."""

    return (*ACTIVE_REGISTRATIONS, *CUSTOM_ACTIVE_REGISTRATIONS)


def _custom_module_for_output(registration: Any) -> str | None:
    """Return a custom harness module root only when it is meaningful."""

    if (
        registration.custom_module is not None
        or registration.status == CUSTOM_ACTIVE_STATUS
    ):
        return registration.custom_module_root
    return None


def registry_rows() -> list[dict[str, Any]]:
    """Return a stable machine-readable summary of all registered environments."""

    rows: list[dict[str, Any]] = []
    for registration in ALL_REGISTRATIONS:
        spec = registration.spec
        rows.append(
            {
                "env_id": spec.env_id,
                "key": registration.key,
                "slug": registration.slug,
                "status": registration.status,
                "execution": execution_kind(registration.status),
                "category": spec.category,
                "policy_module": registration.policy_module,
                "custom_module": _custom_module_for_output(registration),
                "artifact_dir": f"experiments/{registration.slug}",
            }
        )
    return rows


def _import_check(module_name: str) -> dict[str, str]:
    try:
        importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - exercised by failure messages in use.
        return {
            "module": module_name,
            "pass_fail": "fail",
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {"module": module_name, "pass_fail": "pass", "error": ""}


def _policy_factory_check(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - exercised by failure messages in use.
        return {
            "module": module_name,
            "pass_fail": "fail",
            "error": f"{type(exc).__name__}: {exc}",
            "supported_policy_names": [],
            "candidate_configs_available": False,
        }

    errors: list[str] = []
    supported = getattr(module, "SUPPORTED_POLICY_NAMES", None)
    if supported is None:
        names: list[str] = []
        errors.append("missing SUPPORTED_POLICY_NAMES")
    elif isinstance(supported, str):
        names = [supported]
    else:
        try:
            names = sorted(str(name) for name in supported)
        except TypeError:
            names = []
            errors.append("SUPPORTED_POLICY_NAMES must be iterable")
    if not names:
        errors.append("SUPPORTED_POLICY_NAMES is empty")
    if not callable(getattr(module, "make_policy", None)):
        errors.append("missing callable make_policy()")
    has_candidate_configs = callable(getattr(module, "candidate_configs", None))
    if not has_candidate_configs:
        errors.append("missing callable candidate_configs()")

    return {
        "module": module_name,
        "pass_fail": "fail" if errors else "pass",
        "error": "; ".join(errors),
        "supported_policy_names": names,
        "candidate_configs_available": has_candidate_configs,
    }


def _callable_main_check(module_name: str) -> dict[str, str]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - exercised by failure messages in use.
        return {
            "module": module_name,
            "pass_fail": "fail",
            "error": f"{type(exc).__name__}: {exc}",
        }
    main = getattr(module, "main", None)
    if not callable(main):
        return {
            "module": module_name,
            "pass_fail": "fail",
            "error": "missing callable main()",
        }
    return {"module": module_name, "pass_fail": "pass", "error": ""}


def _custom_harness_modules(module_root: str) -> tuple[str, ...]:
    return (
        module_root,
        f"{module_root}.adapter",
        f"{module_root}.evaluate",
        f"{module_root}.search",
        f"{module_root}.summarize",
        f"{module_root}.report",
        f"{module_root}.performance_report",
        f"{module_root}.audit",
    )


def _custom_command_modules(module_root: str) -> tuple[str, ...]:
    return (
        f"{module_root}.evaluate",
        f"{module_root}.search",
        f"{module_root}.summarize",
        f"{module_root}.report",
        f"{module_root}.performance_report",
        f"{module_root}.audit",
    )


def _module_source_path(module_name: str) -> Path | None:
    try:
        spec = importlib.util.find_spec(module_name)
    except Exception:
        return None
    origin = getattr(spec, "origin", None) if spec is not None else None
    if not origin or origin in {"built-in", "frozen", "namespace"}:
        return None
    path = Path(origin)
    return path if path.is_file() else None


def _scaffold_source_check(module_name: str) -> dict[str, Any]:
    path = _module_source_path(module_name)
    markers: list[str] = []
    if path is not None:
        text = path.read_text(encoding="utf-8")
        markers = [marker for marker in SCAFFOLD_SOURCE_MARKERS if marker in text]
    return {
        "module": module_name,
        "path": path.as_posix() if path is not None else "",
        "markers": markers,
        "pass_fail": "pass" if not markers else "fail",
    }


def _scaffold_source_checks(module_names: tuple[str, ...]) -> list[dict[str, Any]]:
    return [_scaffold_source_check(module_name) for module_name in module_names]


def _has_placeholder_text(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or normalized == "todo" or "todo:" in normalized


def _planned_test_scaffold_issues(registration: Any) -> tuple[str, ...]:
    """Return skipped-test scaffold issues for planned registrations."""

    if registration.status != PLANNED_STATUS:
        return ()
    path = environment_test_scaffold_path(registration.spec.env_id)
    if not path.is_file():
        return (f"missing {path.as_posix()}",)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return (f"unreadable {path.as_posix()}: {exc}",)
    missing_markers = tuple(
        marker
        for marker in _planned_test_scaffold_markers(registration)
        if marker not in text
    )
    return tuple(
        f"{path.as_posix()} missing planned test scaffold marker {marker!r}"
        for marker in missing_markers
    )


def _runnable_test_scaffold_issues(registration: Any) -> tuple[str, ...]:
    """Return unreplaced skipped-test scaffold issues for runnable envs."""

    if registration.status not in {GENERIC_ACTIVE_STATUS, CUSTOM_ACTIVE_STATUS}:
        return ()
    path = environment_test_scaffold_path(registration.spec.env_id)
    if not path.is_file():
        return ()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return (f"unreadable {path.as_posix()}: {exc}",)
    leftover_markers = tuple(
        marker for marker in RUNNABLE_TEST_SCAFFOLD_MARKERS if marker in text
    )
    return tuple(
        f"{path.as_posix()} still contains planned test scaffold marker {marker!r}"
        for marker in leftover_markers
    )


def _promotion_test_scaffold_issues(registration: Any) -> tuple[str, ...]:
    """Return skipped-test scaffold markers that block planned-env promotion."""

    if registration.status != PLANNED_STATUS:
        return ()
    path = environment_test_scaffold_path(registration.spec.env_id)
    if not path.is_file():
        return ()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return (f"unreadable {path.as_posix()}: {exc}",)
    leftover_markers = tuple(
        marker for marker in RUNNABLE_TEST_SCAFFOLD_MARKERS if marker in text
    )
    return tuple(
        f"{path.as_posix()} must replace planned test scaffold marker {marker!r} before promotion"
        for marker in leftover_markers
    )


def _runnable_spec_issues(registration: Any) -> tuple[str, ...]:
    """Return scaffold metadata issues for a promoted runnable registration."""

    spec = registration.spec
    issues: list[str] = []
    text_fields = (
        "category",
        "observation_summary",
        "action_summary",
        "reward_interpretation",
        "initial_policy",
        "docs_url",
    )
    for field_name in text_fields:
        value = getattr(spec, field_name)
        if _has_placeholder_text(value):
            issues.append(f"EnvSpec.{field_name} still contains scaffold placeholder")
    if spec.episode_length <= 0:
        issues.append("EnvSpec.episode_length must be positive for runnable environments")
    if not spec.known_failure_modes:
        issues.append("EnvSpec.known_failure_modes must document at least one failure mode")
    for index, failure_mode in enumerate(spec.known_failure_modes):
        if _has_placeholder_text(failure_mode):
            issues.append(
                f"EnvSpec.known_failure_modes[{index}] still contains scaffold placeholder"
            )
    return tuple(issues)


def environment_readiness_result(env_id: str) -> dict[str, Any]:
    """Return a machine-readable readiness check for one registered environment."""

    try:
        registration = registration_for(env_id)
    except KeyError as exc:
        return {
            "env_id": env_id,
            "pass_fail": "fail",
            "issues": [str(exc)],
            "registered": False,
        }

    status = registration.status
    execution = execution_kind(status)
    is_runnable = status in {GENERIC_ACTIVE_STATUS, CUSTOM_ACTIVE_STATUS}
    issues: list[str] = []
    artifact_issues = list(experiment_artifact_layout_issues(env_id))
    metadata_issues: list[str] = []
    planned_test_scaffold_issues = list(_planned_test_scaffold_issues(registration))
    runnable_test_scaffold_issues: list[str] = []
    if is_runnable:
        runnable_test_scaffold_issues = list(_runnable_test_scaffold_issues(registration))
    test_scaffold_issues = [
        *planned_test_scaffold_issues,
        *runnable_test_scaffold_issues,
    ]
    issues.extend(artifact_issues)
    issues.extend(test_scaffold_issues)
    if is_runnable:
        metadata_issues = list(_runnable_spec_issues(registration))
        issues.extend(metadata_issues)

    policy_import = _import_check(registration.policy_module)
    if policy_import["pass_fail"] != "pass":
        issues.append(f"policy module import failed: {policy_import['error']}")
    policy_factory = _policy_factory_check(registration.policy_module)
    missing_required_policy_names: tuple[str, ...] = ()
    if is_runnable:
        if policy_factory["pass_fail"] != "pass":
            issues.append(f"policy factory contract failed: {policy_factory['error']}")
        supported_names = set(policy_factory.get("supported_policy_names", []))
        missing_required_policy_names = tuple(
            name for name in REQUIRED_RUNNABLE_POLICY_NAMES if name not in supported_names
        )
        if missing_required_policy_names:
            issues.append(
                "runnable policy module missing required policy names: "
                + ", ".join(missing_required_policy_names)
            )

    custom_harness_modules: tuple[str, ...] = ()
    custom_harness_imports: list[dict[str, str]] = []
    custom_command_entrypoints: list[dict[str, str]] = []
    has_custom_harness = status == CUSTOM_ACTIVE_STATUS or (
        status == PLANNED_STATUS and registration.custom_module is not None
    )
    if has_custom_harness:
        custom_harness_modules = _custom_harness_modules(registration.custom_module_root)
        custom_harness_imports = [
            _import_check(module_name)
            for module_name in custom_harness_modules
        ]
        for import_result in custom_harness_imports:
            if import_result["pass_fail"] != "pass":
                issues.append(
                    "custom harness import failed for {module}: {error}".format(
                        **import_result
                    )
                )
        custom_command_entrypoints = [
            _callable_main_check(module_name)
            for module_name in _custom_command_modules(registration.custom_module_root)
        ]
        for entrypoint_result in custom_command_entrypoints:
            if entrypoint_result["pass_fail"] != "pass":
                issues.append(
                    "custom command main() missing for {module}: {error}".format(
                        **entrypoint_result
                    )
                )

    scaffold_source_checks: list[dict[str, Any]] = []
    if is_runnable:
        scaffold_source_checks = _scaffold_source_checks(
            (registration.policy_module,) + custom_harness_modules
        )
        for check in scaffold_source_checks:
            if check["markers"]:
                issues.append(
                    "scaffold markers remain in {module}: {markers}".format(
                        module=check["module"],
                        markers=", ".join(check["markers"]),
                    )
                )

    promotion_blockers: list[str] = []
    if status == PLANNED_STATUS:
        promotion_blockers.extend(artifact_issues)
        promotion_blockers.extend(planned_test_scaffold_issues)
        promotion_blockers.extend(_runnable_spec_issues(registration))
        promotion_blockers.extend(_promotion_test_scaffold_issues(registration))
        if policy_import["pass_fail"] != "pass":
            promotion_blockers.append(
                f"policy module import failed: {policy_import['error']}"
            )
        if policy_factory["pass_fail"] != "pass":
            promotion_blockers.append(
                f"policy factory contract failed: {policy_factory['error']}"
            )
        promotion_supported_names = set(policy_factory.get("supported_policy_names", []))
        promotion_missing_policy_names = tuple(
            name
            for name in REQUIRED_RUNNABLE_POLICY_NAMES
            if name not in promotion_supported_names
        )
        if promotion_missing_policy_names:
            promotion_blockers.append(
                "policy module missing required policy names before promotion: "
                + ", ".join(promotion_missing_policy_names)
            )
        for import_result in custom_harness_imports:
            if import_result["pass_fail"] != "pass":
                promotion_blockers.append(
                    "custom harness import failed before promotion for {module}: {error}".format(
                        **import_result
                    )
                )
        for entrypoint_result in custom_command_entrypoints:
            if entrypoint_result["pass_fail"] != "pass":
                promotion_blockers.append(
                    "custom command main() missing before promotion for {module}: {error}".format(
                        **entrypoint_result
                    )
                )
        promotion_scaffold_checks = _scaffold_source_checks(
            (registration.policy_module,) + custom_harness_modules
        )
        for check in promotion_scaffold_checks:
            if check["markers"]:
                promotion_blockers.append(
                    "scaffold markers remain before promotion in {module}: {markers}".format(
                        module=check["module"],
                        markers=", ".join(check["markers"]),
                    )
                )
    promotion_ready = not promotion_blockers if status == PLANNED_STATUS else not issues

    return {
        "env_id": env_id,
        "key": registration.key,
        "slug": registration.slug,
        "status": status,
        "execution": execution,
        "registered": True,
        "runnable": is_runnable,
        "promotion_ready": promotion_ready,
        "promotion_blockers": promotion_blockers,
        "artifact_dir": f"experiments/{registration.slug}",
        "artifact_issues": artifact_issues,
        "test_scaffold_issues": test_scaffold_issues,
        "planned_test_scaffold_issues": planned_test_scaffold_issues,
        "runnable_test_scaffold_issues": runnable_test_scaffold_issues,
        "metadata_issues": metadata_issues,
        "policy_module": registration.policy_module,
        "custom_module": _custom_module_for_output(registration),
        "policy_import": policy_import,
        "policy_factory": policy_factory,
        "required_policy_names": list(REQUIRED_RUNNABLE_POLICY_NAMES),
        "missing_required_policy_names": list(missing_required_policy_names),
        "custom_harness_imports": custom_harness_imports,
        "custom_command_entrypoints": custom_command_entrypoints,
        "scaffold_source_checks": scaffold_source_checks,
        "pass_fail": "pass" if not issues else "fail",
        "issues": issues,
    }


def render_environment_readiness(result: dict[str, Any]) -> str:
    """Render a compact human-readable environment readiness check."""

    lines = [f"Environment readiness: {result['pass_fail']}"]
    lines.append(f"- Environment: {result['env_id']}")
    if not result.get("registered", False):
        lines.append("- Registered: False")
    else:
        lines.extend(
            [
                "- Registered: True",
                f"- Status: {result['status']}",
                f"- Execution: {result['execution']}",
                f"- Promotion ready: {result['promotion_ready']}",
                f"- Artifacts: {result['artifact_dir']}",
                f"- Policy import: {result['policy_import']['pass_fail']}",
                f"- Policy factory: {result['policy_factory']['pass_fail']}",
            ]
        )
        if result.get("runnable", False):
            required_policy_status = (
                "pass" if not result.get("missing_required_policy_names") else "fail"
            )
            lines.append(f"- Required policies: {required_policy_status}")
        if result.get("custom_module"):
            lines.append(f"- Custom module: {result['custom_module']}")
        if "artifact_issues" in result:
            artifact_status = "pass" if not result["artifact_issues"] else "fail"
            lines.append(f"- Artifact layout: {artifact_status}")
        if result.get("status") == PLANNED_STATUS or result.get("test_scaffold_issues"):
            test_scaffold_status = "fail" if result.get("test_scaffold_issues") else "pass"
            lines.append(f"- Test scaffold: {test_scaffold_status}")
        if "metadata_issues" in result:
            if result.get("runnable", False):
                metadata_status = "pass" if not result["metadata_issues"] else "fail"
            else:
                metadata_status = "not checked until promotion"
            lines.append(f"- Metadata: {metadata_status}")
        if result.get("custom_harness_imports"):
            harness_status = "pass"
            if any(
                row["pass_fail"] != "pass"
                for row in result["custom_harness_imports"]
            ):
                harness_status = "fail"
            lines.append(f"- Custom harness imports: {harness_status}")
        if result.get("custom_command_entrypoints"):
            entrypoint_status = "pass"
            if any(
                row["pass_fail"] != "pass"
                for row in result["custom_command_entrypoints"]
            ):
                entrypoint_status = "fail"
            lines.append(f"- Custom command entrypoints: {entrypoint_status}")
        if result.get("scaffold_source_checks"):
            scaffold_status = "pass"
            if any(
                row["pass_fail"] != "pass"
                for row in result["scaffold_source_checks"]
            ):
                scaffold_status = "fail"
            lines.append(f"- Scaffold markers: {scaffold_status}")
    if result.get("promotion_blockers"):
        lines.append("- Promotion blockers:")
        lines.extend(f"  - {issue}" for issue in result["promotion_blockers"])
    if result.get("issues"):
        lines.append("- Issues:")
        lines.extend(f"  - {issue}" for issue in result["issues"])
    return "\n".join(lines) + "\n"


def environment_readiness_summary() -> dict[str, Any]:
    """Return readiness checks for runnable envs, plus visible planned envs."""

    checked = [
        environment_readiness_result(registration.spec.env_id)
        for registration in runnable_registrations()
    ]
    planned = [
        environment_readiness_result(registration.spec.env_id)
        for registration in PLANNED_REGISTRATIONS
    ]
    failures = [row for row in checked if row["pass_fail"] != "pass"]
    return {
        "pass_fail": "pass" if not failures else "fail",
        "checked_count": len(checked),
        "planned_count": len(planned),
        "checked": checked,
        "planned": planned,
        "errors": [
            f"{row['env_id']}: " + "; ".join(row.get("issues", []))
            for row in failures
        ],
    }


def render_environment_readiness_summary(result: dict[str, Any]) -> str:
    """Render a compact human-readable readiness summary."""

    lines = [f"Runnable environment readiness: {result['pass_fail']}"]
    lines.append(f"- Checked environments: {result['checked_count']}")
    planned_count = int(result.get("planned_count", 0))
    lines.append(f"- Planned environments: {planned_count}")
    for row in result["checked"]:
        lines.append(
            "- {env_id}: {pass_fail} ({execution}, {artifact_dir})".format(**row)
        )
    if planned_count:
        lines.append("- Planned registry entries:")
        for row in result.get("planned", []):
            lines.append(
                "  - {env_id}: {pass_fail} ({execution}, {artifact_dir})".format(**row)
            )
    if result.get("errors"):
        lines.append("- Issues:")
        lines.extend(f"  - {error}" for error in result["errors"])
    return "\n".join(lines) + "\n"


def promotion_readiness_summary() -> dict[str, Any]:
    """Return promotion readiness checks for all registered environments."""

    checked = [
        environment_readiness_result(registration.spec.env_id)
        for registration in ALL_REGISTRATIONS
    ]
    blocked = [row for row in checked if not row.get("promotion_ready", False)]
    ready = [row for row in checked if row.get("promotion_ready", False)]
    return {
        "pass_fail": "pass" if not blocked else "fail",
        "checked_count": len(checked),
        "ready_count": len(ready),
        "blocked_count": len(blocked),
        "checked": checked,
        "errors": [
            f"{row['env_id']}: " + "; ".join(row.get("promotion_blockers", []))
            for row in blocked
        ],
    }


def render_promotion_readiness_summary(result: dict[str, Any]) -> str:
    """Render a compact promotion-readiness summary."""

    lines = [f"Promotion readiness: {result['pass_fail']}"]
    lines.append(f"- Checked environments: {result['checked_count']}")
    lines.append(f"- Promotion ready: {result['ready_count']}")
    lines.append(f"- Promotion blocked: {result['blocked_count']}")
    for row in result["checked"]:
        readiness = "ready" if row.get("promotion_ready", False) else "blocked"
        lines.append(
            f"- {row['env_id']}: {readiness} ({row['status']}, {row['artifact_dir']})"
        )
    if result.get("errors"):
        lines.append("- Promotion blockers:")
        lines.extend(f"  - {error}" for error in result["errors"])
    return "\n".join(lines) + "\n"


def planned_environment_readiness_summary() -> dict[str, Any]:
    """Return readiness checks for all planned, non-runnable registrations."""

    checked = [
        environment_readiness_result(registration.spec.env_id)
        for registration in PLANNED_REGISTRATIONS
    ]
    failures = [row for row in checked if row["pass_fail"] != "pass"]
    return {
        "pass_fail": "pass" if not failures else "fail",
        "checked_count": len(checked),
        "checked": checked,
        "errors": [
            f"{row['env_id']}: " + "; ".join(row.get("issues", []))
            for row in failures
        ],
    }


def render_planned_environment_readiness_summary(result: dict[str, Any]) -> str:
    """Render a compact planned-environment readiness summary."""

    lines = [f"Planned environment readiness: {result['pass_fail']}"]
    lines.append(f"- Checked planned environments: {result['checked_count']}")
    if not result["checked"]:
        lines.append("- No planned environments registered.")
    for row in result["checked"]:
        lines.append(
            "- {env_id}: {pass_fail} ({execution}, {artifact_dir})".format(**row)
        )
    if result.get("errors"):
        lines.append("- Issues:")
        lines.extend(f"  - {error}" for error in result["errors"])
    return "\n".join(lines) + "\n"


def _display_path(path: Path) -> str:
    """Return a stable path for machine-readable local artifact output."""

    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def artifact_layout_result() -> dict[str, Any]:
    """Return a machine-readable artifact-layout check result."""

    checked: list[dict[str, Any]] = []
    errors: list[str] = []
    for registration in runnable_registrations():
        issues = list(experiment_artifact_layout_issues(registration.spec.env_id))
        env_id = registration.spec.env_id
        row = {
            "env_id": env_id,
            "key": registration.key,
            "slug": registration.slug,
            "status": registration.status,
            "artifact_dir": f"experiments/{registration.slug}",
            "required_dirs": [
                _display_path(path) for path in expected_experiment_dirs(env_id)
            ],
            "required_files": [
                _display_path(path) for path in expected_experiment_files(env_id)
            ],
            "required_placeholder_files": [
                _display_path(path)
                for path in expected_experiment_placeholder_files(env_id)
            ],
            "issues": issues,
            "pass_fail": "pass" if not issues else "fail",
        }
        checked.append(row)
        if issues:
            errors.append(f"{env_id}: " + "; ".join(issues))
    return {
        "pass_fail": "pass" if not errors else "fail",
        "checked_count": len(checked),
        "checked": checked,
        "errors": errors,
    }


def artifact_layout_errors() -> list[str]:
    """Return artifact-layout errors for runnable environments."""

    return list(artifact_layout_result()["errors"])


def render_registry_table(rows: list[dict[str, Any]] | None = None) -> str:
    """Render registered environments as a compact Markdown table."""

    rows = registry_rows() if rows is None else rows
    lines = [
        "| Environment | Status | Execution | Slug | Category | Custom Module | Artifacts |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {env_id} | {status} | {execution} | {slug} | {category} | {custom_module} | {artifact_dir} |".format(
                **{**row, "custom_module": row.get("custom_module") or "-"}
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format.",
    )
    parser.add_argument(
        "--check-artifacts",
        action="store_true",
        help="Validate required artifact directories and files for runnable environments.",
    )
    parser.add_argument(
        "--check-env",
        metavar="ENV_ID",
        help="Validate registry, artifact, policy, and custom-harness readiness for one environment without running evaluation.",
    )
    parser.add_argument(
        "--check-promotion",
        metavar="ENV_ID",
        help="Validate that one environment has no remaining blockers before promotion.",
    )
    parser.add_argument(
        "--check-promotions",
        action="store_true",
        help="Validate promotion readiness for all registered environments.",
    )
    parser.add_argument(
        "--check-envs",
        action="store_true",
        help="Validate readiness for all runnable registered environments without running evaluation.",
    )
    parser.add_argument(
        "--check-planned",
        action="store_true",
        help="Validate scaffold readiness for all planned registered environments.",
    )
    args = parser.parse_args()
    if args.check_env:
        result = environment_readiness_result(args.check_env)
        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(render_environment_readiness(result), end="")
        if result["pass_fail"] != "pass":
            raise SystemExit(1)
        return

    if args.check_promotion:
        result = environment_readiness_result(args.check_promotion)
        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(render_environment_readiness(result), end="")
        if not result.get("promotion_ready", False):
            raise SystemExit(1)
        return

    if args.check_promotions:
        result = promotion_readiness_summary()
        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(render_promotion_readiness_summary(result), end="")
        if result["pass_fail"] != "pass":
            raise SystemExit(1)
        return

    if args.check_envs:
        result = environment_readiness_summary()
        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(render_environment_readiness_summary(result), end="")
        if result["pass_fail"] != "pass":
            raise SystemExit(1)
        return

    if args.check_planned:
        result = planned_environment_readiness_summary()
        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(render_planned_environment_readiness_summary(result), end="")
        if result["pass_fail"] != "pass":
            raise SystemExit(1)
        return

    if args.check_artifacts:
        result = artifact_layout_result()
        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            if result["errors"]:
                for error in result["errors"]:
                    print(error)
            else:
                print("runnable artifact layout ok")
        if result["pass_fail"] != "pass":
            raise SystemExit(1)
        return

    rows = registry_rows()
    if args.format == "json":
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print(render_registry_table(rows), end="")


if __name__ == "__main__":
    main()
