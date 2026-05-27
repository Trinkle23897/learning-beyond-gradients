from __future__ import annotations

import importlib
import json
import py_compile
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Sequence

import pytest
from setuptools import find_packages

import hl_benchmark.registry as registry_module
import hl_benchmark.artifacts as artifacts_module
import hl_benchmark.environments as environment_module
import hl_benchmark.custom as custom_module

import hl_benchmark

from hl_benchmark.custom import (
    available_custom_commands,
    custom_verify_extra_commands,
    custom_command_module_name,
    render_available_custom_commands,
    require_custom_registration,
)
from hl_benchmark.artifacts import (
    CUSTOM_HARNESS_FILES,
    PROJECT_ROOT,
    custom_harness_dir,
    custom_harness_module_slug,
    custom_harness_parent_init_path,
    environment_registration_path,
    environment_test_scaffold_path,
    env_ledger_path,
    expected_experiment_dirs,
    expected_experiment_files,
    expected_experiment_placeholder_files,
    experiment_artifact_layout_issues,
    experiment_dir,
    experiment_readme_identity_issues,
    expected_custom_harness_files,
    expected_environment_code_files,
    policy_scaffold_path,
    render_custom_harness_file,
    render_custom_harness_parent_init_file,
    render_environment_registration_file,
    render_policy_scaffold_file,
    render_environment_test_scaffold_file,
    render_experiment_readme,
    render_scaffold_result,
    scaffold_custom_harness_code,
    scaffold_environment_code,
    scaffold_environment_tests,
    scaffold_experiment_artifacts,
    missing_experiment_artifacts,
    missing_experiment_dirs,
    missing_experiment_files,
    missing_experiment_placeholder_files,
    slug_for_env_id,
)
from hl_benchmark.envs import (
    CUSTOM_ENV_SPECS,
    ENV_SPECS,
    KNOWN_ENV_SPECS,
    PLANNED_ENV_SPECS,
    benchmark_env_ids,
    custom_env_ids,
    planned_env_ids,
    spec_for,
)
from hl_benchmark.environments.base import EnvSpec, EnvironmentRegistration
from hl_benchmark.environments import (
    ACTIVE_REGISTRATIONS,
    ALL_REGISTRATIONS,
    CUSTOM_ACTIVE_REGISTRATIONS,
    PLANNED_REGISTRATIONS,
    discover_registrations,
    registration_for,
)
from hl_benchmark.registry import (
    REQUIRED_RUNNABLE_POLICY_NAMES,
    artifact_layout_errors,
    artifact_layout_result,
    environment_readiness_result,
    environment_readiness_summary,
    planned_environment_readiness_summary,
    registry_rows,
    render_environment_readiness,
    render_environment_readiness_summary,
    render_planned_environment_readiness_summary,
    render_registry_table,
)


def test_active_registry_preserves_existing_benchmark_order() -> None:
    assert REQUIRED_RUNNABLE_POLICY_NAMES == ("initial", "improved", "tuned")
    assert benchmark_env_ids() == [
        "CartPole-v1",
        "MountainCar-v0",
        "Acrobot-v1",
        "LunarLander-v3",
        "BipedalWalker-v3",
    ]
    assert list(ENV_SPECS) == benchmark_env_ids()
    assert len(ACTIVE_REGISTRATIONS) == 5


def test_custom_harness_module_slug_sanitizes_registered_artifact_slug(monkeypatch) -> None:
    registration = SimpleNamespace(slug="Future-Env.v0")
    monkeypatch.setattr(artifacts_module, "registration_for", lambda _env_id: registration)

    assert custom_harness_module_slug("FutureEnv-v0") == "future_env_v0"

    registration.slug = "123-Future.v0"
    assert custom_harness_module_slug("FutureEnv-v0") == "env_123_future_v0"


def test_registry_auto_discovers_environment_modules() -> None:
    module_names = {
        path.stem
        for path in (PROJECT_ROOT / "hl_benchmark" / "environments").glob("*.py")
        if path.stem not in {"__init__", "base"} and not path.stem.startswith("_")
    }
    discovered = discover_registrations()
    discovered_modules = set()
    for module_name in module_names:
        module = importlib.import_module(f"hl_benchmark.environments.{module_name}")
        assert module.REGISTRATION in discovered
        discovered_modules.add(module_name)

    assert discovered_modules == module_names
    assert discovered == ALL_REGISTRATIONS
    assert list(discovered) == sorted(
        discovered,
        key=lambda registration: (registration.suite_order, registration.key),
    )


def test_scaffolded_registration_files_are_auto_discoverable(
    tmp_path,
    monkeypatch,
) -> None:
    package_dir = tmp_path / "hl_benchmark"
    scaffold_environment_code("AutoDiscover-v0", package_dir=package_dir)
    scaffold_environment_code(
        "AutoCustom-v0",
        package_dir=package_dir,
        include_custom_module=True,
    )
    env_package_dir = package_dir / "environments"

    monkeypatch.setattr(environment_module, "__path__", [str(env_package_dir)])
    for module_name in (
        "hl_benchmark.environments.autodiscover_v0",
        "hl_benchmark.environments.autocustom_v0",
    ):
        monkeypatch.delitem(sys.modules, module_name, raising=False)
    importlib.invalidate_caches()

    discovered = environment_module.discover_registrations()

    by_env = {registration.spec.env_id: registration for registration in discovered}
    assert sorted(by_env) == ["AutoCustom-v0", "AutoDiscover-v0"]
    generic = by_env["AutoDiscover-v0"]
    custom = by_env["AutoCustom-v0"]
    assert generic.status == "planned"
    assert generic.key == "autodiscover_v0"
    assert generic.policy_module == "hl_benchmark.policies.autodiscover_v0"
    assert generic.custom_module is None
    assert generic.custom_module_root == "hl_benchmark.autodiscover_v0"
    assert custom.status == "planned"
    assert custom.key == "autocustom_v0"
    assert custom.policy_module == "hl_benchmark.policies.autocustom_v0"
    assert custom.custom_module == "hl_benchmark.custom_envs.autocustom_v0"
    assert custom.custom_module_root == "hl_benchmark.custom_envs.autocustom_v0"
    assert [registration.key for registration in discovered] == [
        "autocustom_v0",
        "autodiscover_v0",
    ]


def _test_registration(
    *,
    env_id: str,
    key: str,
    artifact_slug: str | None = None,
    custom_module: str | None = None,
) -> EnvironmentRegistration:
    return EnvironmentRegistration(
        key=key,
        policy_module="fake.policy",
        status="planned",
        artifact_slug=artifact_slug,
        custom_module=custom_module,
        spec=EnvSpec(
            env_id=env_id,
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )


def test_registry_rejects_duplicate_env_keys_and_artifact_slugs(monkeypatch) -> None:
    registrations = {
        "first": _test_registration(
            env_id="DuplicateEnv-v0",
            key="duplicate_key",
            artifact_slug="shared_slug",
        ),
        "second": _test_registration(
            env_id="DuplicateEnv-v0",
            key="duplicate_key",
            artifact_slug="shared_slug",
        ),
    }
    monkeypatch.setattr(
        environment_module,
        "_iter_registration_module_names",
        lambda: tuple(registrations),
    )
    monkeypatch.setattr(
        environment_module,
        "_load_registration",
        lambda module_name: registrations[module_name],
    )

    with pytest.raises(ValueError) as exc_info:
        environment_module.discover_registrations()

    message = str(exc_info.value)
    assert "duplicate environment ids: DuplicateEnv-v0" in message
    assert "duplicate environment keys: duplicate_key" in message
    assert "duplicate artifact slugs: shared_slug" in message
    assert "duplicate custom module roots" not in message


def test_registry_rejects_duplicate_custom_module_roots(monkeypatch) -> None:
    registrations = {
        "first": _test_registration(
            env_id="FirstCustom-v0",
            key="first_custom",
            artifact_slug="first_custom",
            custom_module="hl_benchmark.custom_envs.shared_harness",
        ),
        "second": _test_registration(
            env_id="SecondCustom-v0",
            key="second_custom",
            artifact_slug="second_custom",
            custom_module="hl_benchmark.custom_envs.shared_harness",
        ),
    }
    monkeypatch.setattr(
        environment_module,
        "_iter_registration_module_names",
        lambda: tuple(registrations),
    )
    monkeypatch.setattr(
        environment_module,
        "_load_registration",
        lambda module_name: registrations[module_name],
    )

    with pytest.raises(ValueError) as exc_info:
        environment_module.discover_registrations()

    message = str(exc_info.value)
    assert "duplicate custom module roots: hl_benchmark.custom_envs.shared_harness" in message
    assert "duplicate environment ids" not in message
    assert "duplicate environment keys" not in message
    assert "duplicate artifact slugs" not in message


def test_custom_active_slimevolley_is_known_but_not_default_benchmark() -> None:
    assert planned_env_ids() == []
    assert PLANNED_ENV_SPECS == {}
    assert PLANNED_REGISTRATIONS == ()
    assert "SlimeVolley-v0" in KNOWN_ENV_SPECS
    assert "SlimeVolley-v0" not in ENV_SPECS
    registration = registration_for("SlimeVolley-v0")
    assert registration.key == "slimevolley"
    assert registration.status == "custom_active"
    assert [item.spec.env_id for item in CUSTOM_ACTIVE_REGISTRATIONS] == ["SlimeVolley-v0"]
    assert custom_env_ids() == ["SlimeVolley-v0"]
    assert list(CUSTOM_ENV_SPECS) == ["SlimeVolley-v0"]
    assert spec_for("SlimeVolley-v0").category == "competitive_control"


def test_custom_active_environments_have_harness_modules() -> None:
    for registration in CUSTOM_ACTIVE_REGISTRATIONS:
        assert registration.slug.isidentifier()
        assert registration.notes
        assert registration.custom_module_root
        importlib.import_module(registration.custom_module_root)
        importlib.import_module(f"{registration.custom_module_root}.evaluate")
        importlib.import_module(f"{registration.custom_module_root}.report")


def test_slimevolley_custom_env_bridge_preserves_legacy_harness() -> None:
    bridge = importlib.import_module("hl_benchmark.custom_envs.slimevolley")
    legacy = importlib.import_module("hl_benchmark.slimevolley")

    assert bridge.CUSTOM_VERIFY_EXTRA_COMMANDS == legacy.CUSTOM_VERIFY_EXTRA_COMMANDS
    for module_name in (
        "audit",
        "contact_diagnostics",
        "doctor",
        "evaluate",
        "final_eval",
        "generation_report",
        "performance_report",
        "protocol",
        "report",
        "search",
        "summarize",
        "tournament",
    ):
        module = importlib.import_module(f"hl_benchmark.custom_envs.slimevolley.{module_name}")
        assert callable(getattr(module, "main", None))


def test_setuptools_package_discovery_includes_environment_and_custom_roots() -> None:
    packages = set(find_packages(where=PROJECT_ROOT.as_posix(), include=["hl_benchmark*"]))

    assert {
        "hl_benchmark",
        "hl_benchmark.custom_envs",
        "hl_benchmark.environments",
        "hl_benchmark.policies",
        "hl_benchmark.slimevolley",
        "hl_benchmark.custom_envs.slimevolley",
    }.issubset(packages)


def test_runnable_environments_have_artifact_layout() -> None:
    for registration in (*ACTIVE_REGISTRATIONS, *CUSTOM_ACTIVE_REGISTRATIONS):
        artifact_root = experiment_dir(registration.spec.env_id)
        assert expected_experiment_dirs(registration.spec.env_id)[0] == artifact_root
        assert expected_experiment_files(registration.spec.env_id) == (
            artifact_root / "README.md",
        )
        assert expected_experiment_placeholder_files(registration.spec.env_id) == (
            artifact_root / "configs" / ".gitkeep",
            artifact_root / "results" / ".gitkeep",
            artifact_root / "reports" / ".gitkeep",
            artifact_root / "notes" / ".gitkeep",
        )
        assert missing_experiment_artifacts(registration.spec.env_id) == ()
        assert missing_experiment_dirs(registration.spec.env_id) == ()
        assert missing_experiment_files(registration.spec.env_id) == ()
        assert missing_experiment_placeholder_files(registration.spec.env_id) == ()
        assert experiment_artifact_layout_issues(registration.spec.env_id) == ()


def test_every_registration_has_a_policy_module_and_artifact_slug() -> None:
    seen_slugs: set[str] = set()
    seen_custom_modules: set[str] = set()
    for registration in ALL_REGISTRATIONS:
        assert registration.key
        assert registration.policy_module
        if registration.status != "planned":
            importlib.import_module(registration.policy_module)
        assert registration.slug not in seen_slugs
        seen_slugs.add(registration.slug)
        if registration.custom_module is not None or registration.status == "custom_active":
            assert registration.custom_module_root not in seen_custom_modules
            seen_custom_modules.add(registration.custom_module_root)


def test_registry_rows_expose_custom_module_roots() -> None:
    by_env = {row["env_id"]: row for row in registry_rows()}

    assert by_env["SlimeVolley-v0"]["custom_module"] == "hl_benchmark.custom_envs.slimevolley"
    assert by_env["CartPole-v1"]["custom_module"] is None


def test_custom_environment_dispatcher_exposes_standard_slimevolley_commands() -> None:
    registration = require_custom_registration("SlimeVolley-v0")
    assert registration.slug == "slimevolley"
    assert custom_command_module_name("SlimeVolley-v0", "summary") == (
        "hl_benchmark.custom_envs.slimevolley.summarize"
    )
    assert custom_command_module_name("SlimeVolley-v0", "eval") == (
        "hl_benchmark.custom_envs.slimevolley.evaluate"
    )
    assert custom_command_module_name("SlimeVolley-v0", "contact-diagnostics") == (
        "hl_benchmark.custom_envs.slimevolley.contact_diagnostics"
    )
    assert custom_command_module_name("SlimeVolley-v0", "protocol") == (
        "hl_benchmark.custom_envs.slimevolley.protocol"
    )

    commands = set(available_custom_commands("SlimeVolley-v0"))
    assert {
        "audit",
        "doctor",
        "evaluate",
        "final-eval",
        "report",
        "performance-report",
        "generation-report",
        "contact-diagnostics",
        "protocol",
        "search",
        "summary",
        "tournament",
        "verify",
    }.issubset(commands)
    extra_steps = custom_verify_extra_commands("SlimeVolley-v0")
    assert ("contact-diagnostics", ()) in extra_steps
    assert ("generation-report", ("--generation", "3")) in extra_steps
    assert ("protocol", ()) in extra_steps
    assert ("protocol", ("--generation", "3")) in extra_steps
    assert ("protocol", ("--generation", "4")) in extra_steps

    rendered = render_available_custom_commands("SlimeVolley-v0")
    assert "Custom environment commands: SlimeVolley-v0" in rendered
    assert "hl_benchmark.custom_envs.slimevolley" in rendered
    assert importlib.import_module("hl_benchmark.slimevolley.evaluate")
    assert "verify" in rendered


def test_custom_environment_dispatcher_rejects_non_custom_envs() -> None:
    with pytest.raises(ValueError, match="expected 'custom_active'"):
        require_custom_registration("CartPole-v1")
    with pytest.raises(ValueError, match="unregistered environment"):
        available_custom_commands("UnknownEnv-v0")


def test_custom_environment_dispatcher_uses_registration_slug_without_slimevolley_coupling(monkeypatch) -> None:
    fake_registration = EnvironmentRegistration(
        key="fake_custom",
        status="custom_active",
        policy_module="fake.policy",
        artifact_slug="fake_custom",
        custom_module="fakepkg_custom.harness",
        spec=EnvSpec(
            env_id="FakeCustom-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(custom_module, "registration_for", lambda _env_id: fake_registration)
    implemented_modules = {
        "fakepkg_custom.harness.evaluate",
        "fakepkg_custom.harness.summarize",
        "fakepkg_custom.harness.report",
        "fakepkg_custom.harness.performance_report",
        "fakepkg_custom.harness.audit",
    }
    monkeypatch.setattr(
        custom_module,
        "_module_available",
        lambda module_name: module_name in implemented_modules,
    )
    command_modules = {
        module_name: SimpleNamespace(main=lambda: None)
        for module_name in implemented_modules
    }
    monkeypatch.setattr(
        custom_module.importlib,
        "import_module",
        lambda module_name: command_modules[module_name],
    )

    assert custom_command_module_name("FakeCustom-v0", "summary") == (
        "fakepkg_custom.harness.summarize"
    )
    assert custom_command_module_name("FakeCustom-v0", "eval") == (
        "fakepkg_custom.harness.evaluate"
    )
    commands = set(available_custom_commands("FakeCustom-v0"))
    assert {"audit", "evaluate", "performance-report", "report", "summary", "verify"}.issubset(commands)
    assert "doctor" not in commands
    rendered = render_available_custom_commands("FakeCustom-v0")
    assert "Custom environment commands: FakeCustom-v0" in rendered
    assert "fakepkg_custom.harness" in rendered


def test_custom_environment_dispatcher_lists_verify_only_with_required_mains(monkeypatch) -> None:
    fake_registration = EnvironmentRegistration(
        key="fake_custom",
        status="custom_active",
        policy_module="fake.policy",
        artifact_slug="fake_custom",
        custom_module="fakepkg_custom.harness",
        spec=EnvSpec(
            env_id="FakeCustom-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(custom_module, "registration_for", lambda _env_id: fake_registration)
    implemented_modules = {
        "fakepkg_custom.harness.evaluate",
        "fakepkg_custom.harness.summarize",
        "fakepkg_custom.harness.report",
        "fakepkg_custom.harness.performance_report",
        "fakepkg_custom.harness.audit",
    }
    monkeypatch.setattr(
        custom_module,
        "_module_available",
        lambda module_name: module_name in implemented_modules,
    )
    modules = {
        "fakepkg_custom.harness.evaluate": SimpleNamespace(main=lambda: None),
        "fakepkg_custom.harness.summarize": SimpleNamespace(main=lambda: None),
        "fakepkg_custom.harness.report": SimpleNamespace(main=lambda: None),
        "fakepkg_custom.harness.performance_report": SimpleNamespace(main=lambda: None),
        "fakepkg_custom.harness.audit": SimpleNamespace(),
    }
    monkeypatch.setattr(
        custom_module.importlib,
        "import_module",
        lambda module_name: modules[module_name],
    )

    commands = set(available_custom_commands("FakeCustom-v0"))

    assert {"evaluate", "performance-report", "report", "summary"}.issubset(commands)
    assert "audit" not in commands
    assert "verify" not in commands

    modules["fakepkg_custom.harness.audit"] = SimpleNamespace(main=lambda: None)

    commands = set(available_custom_commands("FakeCustom-v0"))

    assert {"audit", "evaluate", "performance-report", "report", "summary", "verify"}.issubset(commands)


def test_custom_verify_runs_standard_chain_for_any_custom_env(monkeypatch, capsys) -> None:
    fake_registration = EnvironmentRegistration(
        key="fake_custom",
        status="custom_active",
        policy_module="fake.policy",
        artifact_slug="fake_custom",
        spec=EnvSpec(
            env_id="FakeCustom-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(custom_module, "registration_for", lambda _env_id: fake_registration)
    monkeypatch.setattr(
        custom_module,
        "environment_readiness_result",
        lambda env_id: {"pass_fail": "pass", "env_id": env_id},
    )
    monkeypatch.setattr(
        custom_module,
        "render_environment_readiness",
        lambda result: f"readiness {result['env_id']}\n",
    )
    monkeypatch.setattr(
        custom_module,
        "environment_readiness_summary",
        lambda: {"pass_fail": "pass", "checked_count": 1, "checked": [], "errors": []},
    )
    monkeypatch.setattr(
        custom_module,
        "render_environment_readiness_summary",
        lambda _result: "summary readiness\n",
    )
    monkeypatch.setattr(
        custom_module,
        "artifact_layout_result",
        lambda: {"pass_fail": "pass", "errors": []},
    )
    monkeypatch.setattr(
        custom_module,
        "env_results_dir",
        lambda _env_id: Path("/tmp/fake_custom/results"),
    )
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_run_custom_command(
        env_id: str,
        command: str,
        forwarded_args: Sequence[str] = (),
    ) -> str:
        assert env_id == "FakeCustom-v0"
        calls.append((command, tuple(forwarded_args)))
        return command

    monkeypatch.setattr(custom_module, "run_custom_command", fake_run_custom_command)

    custom_module.run_custom_verify("FakeCustom-v0")

    assert calls == [
        ("summary", ()),
        ("report", ()),
        ("performance-report", ()),
        ("audit", ("--output", "/tmp/fake_custom/results/audit_latest.json")),
    ]
    output = capsys.readouterr().out
    assert "readiness FakeCustom-v0" in output
    assert "summary readiness" in output
    assert "runnable artifact layout ok" in output


def test_custom_verify_runs_declared_extra_commands_in_order(monkeypatch) -> None:
    fake_registration = EnvironmentRegistration(
        key="fake_custom",
        status="custom_active",
        policy_module="fake.policy",
        artifact_slug="fake_custom",
        custom_module="fakepkg_extra.harness",
        spec=EnvSpec(
            env_id="FakeExtra-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(custom_module, "registration_for", lambda _env_id: fake_registration)
    monkeypatch.setattr(
        custom_module,
        "environment_readiness_result",
        lambda env_id: {"pass_fail": "pass", "env_id": env_id},
    )
    monkeypatch.setattr(custom_module, "render_environment_readiness", lambda _result: "")
    monkeypatch.setattr(
        custom_module,
        "environment_readiness_summary",
        lambda: {"pass_fail": "pass", "checked_count": 1, "checked": [], "errors": []},
    )
    monkeypatch.setattr(
        custom_module,
        "render_environment_readiness_summary",
        lambda _result: "",
    )
    monkeypatch.setattr(
        custom_module,
        "artifact_layout_result",
        lambda: {"pass_fail": "pass", "errors": []},
    )
    monkeypatch.setattr(
        custom_module,
        "env_results_dir",
        lambda _env_id: Path("/tmp/fake_extra/results"),
    )
    monkeypatch.setattr(
        custom_module.importlib,
        "import_module",
        lambda module_name: SimpleNamespace(
            CUSTOM_VERIFY_EXTRA_COMMANDS=(
                ("contact-diagnostics", ()),
                ("protocol", ("--generation", "3")),
            )
        ),
    )
    monkeypatch.setattr(
        custom_module,
        "available_custom_commands",
        lambda _env_id: ("summary", "report", "performance-report", "audit"),
    )
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_run_custom_command(
        env_id: str,
        command: str,
        forwarded_args: Sequence[str] = (),
    ) -> str:
        assert env_id == "FakeExtra-v0"
        calls.append((command, tuple(forwarded_args)))
        return command

    monkeypatch.setattr(custom_module, "run_custom_command", fake_run_custom_command)

    custom_module.run_custom_verify("FakeExtra-v0")

    assert calls == [
        ("summary", ()),
        ("contact-diagnostics", ()),
        ("protocol", ("--generation", "3")),
        ("report", ()),
        ("performance-report", ()),
        ("audit", ("--output", "/tmp/fake_extra/results/audit_latest.json")),
    ]


def test_custom_verify_extra_commands_rejects_malformed_declarations(monkeypatch) -> None:
    fake_registration = EnvironmentRegistration(
        key="fake_custom",
        status="custom_active",
        policy_module="fake.policy",
        artifact_slug="fake_custom",
        custom_module="fakepkg_bad.harness",
        spec=EnvSpec(
            env_id="FakeBad-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(custom_module, "registration_for", lambda _env_id: fake_registration)

    cases = [
        (("evaluate", ()), "not allowed"),
        (("unknown", ()), "unknown command"),
        (("protocol", "--generation"), "args must be a sequence of strings"),
        (("protocol", ("--generation", 3)), "args must be a sequence of strings"),
        ("protocol", r"must be \(command, args\)"),
    ]
    for declaration, message in cases:
        monkeypatch.setattr(
            custom_module.importlib,
            "import_module",
            lambda _module_name, declaration=declaration: SimpleNamespace(
                CUSTOM_VERIFY_EXTRA_COMMANDS=(declaration,)
            ),
        )
        with pytest.raises(ValueError, match=message):
            custom_verify_extra_commands("FakeBad-v0")


def test_check_env_json_output_exposes_readiness_gates(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.registry",
            "--check-env",
            "SlimeVolley-v0",
            "--format",
            "json",
        ],
    )

    registry_module.main()

    result = json.loads(capsys.readouterr().out)
    assert result["pass_fail"] == "pass"
    assert result["runnable"] is True
    assert result["promotion_ready"] is True
    assert result["promotion_blockers"] == []
    assert result["metadata_issues"] == []
    assert result["artifact_issues"] == []
    assert result["test_scaffold_issues"] == []
    assert result["planned_test_scaffold_issues"] == []
    assert result["runnable_test_scaffold_issues"] == []
    assert result["policy_import"]["pass_fail"] == "pass"
    assert result["policy_factory"]["pass_fail"] == "pass"
    assert result["policy_factory"]["candidate_configs_available"] is True
    assert result["required_policy_names"] == ["initial", "improved", "tuned"]
    assert result["missing_required_policy_names"] == []
    assert "improved" in result["policy_factory"]["supported_policy_names"]
    modules = {row["module"] for row in result["custom_harness_imports"]}
    assert "hl_benchmark.custom_envs.slimevolley.summarize" in modules
    assert "hl_benchmark.custom_envs.slimevolley.audit" in modules
    entrypoint_modules = {row["module"] for row in result["custom_command_entrypoints"]}
    assert "hl_benchmark.custom_envs.slimevolley.summarize" in entrypoint_modules
    assert "hl_benchmark.custom_envs.slimevolley.audit" in entrypoint_modules
    assert all(row["pass_fail"] == "pass" for row in result["custom_command_entrypoints"])


def test_policy_factory_contract_requires_local_candidate_configs(monkeypatch) -> None:
    fake_policy_module = SimpleNamespace(
        SUPPORTED_POLICY_NAMES=("initial",),
        make_policy=lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(
        registry_module.importlib,
        "import_module",
        lambda _module_name: fake_policy_module,
    )

    result = registry_module._policy_factory_check("fake.policy")

    assert result["pass_fail"] == "fail"
    assert result["supported_policy_names"] == ["initial"]
    assert result["candidate_configs_available"] is False
    assert "missing callable candidate_configs()" in result["error"]


def test_environment_readiness_fails_when_runnable_policy_names_are_incomplete(monkeypatch) -> None:
    fake_registration = EnvironmentRegistration(
        key="fake_active",
        status="active",
        policy_module="fake.policy",
        artifact_slug="fake_active",
        spec=EnvSpec(
            env_id="FakeActive-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "_policy_factory_check",
        lambda _module_name: {
            "module": "fake.policy",
            "pass_fail": "pass",
            "error": "",
            "supported_policy_names": ["initial"],
            "candidate_configs_available": True,
        },
    )

    result = registry_module.environment_readiness_result("FakeActive-v0")

    assert result["pass_fail"] == "fail"
    assert result["runnable"] is True
    assert result["required_policy_names"] == ["initial", "improved", "tuned"]
    assert result["missing_required_policy_names"] == ["improved", "tuned"]
    assert any(
        "runnable policy module missing required policy names: improved, tuned"
        in issue
        for issue in result["issues"]
    )
    rendered = registry_module.render_environment_readiness(result)
    assert "Required policies: fail" in rendered


def test_environment_readiness_result_checks_generic_and_custom_envs() -> None:
    cartpole = environment_readiness_result("CartPole-v1")
    assert cartpole["pass_fail"] == "pass"
    assert cartpole["registered"] is True
    assert cartpole["runnable"] is True
    assert cartpole["execution"] == "generic-eval-all"
    assert cartpole["artifact_dir"] == "experiments/cartpole"
    assert cartpole["policy_import"]["pass_fail"] == "pass"
    assert cartpole["policy_factory"]["pass_fail"] == "pass"
    assert cartpole["policy_factory"]["candidate_configs_available"] is True
    assert cartpole["required_policy_names"] == ["initial", "improved", "tuned"]
    assert cartpole["missing_required_policy_names"] == []
    assert cartpole["custom_module"] is None
    assert cartpole["policy_factory"]["supported_policy_names"] == ["improved", "initial", "tuned"]
    assert cartpole["metadata_issues"] == []
    assert cartpole["custom_harness_imports"] == []
    assert cartpole["custom_command_entrypoints"] == []

    slimevolley = environment_readiness_result("SlimeVolley-v0")
    assert slimevolley["pass_fail"] == "pass"
    assert slimevolley["runnable"] is True
    assert slimevolley["execution"] == "custom-harness"
    assert slimevolley["metadata_issues"] == []
    assert [row["module"] for row in slimevolley["custom_harness_imports"]] == [
        "hl_benchmark.custom_envs.slimevolley",
        "hl_benchmark.custom_envs.slimevolley.adapter",
        "hl_benchmark.custom_envs.slimevolley.evaluate",
        "hl_benchmark.custom_envs.slimevolley.search",
        "hl_benchmark.custom_envs.slimevolley.summarize",
        "hl_benchmark.custom_envs.slimevolley.report",
        "hl_benchmark.custom_envs.slimevolley.performance_report",
        "hl_benchmark.custom_envs.slimevolley.audit",
    ]
    assert all(row["pass_fail"] == "pass" for row in slimevolley["custom_harness_imports"])
    assert [row["module"] for row in slimevolley["custom_command_entrypoints"]] == [
        "hl_benchmark.custom_envs.slimevolley.evaluate",
        "hl_benchmark.custom_envs.slimevolley.search",
        "hl_benchmark.custom_envs.slimevolley.summarize",
        "hl_benchmark.custom_envs.slimevolley.report",
        "hl_benchmark.custom_envs.slimevolley.performance_report",
        "hl_benchmark.custom_envs.slimevolley.audit",
    ]
    assert all(row["pass_fail"] == "pass" for row in slimevolley["custom_command_entrypoints"])
    assert slimevolley["policy_factory"]["pass_fail"] == "pass"
    assert slimevolley["policy_factory"]["candidate_configs_available"] is True
    assert slimevolley["required_policy_names"] == ["initial", "improved", "tuned"]
    assert slimevolley["missing_required_policy_names"] == []
    assert "improved-v2" in slimevolley["policy_factory"]["supported_policy_names"]
    assert all(row["pass_fail"] == "pass" for row in slimevolley["scaffold_source_checks"])
    rendered_cartpole = render_environment_readiness(cartpole)
    assert "Artifact layout: pass" in rendered_cartpole
    assert "Custom module:" not in rendered_cartpole

    rendered = render_environment_readiness(slimevolley)
    assert "Environment readiness: pass" in rendered
    assert "Custom module: hl_benchmark.custom_envs.slimevolley" in rendered
    assert "Artifact layout: pass" in rendered
    assert "Policy factory: pass" in rendered
    assert "Required policies: pass" in rendered
    assert "Custom harness imports: pass" in rendered
    assert "Custom command entrypoints: pass" in rendered


def test_check_promotions_reports_aggregate_blockers(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    package_root = tmp_path / "fakepkg_promotions_gate"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_many.py").write_text(
        render_policy_scaffold_file("PlannedMany-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    test_scaffold_path = tmp_path / "tests" / "test_planned_many_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("PlannedMany-v0"),
        encoding="utf-8",
    )

    fake_registration = EnvironmentRegistration(
        key="planned_many",
        status="planned",
        policy_module="fakepkg_promotions_gate.policies.planned_many",
        artifact_slug="planned_many",
        spec=EnvSpec(
            env_id="PlannedMany-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(registry_module, "ALL_REGISTRATIONS", (fake_registration,))
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.registry",
            "--check-promotions",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        registry_module.main()

    assert exc_info.value.code == 1
    output = capsys.readouterr().out
    assert "Promotion readiness: fail" in output
    assert "Checked environments: 1" in output
    assert "Promotion ready: 0" in output
    assert "Promotion blocked: 1" in output
    assert "PlannedMany-v0: blocked (planned, experiments/planned_many)" in output
    assert "policy module missing required policy names before promotion" in output


def test_check_promotion_fails_for_scaffold_ready_planned_env(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    package_root = tmp_path / "fakepkg_promotion_gate"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_gate.py").write_text(
        render_policy_scaffold_file("PlannedPromotionGate-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    test_scaffold_path = tmp_path / "tests" / "test_planned_gate_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("PlannedPromotionGate-v0"),
        encoding="utf-8",
    )

    fake_registration = EnvironmentRegistration(
        key="planned_gate",
        status="planned",
        policy_module="fakepkg_promotion_gate.policies.planned_gate",
        artifact_slug="planned_gate",
        spec=EnvSpec(
            env_id="PlannedPromotionGate-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hl_benchmark.registry",
            "--check-promotion",
            "PlannedPromotionGate-v0",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        registry_module.main()

    assert exc_info.value.code == 1
    output = capsys.readouterr().out
    assert "Environment readiness: pass" in output
    assert "Promotion ready: False" in output
    assert "Promotion blockers:" in output
    assert "policy module missing required policy names before promotion" in output


def test_planned_scaffold_readiness_allows_placeholders_until_promotion(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_planned"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_env.py").write_text(
        render_policy_scaffold_file("PlannedEnv-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="planned_env",
        status="planned",
        policy_module="fakepkg_planned.policies.planned_env",
        artifact_slug="planned_env",
        spec=EnvSpec(
            env_id="PlannedEnv-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    test_scaffold_path = tmp_path / "tests" / "test_planned_env_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("PlannedEnv-v0"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )

    result = registry_module.environment_readiness_result("PlannedEnv-v0")

    assert result["pass_fail"] == "pass"
    assert result["runnable"] is False
    assert result["promotion_ready"] is False
    assert any("EnvSpec.category" in issue for issue in result["promotion_blockers"])
    assert any("improved, tuned" in issue for issue in result["promotion_blockers"])
    assert any("must replace planned test scaffold" in issue for issue in result["promotion_blockers"])
    assert any("scaffold markers remain before promotion" in issue for issue in result["promotion_blockers"])
    assert result["execution"] == "not-runnable"
    assert result["metadata_issues"] == []
    assert result["artifact_issues"] == []
    assert result["custom_harness_imports"] == []
    assert result["custom_command_entrypoints"] == []
    assert result["scaffold_source_checks"] == []
    assert result["policy_import"]["pass_fail"] == "pass"
    rendered = registry_module.render_environment_readiness(result)
    assert "Artifact layout: pass" in rendered
    assert "Test scaffold: pass" in rendered
    assert "Promotion ready: False" in rendered
    assert "Promotion blockers:" in rendered
    assert "Metadata: not checked until promotion" in rendered


def test_planned_custom_readiness_fails_when_artifact_scaffold_is_missing(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_missing_artifacts"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_missing.py").write_text(
        render_policy_scaffold_file("PlannedMissing-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="planned_missing",
        status="planned",
        policy_module="fakepkg_missing_artifacts.policies.planned_missing",
        artifact_slug="planned_missing",
        spec=EnvSpec(
            env_id="PlannedMissing-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    test_scaffold_path = tmp_path / "tests" / "test_planned_missing_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("PlannedMissing-v0"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: ("missing experiments/planned_missing/README.md",),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )

    result = registry_module.environment_readiness_result("PlannedMissing-v0")

    assert result["pass_fail"] == "fail"
    assert result["runnable"] is False
    assert result["metadata_issues"] == []
    assert result["test_scaffold_issues"] == []
    assert result["artifact_issues"] == ["missing experiments/planned_missing/README.md"]
    assert result["issues"] == ["missing experiments/planned_missing/README.md"]
    rendered = registry_module.render_environment_readiness(result)
    assert "Artifact layout: fail" in rendered
    assert "Metadata: not checked until promotion" in rendered


def test_planned_custom_registration_requires_harness_scaffold_imports(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_planned_custom"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_custom.py").write_text(
        render_policy_scaffold_file("PlannedCustom-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="planned_custom",
        status="planned",
        policy_module="fakepkg_planned_custom.policies.planned_custom",
        artifact_slug="planned_custom",
        custom_module="fakepkg_planned_custom.custom_envs.planned_custom",
        spec=EnvSpec(
            env_id="PlannedCustom-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    test_scaffold_path = tmp_path / "tests" / "test_planned_custom_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("PlannedCustom-v0"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )

    result = registry_module.environment_readiness_result("PlannedCustom-v0")

    assert result["pass_fail"] == "fail"
    assert result["runnable"] is False
    assert result["execution"] == "not-runnable"
    assert result["custom_module"] == "fakepkg_planned_custom.custom_envs.planned_custom"
    assert len(result["custom_harness_imports"]) == 8
    assert result["custom_harness_imports"][0]["module"] == (
        "fakepkg_planned_custom.custom_envs.planned_custom"
    )
    assert all(
        import_result["pass_fail"] == "fail"
        for import_result in result["custom_harness_imports"]
    )
    assert len(result["custom_command_entrypoints"]) == 6
    assert all(
        entrypoint["pass_fail"] == "fail"
        for entrypoint in result["custom_command_entrypoints"]
    )
    assert result["scaffold_source_checks"] == []
    assert any("custom harness import failed" in issue for issue in result["issues"])
    assert any("custom command main() missing" in issue for issue in result["issues"])
    rendered = registry_module.render_environment_readiness(result)
    assert "Custom module: fakepkg_planned_custom.custom_envs.planned_custom" in rendered
    assert "Artifact layout: pass" in rendered
    assert "Custom harness imports: fail" in rendered
    assert "Custom command entrypoints: fail" in rendered
    assert "Metadata: not checked until promotion" in rendered

def test_environment_readiness_fails_on_promoted_scaffold_metadata(tmp_path, monkeypatch) -> None:
    package_root = tmp_path / "fakepkg_metadata"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "example_env.py").write_text(
        "class CleanPolicy:\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="example_env",
        policy_module="fakepkg_metadata.policies.example_env",
        artifact_slug="example_env",
        spec=EnvSpec(
            env_id="ExampleEnv-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )

    result = registry_module.environment_readiness_result("ExampleEnv-v0")

    assert result["pass_fail"] == "fail"
    assert result["policy_import"]["pass_fail"] == "pass"
    assert result["custom_harness_imports"] == []
    assert result["scaffold_source_checks"][0]["pass_fail"] == "pass"
    assert len(result["metadata_issues"]) >= 7
    assert any("EnvSpec.category" in issue for issue in result["metadata_issues"])
    assert any("EnvSpec.episode_length" in issue for issue in result["metadata_issues"])
    assert any("known_failure_modes[0]" in issue for issue in result["metadata_issues"])
    rendered = registry_module.render_environment_readiness(result)
    assert "Metadata: fail" in rendered


def test_environment_readiness_fails_when_custom_command_main_missing(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_no_main"
    policy_root = package_root / "policies"
    harness_root = package_root / "harness"
    policy_root.mkdir(parents=True)
    harness_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (harness_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "example_env.py").write_text(
        "class CleanPolicy:\n    pass\n",
        encoding="utf-8",
    )
    (harness_root / "search.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="example_env",
        status="custom_active",
        policy_module="fakepkg_no_main.policies.example_env",
        artifact_slug="example_env",
        spec=EnvSpec(
            env_id="ExampleEnv-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "_custom_harness_modules",
        lambda _slug: ("fakepkg_no_main.harness.search",),
    )
    monkeypatch.setattr(
        registry_module,
        "_custom_command_modules",
        lambda _slug: ("fakepkg_no_main.harness.search",),
    )

    result = registry_module.environment_readiness_result("ExampleEnv-v0")

    assert result["pass_fail"] == "fail"
    assert result["custom_harness_imports"][0]["pass_fail"] == "pass"
    assert result["custom_command_entrypoints"] == [
        {
            "module": "fakepkg_no_main.harness.search",
            "pass_fail": "fail",
            "error": "missing callable main()",
        }
    ]
    assert any("custom command main() missing" in issue for issue in result["issues"])
    rendered = registry_module.render_environment_readiness(result)
    assert "Custom command entrypoints: fail" in rendered


def test_environment_readiness_fails_on_promoted_scaffold_sources(tmp_path, monkeypatch) -> None:
    package_root = tmp_path / "fakepkg"
    policy_root = package_root / "policies"
    harness_root = package_root / "harness"
    policy_root.mkdir(parents=True)
    harness_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (harness_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "example_env.py").write_text(
        render_policy_scaffold_file("ExampleEnv-v0"),
        encoding="utf-8",
    )
    (harness_root / "evaluate.py").write_text(
        render_custom_harness_file("ExampleEnv-v0", "evaluate.py"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="example_env",
        status="custom_active",
        policy_module="fakepkg.policies.example_env",
        artifact_slug="example_env",
        spec=EnvSpec(
            env_id="ExampleEnv-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=0.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "_custom_harness_modules",
        lambda _slug: ("fakepkg.harness.evaluate",),
    )
    monkeypatch.setattr(
        registry_module,
        "_custom_command_modules",
        lambda _slug: ("fakepkg.harness.evaluate",),
    )

    result = registry_module.environment_readiness_result("ExampleEnv-v0")

    assert result["pass_fail"] == "fail"
    assert result["policy_import"]["pass_fail"] == "pass"
    assert result["custom_harness_imports"][0]["pass_fail"] == "pass"
    assert any("scaffold markers remain" in issue for issue in result["issues"])
    by_module = {row["module"]: row for row in result["scaffold_source_checks"]}
    assert by_module["fakepkg.policies.example_env"]["pass_fail"] == "fail"
    assert "define scalar search space" in by_module["fakepkg.policies.example_env"]["markers"]
    assert by_module["fakepkg.harness.evaluate"]["pass_fail"] == "fail"
    rendered = registry_module.render_environment_readiness(result)
    assert "Scaffold markers: fail" in rendered


def test_environment_readiness_fails_when_promoted_test_scaffold_remains(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_promoted_test_scaffold"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "promoted_test.py").write_text(
        "SUPPORTED_POLICY_NAMES = ('initial', 'improved', 'tuned')\n"
        "def make_policy(*_args, **_kwargs):\n"
        "    return object()\n"
        "def candidate_configs(*_args, **_kwargs):\n"
        "    return []\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    test_scaffold_path = tmp_path / "tests" / "test_promoted_test_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("PromotedTest-v0"),
        encoding="utf-8",
    )

    fake_registration = EnvironmentRegistration(
        key="promoted_test",
        status="active",
        policy_module="fakepkg_promoted_test_scaffold.policies.promoted_test",
        artifact_slug="promoted_test",
        spec=EnvSpec(
            env_id="PromotedTest-v0",
            category="test",
            observation_summary="test observation",
            action_summary="test action",
            reward_interpretation="test reward",
            episode_length=10,
            success_target=1.0,
            initial_policy="test policy",
            known_failure_modes=("test failure",),
            docs_url="https://example.invalid/promoted-test",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )

    result = registry_module.environment_readiness_result("PromotedTest-v0")

    assert result["pass_fail"] == "fail"
    assert result["runnable"] is True
    assert result["metadata_issues"] == []
    assert result["policy_factory"]["pass_fail"] == "pass"
    expected_issues = [
        f"{test_scaffold_path.as_posix()} still contains planned test scaffold marker 'pytest.mark.skip'",
        f"{test_scaffold_path.as_posix()} still contains planned test scaffold marker 'TODO: replace'",
        f"{test_scaffold_path.as_posix()} still contains planned test scaffold marker 'make check-promotion'",
        f"{test_scaffold_path.as_posix()} still contains planned test scaffold marker 'make check-planned-envs'",
        f"{test_scaffold_path.as_posix()} still contains planned test scaffold marker 'test_planned_readiness_gate_before_promotion'",
    ]
    assert result["test_scaffold_issues"] == expected_issues
    assert result["planned_test_scaffold_issues"] == []
    assert result["runnable_test_scaffold_issues"] == expected_issues
    assert any("still contains planned test scaffold" in issue for issue in result["issues"])
    rendered = render_environment_readiness(result)
    assert "Test scaffold: fail" in rendered


def test_environment_readiness_result_reports_unknown_env() -> None:
    result = environment_readiness_result("UnknownEnv-v0")
    assert result["pass_fail"] == "fail"
    assert result["registered"] is False
    assert "unregistered environment" in " ".join(result["issues"])


def test_environment_readiness_summary_checks_all_runnable_envs() -> None:
    result = environment_readiness_summary()
    assert result["pass_fail"] == "pass"
    assert result["checked_count"] == len(ACTIVE_REGISTRATIONS) + len(
        CUSTOM_ACTIVE_REGISTRATIONS
    )
    assert result["planned_count"] == len(PLANNED_REGISTRATIONS)
    assert result["planned"] == []
    checked_envs = {row["env_id"] for row in result["checked"]}
    assert checked_envs == {
        registration.spec.env_id
        for registration in (*ACTIVE_REGISTRATIONS, *CUSTOM_ACTIVE_REGISTRATIONS)
    }
    assert result["errors"] == []
    rendered = render_environment_readiness_summary(result)
    assert "Runnable environment readiness: pass" in rendered
    assert "Planned environments: 0" in rendered
    assert "SlimeVolley-v0: pass" in rendered


def test_environment_readiness_summary_lists_planned_envs_without_gating_pass_fail(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_summary"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_summary.py").write_text(
        render_policy_scaffold_file("PlannedSummary-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="planned_summary",
        status="planned",
        policy_module="fakepkg_summary.policies.planned_summary",
        artifact_slug="planned_summary",
        custom_module="fakepkg_summary.custom_envs.planned_summary",
        spec=EnvSpec(
            env_id="PlannedSummary-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(registry_module, "runnable_registrations", lambda: ())
    monkeypatch.setattr(
        registry_module,
        "PLANNED_REGISTRATIONS",
        (fake_registration,),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )

    result = registry_module.environment_readiness_summary()

    assert result["pass_fail"] == "pass"
    assert result["checked_count"] == 0
    assert result["checked"] == []
    assert result["planned_count"] == 1
    assert result["planned"][0]["env_id"] == "PlannedSummary-v0"
    assert result["planned"][0]["execution"] == "not-runnable"
    assert result["planned"][0]["pass_fail"] == "fail"
    assert result["errors"] == []
    rendered = registry_module.render_environment_readiness_summary(result)
    assert "Checked environments: 0" in rendered
    assert "Planned environments: 1" in rendered
    assert "Planned registry entries:" in rendered
    assert "PlannedSummary-v0: fail (not-runnable, experiments/planned_summary)" in rendered


def test_planned_environment_readiness_summary_is_a_strict_planned_gate(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_planned_gate"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_gate.py").write_text(
        render_policy_scaffold_file("PlannedGate-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    fake_registration = EnvironmentRegistration(
        key="planned_gate",
        status="planned",
        policy_module="fakepkg_planned_gate.policies.planned_gate",
        artifact_slug="planned_gate",
        spec=EnvSpec(
            env_id="PlannedGate-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "PLANNED_REGISTRATIONS",
        (fake_registration,),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    test_scaffold_path = tmp_path / "tests" / "test_planned_gate_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("PlannedGate-v0"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: ("missing experiments/planned_gate/README.md",),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )

    result = planned_environment_readiness_summary()

    assert result["pass_fail"] == "fail"
    assert result["checked_count"] == 1
    assert result["checked"][0]["env_id"] == "PlannedGate-v0"
    assert result["checked"][0]["artifact_issues"] == [
        "missing experiments/planned_gate/README.md"
    ]
    assert result["errors"] == [
        "PlannedGate-v0: missing experiments/planned_gate/README.md"
    ]
    rendered = render_planned_environment_readiness_summary(result)
    assert "Planned environment readiness: fail" in rendered
    assert "Checked planned environments: 1" in rendered
    assert "PlannedGate-v0: fail (not-runnable, experiments/planned_gate)" in rendered


def test_planned_environment_readiness_summary_passes_when_no_planned_envs() -> None:
    result = planned_environment_readiness_summary()

    assert result["pass_fail"] == "pass"
    assert result["checked_count"] == len(PLANNED_REGISTRATIONS)
    assert result["checked"] == []
    rendered = render_planned_environment_readiness_summary(result)
    assert "Planned environment readiness: pass" in rendered
    assert "No planned environments registered" in rendered


def test_planned_environment_readiness_fails_when_test_scaffold_contract_is_invalid(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_invalid_test_scaffold"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_bad_test.py").write_text(
        render_policy_scaffold_file("PlannedBadTest-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    test_scaffold_path = tmp_path / "tests" / "test_planned_bad_test_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text("# arbitrary file is not enough\n", encoding="utf-8")

    fake_registration = EnvironmentRegistration(
        key="planned_bad_test",
        status="planned",
        policy_module="fakepkg_invalid_test_scaffold.policies.planned_bad_test",
        artifact_slug="planned_bad_test",
        spec=EnvSpec(
            env_id="PlannedBadTest-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )

    result = registry_module.environment_readiness_result("PlannedBadTest-v0")

    assert result["pass_fail"] == "fail"
    assert result["artifact_issues"] == []
    expected_issues = [
        f"{test_scaffold_path.as_posix()} missing planned test scaffold marker 'pytest.mark.skip'",
        f"{test_scaffold_path.as_posix()} missing planned test scaffold marker 'make check-planned-envs'",
        f"{test_scaffold_path.as_posix()} missing planned test scaffold marker 'test_planned_readiness_gate_before_promotion'",
        f'{test_scaffold_path.as_posix()} missing planned test scaffold marker \'ENV_ID = "PlannedBadTest-v0"\'',
        f'{test_scaffold_path.as_posix()} missing planned test scaffold marker \'MODULE_SLUG = "plannedbadtest_v0"\'',
        f"{test_scaffold_path.as_posix()} missing planned test scaffold marker 'make check-env ENV=PlannedBadTest-v0'",
        f"{test_scaffold_path.as_posix()} missing planned test scaffold marker 'make check-promotion ENV=PlannedBadTest-v0'",
    ]
    assert result["test_scaffold_issues"] == expected_issues
    assert result["planned_test_scaffold_issues"] == expected_issues
    assert result["runnable_test_scaffold_issues"] == []
    rendered = render_environment_readiness(result)
    assert "Test scaffold: fail" in rendered


def test_planned_environment_readiness_fails_when_test_scaffold_identity_mismatches(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_wrong_test_identity"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_wrong_identity.py").write_text(
        render_policy_scaffold_file("PlannedWrongIdentity-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    test_scaffold_path = tmp_path / "tests" / "test_planned_wrong_identity_scaffold.py"
    test_scaffold_path.parent.mkdir(parents=True)
    test_scaffold_path.write_text(
        render_environment_test_scaffold_file("DifferentEnv-v0"),
        encoding="utf-8",
    )

    fake_registration = EnvironmentRegistration(
        key="planned_wrong_identity",
        status="planned",
        policy_module="fakepkg_wrong_test_identity.policies.planned_wrong_identity",
        artifact_slug="planned_wrong_identity",
        spec=EnvSpec(
            env_id="PlannedWrongIdentity-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: test_scaffold_path,
    )

    result = registry_module.environment_readiness_result("PlannedWrongIdentity-v0")

    assert result["pass_fail"] == "fail"
    assert result["test_scaffold_issues"] == [
        f'{test_scaffold_path.as_posix()} missing planned test scaffold marker \'ENV_ID = "PlannedWrongIdentity-v0"\'',
        f'{test_scaffold_path.as_posix()} missing planned test scaffold marker \'MODULE_SLUG = "plannedwrongidentity_v0"\'',
        f"{test_scaffold_path.as_posix()} missing planned test scaffold marker 'make check-env ENV=PlannedWrongIdentity-v0'",
        f"{test_scaffold_path.as_posix()} missing planned test scaffold marker 'make check-promotion ENV=PlannedWrongIdentity-v0'",
    ]


def test_planned_environment_readiness_fails_when_test_scaffold_is_missing(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_missing_test_scaffold"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_no_test.py").write_text(
        render_policy_scaffold_file("PlannedNoTest-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    missing_test_path = tmp_path / "tests" / "test_planned_no_test_scaffold.py"

    fake_registration = EnvironmentRegistration(
        key="planned_no_test",
        status="planned",
        policy_module="fakepkg_missing_test_scaffold.policies.planned_no_test",
        artifact_slug="planned_no_test",
        spec=EnvSpec(
            env_id="PlannedNoTest-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: missing_test_path,
    )

    result = registry_module.environment_readiness_result("PlannedNoTest-v0")

    assert result["pass_fail"] == "fail"
    assert result["runnable"] is False
    assert result["artifact_issues"] == []
    assert result["test_scaffold_issues"] == [f"missing {missing_test_path.as_posix()}"]
    assert result["metadata_issues"] == []
    assert result["custom_harness_imports"] == []
    assert result["custom_command_entrypoints"] == []
    rendered = render_environment_readiness(result)
    assert "Test scaffold: fail" in rendered
    assert "Metadata: not checked until promotion" in rendered


def test_planned_environment_readiness_summary_reports_missing_test_scaffold(
    tmp_path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "fakepkg_missing_summary_test"
    policy_root = package_root / "policies"
    policy_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "__init__.py").write_text("", encoding="utf-8")
    (policy_root / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    (policy_root / "planned_summary_no_test.py").write_text(
        render_policy_scaffold_file("PlannedSummaryNoTest-v0"),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    missing_test_path = tmp_path / "tests" / "test_planned_summary_no_test_scaffold.py"

    fake_registration = EnvironmentRegistration(
        key="planned_summary_no_test",
        status="planned",
        policy_module="fakepkg_missing_summary_test.policies.planned_summary_no_test",
        artifact_slug="planned_summary_no_test",
        spec=EnvSpec(
            env_id="PlannedSummaryNoTest-v0",
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(registry_module, "PLANNED_REGISTRATIONS", (fake_registration,))
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda _env_id: (),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda _env_id: missing_test_path,
    )

    result = planned_environment_readiness_summary()

    assert result["pass_fail"] == "fail"
    assert result["checked_count"] == 1
    row = result["checked"][0]
    assert row["env_id"] == "PlannedSummaryNoTest-v0"
    assert row["test_scaffold_issues"] == [f"missing {missing_test_path.as_posix()}"]
    assert result["errors"] == [
        f"PlannedSummaryNoTest-v0: missing {missing_test_path.as_posix()}"
    ]
    rendered = render_planned_environment_readiness_summary(result)
    assert "Planned environment readiness: fail" in rendered
    assert "PlannedSummaryNoTest-v0: fail" in rendered
    assert f"missing {missing_test_path.as_posix()}" in rendered


def test_new_generic_scaffold_passes_planned_readiness_gate(
    tmp_path,
    monkeypatch,
) -> None:
    env_id = "GenericProbe-v0"
    package_dir = tmp_path / "hl_benchmark"
    experiments_dir = tmp_path / "experiments"
    tests_dir = tmp_path / "tests"

    scaffold_experiment_artifacts(env_id, experiments_dir=experiments_dir)
    scaffold_environment_code(env_id, package_dir=package_dir)
    scaffold_environment_tests(env_id, tests_dir=tests_dir)

    package_dir.mkdir(exist_ok=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "policies" / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "policies" / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    for module_name in tuple(sys.modules):
        if module_name == "hl_benchmark" or module_name.startswith("hl_benchmark."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)

    fake_registration = EnvironmentRegistration(
        key="genericprobe_v0",
        status="planned",
        policy_module="hl_benchmark.policies.genericprobe_v0",
        artifact_slug="genericprobe_v0",
        spec=EnvSpec(
            env_id=env_id,
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "PLANNED_REGISTRATIONS",
        (fake_registration,),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda checked_env_id: experiment_artifact_layout_issues(
            checked_env_id,
            experiments_dir=experiments_dir,
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda checked_env_id: environment_test_scaffold_path(
            checked_env_id,
            tests_dir=tests_dir,
        ),
    )

    result = planned_environment_readiness_summary()

    assert result["pass_fail"] == "pass"
    assert result["checked_count"] == 1
    row = result["checked"][0]
    assert row["env_id"] == env_id
    assert row["status"] == "planned"
    assert row["execution"] == "not-runnable"
    assert row["runnable"] is False
    assert row["artifact_issues"] == []
    assert row["test_scaffold_issues"] == []
    assert row["metadata_issues"] == []
    assert row["custom_module"] is None
    assert row["custom_harness_imports"] == []
    assert row["custom_command_entrypoints"] == []
    assert row["scaffold_source_checks"] == []
    assert row["policy_factory"]["pass_fail"] == "pass"
    assert row["policy_factory"]["candidate_configs_available"] is True
    assert row["policy_factory"]["supported_policy_names"] == ["initial"]
    rendered = render_planned_environment_readiness_summary(result)
    assert "Planned environment readiness: pass" in rendered
    assert "GenericProbe-v0: pass (not-runnable, experiments/genericprobe_v0)" in rendered


def test_new_custom_scaffold_passes_planned_readiness_gate(
    tmp_path,
    monkeypatch,
) -> None:
    env_id = "ProbeEnv-v0"
    package_dir = tmp_path / "hl_benchmark"
    experiments_dir = tmp_path / "experiments"
    tests_dir = tmp_path / "tests"

    scaffold_experiment_artifacts(env_id, experiments_dir=experiments_dir)
    scaffold_environment_code(
        env_id,
        package_dir=package_dir,
        include_custom_module=True,
    )
    scaffold_custom_harness_code(env_id, package_dir=package_dir)
    scaffold_environment_tests(env_id, tests_dir=tests_dir)

    package_dir.mkdir(exist_ok=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "policies" / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "policies" / "base.py").write_text(
        "class BasePolicy:\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    for module_name in tuple(sys.modules):
        if module_name == "hl_benchmark" or module_name.startswith("hl_benchmark."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)

    fake_registration = EnvironmentRegistration(
        key="probeenv_v0",
        status="planned",
        policy_module="hl_benchmark.policies.probeenv_v0",
        artifact_slug="probeenv_v0",
        custom_module="hl_benchmark.custom_envs.probeenv_v0",
        spec=EnvSpec(
            env_id=env_id,
            category="todo",
            observation_summary="TODO: record observation space and state semantics.",
            action_summary="TODO: record action space and action semantics.",
            reward_interpretation="TODO: record reward semantics and termination rules.",
            episode_length=0,
            success_target=0.0,
            initial_policy="TODO: describe the initial transparent heuristic.",
            known_failure_modes=(
                "TODO: record known failure modes before promotion.",
            ),
            docs_url="TODO",
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "PLANNED_REGISTRATIONS",
        (fake_registration,),
    )
    monkeypatch.setattr(
        registry_module,
        "registration_for",
        lambda _env_id: fake_registration,
    )
    monkeypatch.setattr(
        registry_module,
        "experiment_artifact_layout_issues",
        lambda checked_env_id: experiment_artifact_layout_issues(
            checked_env_id,
            experiments_dir=experiments_dir,
        ),
    )
    monkeypatch.setattr(
        registry_module,
        "environment_test_scaffold_path",
        lambda checked_env_id: environment_test_scaffold_path(
            checked_env_id,
            tests_dir=tests_dir,
        ),
    )

    result = planned_environment_readiness_summary()

    assert result["pass_fail"] == "pass"
    assert result["checked_count"] == 1
    row = result["checked"][0]
    assert row["env_id"] == env_id
    assert row["status"] == "planned"
    assert row["execution"] == "not-runnable"
    assert row["runnable"] is False
    assert row["artifact_issues"] == []
    assert row["test_scaffold_issues"] == []
    assert row["metadata_issues"] == []
    assert row["custom_module"] == "hl_benchmark.custom_envs.probeenv_v0"
    expected_harness_modules = [
        "hl_benchmark.custom_envs.probeenv_v0",
        "hl_benchmark.custom_envs.probeenv_v0.adapter",
        "hl_benchmark.custom_envs.probeenv_v0.evaluate",
        "hl_benchmark.custom_envs.probeenv_v0.search",
        "hl_benchmark.custom_envs.probeenv_v0.summarize",
        "hl_benchmark.custom_envs.probeenv_v0.report",
        "hl_benchmark.custom_envs.probeenv_v0.performance_report",
        "hl_benchmark.custom_envs.probeenv_v0.audit",
    ]
    assert [
        import_result["module"]
        for import_result in row["custom_harness_imports"]
    ] == expected_harness_modules
    assert all(
        import_result["pass_fail"] == "pass"
        for import_result in row["custom_harness_imports"]
    )
    expected_command_modules = [
        "hl_benchmark.custom_envs.probeenv_v0.evaluate",
        "hl_benchmark.custom_envs.probeenv_v0.search",
        "hl_benchmark.custom_envs.probeenv_v0.summarize",
        "hl_benchmark.custom_envs.probeenv_v0.report",
        "hl_benchmark.custom_envs.probeenv_v0.performance_report",
        "hl_benchmark.custom_envs.probeenv_v0.audit",
    ]
    assert [
        entrypoint["module"]
        for entrypoint in row["custom_command_entrypoints"]
    ] == expected_command_modules
    assert all(
        entrypoint["pass_fail"] == "pass"
        for entrypoint in row["custom_command_entrypoints"]
    )
    assert row["scaffold_source_checks"] == []
    assert row["policy_factory"]["pass_fail"] == "pass"
    assert row["policy_factory"]["candidate_configs_available"] is True
    assert row["policy_factory"]["supported_policy_names"] == ["initial"]
    rendered = render_planned_environment_readiness_summary(result)
    assert "Planned environment readiness: pass" in rendered
    assert "ProbeEnv-v0: pass (not-runnable, experiments/probeenv_v0)" in rendered


def test_artifact_layout_result_is_machine_readable() -> None:
    result = artifact_layout_result()
    assert result["pass_fail"] == "pass"
    assert result["checked_count"] == len(ACTIVE_REGISTRATIONS) + len(
        CUSTOM_ACTIVE_REGISTRATIONS
    )
    by_env = {row["env_id"]: row for row in result["checked"]}
    cartpole = by_env["CartPole-v1"]
    slimevolley = by_env["SlimeVolley-v0"]
    assert cartpole["artifact_dir"] == "experiments/cartpole"
    assert cartpole["required_dirs"] == [
        "experiments/cartpole",
        "experiments/cartpole/configs",
        "experiments/cartpole/results",
        "experiments/cartpole/reports",
        "experiments/cartpole/notes",
    ]
    assert cartpole["required_files"] == ["experiments/cartpole/README.md"]
    assert cartpole["required_placeholder_files"] == [
        "experiments/cartpole/configs/.gitkeep",
        "experiments/cartpole/results/.gitkeep",
        "experiments/cartpole/reports/.gitkeep",
        "experiments/cartpole/notes/.gitkeep",
    ]
    assert "experiments/cartpole/results/trials.jsonl" not in cartpole["required_files"]
    assert slimevolley["status"] == "custom_active"
    assert all(row["pass_fail"] == "pass" for row in result["checked"])
    assert result["errors"] == []


def test_runnable_artifact_layout_check_passes() -> None:
    assert artifact_layout_errors() == []


def test_registry_report_distinguishes_generic_and_custom_environments() -> None:
    rows = registry_rows()
    by_env = {row["env_id"]: row for row in rows}
    assert by_env["CartPole-v1"]["execution"] == "generic-eval-all"
    assert by_env["SlimeVolley-v0"]["execution"] == "custom-harness"
    assert by_env["SlimeVolley-v0"]["artifact_dir"] == "experiments/slimevolley"
    table = render_registry_table(rows)
    assert "| Custom Module |" in table
    assert "| SlimeVolley-v0 | custom_active | custom-harness | slimevolley | competitive_control | hl_benchmark.custom_envs.slimevolley | experiments/slimevolley |" in table
    assert "| CartPole-v1 | active | generic-eval-all | cartpole | classic_control | - | experiments/cartpole |" in table


def test_package_exports_custom_environment_helpers() -> None:
    assert "EnvironmentRegistration" in hl_benchmark.__all__
    assert "registration_for" in hl_benchmark.__all__
    assert hl_benchmark.EnvironmentRegistration is EnvironmentRegistration
    assert hl_benchmark.custom_env_ids() == ["SlimeVolley-v0"]
    assert hl_benchmark.planned_env_ids() == []
    assert hl_benchmark.PLANNED_ENV_SPECS == {}
    assert "SlimeVolley-v0" in hl_benchmark.CUSTOM_ENV_SPECS
    assert hl_benchmark.spec_for("SlimeVolley-v0").category == "competitive_control"
    registration = hl_benchmark.registration_for("SlimeVolley-v0")
    assert registration.slug == "slimevolley"
    assert registration.custom_module_root == "hl_benchmark.custom_envs.slimevolley"


def test_readme_documents_current_add_environment_contract() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    for required_text in [
        "make scaffold-env ENV=<EnvId>",
        "make scaffold-generic-env ENV=NewEnv-v0",
        "make scaffold-custom-env ENV=<EnvId>",
        "make slimevolley-generation4-protocol",
        "this creates the artifact tree, planned registration/policy files",
        "leaving `REGISTRATION.custom_module` unset",
        "this sets `REGISTRATION.custom_module` to `hl_benchmark.custom_envs.<env_slug>`",
        "auto-discovered `REGISTRATION`",
        "suite_order",
        "artifact slugs unique",
        "SUPPORTED_POLICY_NAMES",
        "`initial`, `improved`, and `tuned`",
        "candidate_configs()",
        "should not edit `hl_benchmark/policies/factory.py`",
        "`hl_benchmark/search.py`",
        "planned_env_ids()",
        "adapter.py",
        "evaluate.py",
        "search.py",
        "summarize.py",
        "report.py",
        "performance_report.py",
        "audit.py",
        "Keep new environments `planned`",
        "promotion gates for",
        "`custom_active` environments, not scaffold checks",
        "metadata_issues",
        "artifact_issues",
        "test_scaffold_issues",
        "planned_test_scaffold_issues",
        "runnable_test_scaffold_issues",
        "promotion_ready",
        "promotion_blockers",
        "missing_required_policy_names",
        "missing_required_policy_names",
        "artifact scaffold",
        "missing skipped pytest scaffold files",
        "mismatched scaffold identity markers",
        'make eval-env ENV=CartPole-v1 POLICY=initial SPLIT=smoke ARGS="--env-artifacts"',
        'make search-env ENV=CartPole-v1 MAX_CANDIDATES=8 ARGS="--env-artifacts"',
        'make rl-baseline ENV=CartPole-v1 SPLIT=smoke TRAIN_STEPS=100 ARGS="--env-artifacts"',
        "make summary-env ENV=CartPole-v1",
        "make report-env ENV=CartPole-v1",
        "make audit-env ENV=CartPole-v1",
        'make eval-env ... ARGS="--env-artifacts"',
        'make search-env ... ARGS="--env-artifacts"',
        "per-environment root",
        "planned custom envs with `REGISTRATION.custom_module`",
        "importable placeholder harness modules",
        "callable command",
        'make check-env ENV=<EnvId> ARGS="--format json"',
        "make custom-verify ENV=<EnvId>",
        "optional",
        "`CUSTOM_VERIFY_EXTRA_COMMANDS`, and audit gates",
        "performance_report",
        "default non-evaluation, non-regeneration gate",
        "Custom environment summary/report/audit and declared",
        "diagnostics/protocol regeneration remains",
        "generation-2, generation-3, and generation-4 protocol artifacts",
        "CUSTOM_VERIFY_EXTRA_COMMANDS",
        "make check-planned-envs",
        "make check-promotion ENV=<EnvId>",
        "make check-promotions",
        "make verify",
        "docs/pr_review_note.md",
    ]:
        assert required_text in readme


def test_pr_review_note_documents_review_map_and_guardrails() -> None:
    note = (PROJECT_ROOT / "docs" / "pr_review_note.md").read_text(
        encoding="utf-8"
    )
    for required_text in [
        "Environment Registry and SlimeVolley Expansion",
        "hl_benchmark/environments/",
        "hl_benchmark/custom_envs/",
        "hl_benchmark/slimevolley/",
        "experiments/<env_slug>/",
        "Review Order",
        "make verify",
        "make slimevolley-verify",
        "make check-planned-envs",
        "make verify`: pass",
        "148 pytest tests",
        "make slimevolley-verify`: pass",
        "requirements_audit_status_counts",
        "requirements_audit_partial_rows",
        "requirements_audit_completion_state",
        "requirements_audit_completion_recommendation",
        "requirements_audit_partial_row_details",
        "requirements_audit_partial_row_classifications",
        "experiments/slimevolley/reports/requirements_audit.md",
        "intentionally non-evaluative",
        "does not run new holdout evaluation",
        "contact diagnostics and generation protocol/report artifacts",
        "planned_env_ids()",
        "make check-promotion",
        "make check-promotions",
        "skipped pytest scaffold files",
        "matching ENV_ID/MODULE_SLUG",
        "callable custom command entrypoints",
        "real harness implementation remain promotion-time gates",
        "generated skipped test scaffold was not replaced",
        "Holdout rows already exist",
        "generation-3",
        "generation-4",
        "noncanonical historical change types",
    ]:
        assert required_text in note


def test_custom_environment_template_documents_required_contract() -> None:
    template = (PROJECT_ROOT / "docs" / "custom_environment_template.md").read_text(
        encoding="utf-8"
    )
    for required_text in [
        "custom_active",
        "custom_env_ids()",
        "planned_env_ids()",
        "trials.jsonl",
        "Generated after evaluation/report commands",
        "results/audit_latest.json",
        "generated by custom-verify or audit --output",
        "planned custom env can omit `results/audit_latest.json`",
        "reports/requirements_audit.md",
        "configs/.gitkeep",
        "make scaffold-env ENV=<EnvId>",
        "make scaffold-env-code ENV=<EnvId>",
        "make scaffold-env-tests ENV=<EnvId>",
        "make scaffold-generic-env ENV=<EnvId>",
        "make scaffold-custom-env ENV=<EnvId>",
        "This target sets `REGISTRATION.custom_module`",
        "During the planned phase",
        "Do not treat custom command dispatch as a passing gate",
        "`make custom-run` and `make custom-verify` require a",
        "Before promoting to `custom_active`",
        "Do not add `custom-verify` to the default `make verify` target",
        "custom verification",
        "harness-declared `CUSTOM_VERIFY_EXTRA_COMMANDS`",
        "non-evaluation",
        "diagnostics, protocol regeneration, or replay summaries",
        "Custom verify extras reject evaluation, search, tournament, and final-holdout commands",
        "remain an explicit per-environment step",
        "make custom-run ENV=<EnvId> CUSTOM_COMMAND=summary",
        "planned registry-entry visibility",
        "make check-planned-envs",
        "strict planned scaffold gate",
        "artifact, skipped-test identity, policy",
        "custom-harness scaffold gate",
        "planned custom registrations",
        "make verify",
        "artifact_issues",
        "test_scaffold_issues",
        "planned_test_scaffold_issues",
        "runnable_test_scaffold_issues",
        "promotion_ready",
        "promotion_blockers",
        "scaffold/TODO markers",
        "unreplaced",
        "skipped test scaffolds",
        "generated skipped test scaffold",
        "scaffold metadata",
        "SUPPORTED_POLICY_NAMES",
        "`initial`, `improved`, and `tuned`",
        "make_policy()",
        "candidate_configs()",
        "auto-discovers",
        "suite_order",
        "hl_benchmark/custom_envs/<env_slug>/evaluate.py",
        "hl_benchmark/custom_envs/<env_slug>/search.py",
        "hl_benchmark/custom_envs/<env_slug>/summarize.py",
        "hl_benchmark/custom_envs/<env_slug>/performance_report.py",
        "hl_benchmark/custom_envs/<env_slug>/audit.py",
        "experiments/<env_slug>/",
        "Holdout guard",
    ]:
        assert required_text in template


def test_adding_environment_guide_documents_generic_and_custom_paths() -> None:
    guide = (PROJECT_ROOT / "docs" / "adding_environment.md").read_text(
        encoding="utf-8"
    )
    for required_text in [
        "status `active`",
        "status `custom_active`",
        "status `planned`",
        "hl_benchmark/custom_envs/<env_slug>/evaluate.py",
        "hl_benchmark/custom_envs/<env_slug>/search.py",
        "hl_benchmark/custom_envs/<env_slug>/summarize.py",
        "hl_benchmark/custom_envs/<env_slug>/performance_report.py",
        "hl_benchmark/custom_envs/<env_slug>/audit.py",
        "experiments/<env_slug>/",
        "scaffold-created shape",
        "Generated after evaluation/report commands",
        "reports/requirements_audit.md",
        "make list-envs",
        "make check-env-layout",
        "make check-env ENV=<EnvId>",
        "make check-promotion ENV=<EnvId>",
        "metadata_issues",
        "artifact_issues",
        "test_scaffold_issues",
        "validates the planned artifact scaffold",
        "missing the skipped pytest scaffold",
        "mismatched scaffold identity markers",
        "sets `REGISTRATION.custom_module` without",
        "importable placeholder harness modules",
        "placeholder harness modules to import",
        "custom command entrypoints",
        "SUPPORTED_POLICY_NAMES",
        "`initial`, `improved`, and `tuned`",
        "make_policy()",
        "candidate_configs()",
        "`hl_benchmark/search.py`",
        "planned_env_ids()",
        "custom_env_ids()",
        "benchmark_env_ids()",
        "make check-envs",
        "make check-planned-envs",
        "count",
        "names of planned registry",
        "make check-planned-envs",
        "make verify",
        "strict planned-scaffold gate",
        "make custom-run ENV=<EnvId>",
        "make custom-verify ENV=<EnvId>",
        "make scaffold-env ENV=<EnvId>",
        "make scaffold-env-code ENV=<EnvId>",
        "make scaffold-env-tests ENV=<EnvId>",
        "make scaffold-generic-env ENV=<EnvId>",
        "make scaffold-custom-env ENV=<EnvId>",
        "one-shot generic scaffold target",
        "It leaves `REGISTRATION.custom_module` unset",
        "planned registration/policy files with `REGISTRATION.custom_module`",
        "Promotion Checks",
        "planned environments are not runnable",
        "Before promoting a generic Gymnasium environment to `active`",
        'make eval-env ENV=<EnvId> POLICY=initial SPLIT=smoke ARGS="--env-artifacts"',
        'make search-env ENV=<EnvId> MAX_CANDIDATES=8 ARGS="--env-artifacts"',
        'make rl-baseline ENV=<EnvId> SPLIT=smoke TRAIN_STEPS=100 ARGS="--env-artifacts"',
        "make summary-env ENV=<EnvId>",
        "make report-env ENV=<EnvId>",
        "make audit-env ENV=<EnvId>",
        'ARGS="--env-artifacts"',
        "Before promoting a custom environment to `custom_active`",
        "Only then run custom",
        "commands:",
        "regenerates custom summary, report, and audit artifacts",
        "default CI remains a",
        "non-regeneration gate",
        "Scaffolding commands such as `make scaffold-env-code`",
        "scaffold/TODO markers",
        ".gitkeep",
        "every runnable",
        "Do not optimize or debug on holdout seeds",
    ]:
        assert required_text in guide


def test_experiments_readme_distinguishes_scaffold_and_generated_artifacts() -> None:
    readme = (PROJECT_ROOT / "experiments" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Scaffold-created per-environment shape" in readme
    assert "Generated after evaluation/report commands" in readme
    assert "results/trials.jsonl" in readme
    assert "results/audit_latest.json" in readme
    assert "reports/final_report.md" in readme
    assert "reports/requirements_audit.md" in readme
    assert "hl_benchmark/custom_envs/<env_slug>/" in readme
    assert "SlimeVolley is registered through `hl_benchmark/custom_envs/slimevolley/`" in readme


def test_slimevolley_readme_documents_test_status_provenance() -> None:
    readme = (
        PROJECT_ROOT
        / "experiments"
        / "slimevolley"
        / "README.md"
    ).read_text(encoding="utf-8")
    assert "For new ledger-producing runs" in readme
    assert "--tests-pass-fail pass" in readme
    assert "--tests-pass-fail not_recorded" in readme
    assert "`tests_pass_fail`" in readme
    assert "trial_amendments.jsonl" in readme


def test_slimevolley_readme_manifest_lists_custom_env_bridge() -> None:
    readme = (
        PROJECT_ROOT
        / "experiments"
        / "slimevolley"
        / "README.md"
    ).read_text(encoding="utf-8")
    assert "## Artifact Manifest" in readme
    assert "`hl_benchmark/custom_envs/slimevolley/`" in readme
    assert "Registry-facing custom harness bridge" in readme
    assert "requirements_audit_status_counts" in readme
    assert "requirements_audit_partial_rows" in readme
    assert "requirements_audit_completion_state" in readme
    assert "requirements_audit_completion_recommendation" in readme
    assert "requirements_audit_partial_row_details" in readme
    assert "requirements_audit_partial_row_classifications" in readme
    assert "make check-env ENV=SlimeVolley-v0" in readme


def test_slimevolley_requirements_audit_documents_coverage_and_limits() -> None:
    requirements_audit = (
        PROJECT_ROOT
        / "experiments"
        / "slimevolley"
        / "reports"
        / "requirements_audit.md"
    ).read_text(encoding="utf-8")
    for required_text in [
        "SlimeVolley Requirement Coverage Audit",
        "Coverage Matrix",
        "Machine-Readable Completion State",
        "requirements_audit_completion_state",
        "requirements_audit_completion_recommendation",
        "eligible_for_completion_audit",
        "trial_amendments.jsonl",
        "append-only `tests_pass_fail=not_recorded` metadata amendments",
        "Working repository",
        "Initial handwritten heuristic",
        "Agent-maintained heuristic policy versions",
        "Packaged RNN comparator",
        "Required command surface",
        "Heuristic-system improvement loop",
        "Replay and diagnostics",
        "Baseline comparison set",
        "documented pretrained neural/RNN comparator. No local PPO/DQN/self-play training baseline was run. | Satisfied |",
        "Holdout seeds `1000..1049`",
        "generation-2 holdout seeds `4000..4049`",
        "generation-3 holdout seeds `7000..7049`",
        "not deep-RL comparable",
        "predeclared generation-4 protocol",
        "raw generation-1 rows still predate `tests_pass_fail`",
        "148 pytest tests",
    ]:
        assert required_text in requirements_audit


def test_slimevolley_verify_target_runs_readiness_gates() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    target = makefile.split("slimevolley-verify:\n", 1)[1]
    target = target.split("\nslimevolley-eval:\n", 1)[0]
    assert "--check-env SlimeVolley-v0" in target
    assert "--check-envs" in target
    assert "--check-artifacts" in target
    assert "hl_benchmark.custom_envs.slimevolley.protocol" in target


def test_makefile_exposes_generic_custom_environment_targets() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "verify:" in makefile
    assert "--check-envs" in makefile
    assert "--check-planned" in makefile
    assert "--check-artifacts" in makefile
    assert "-m pytest tests" in makefile
    assert "scaffold-env-code:" in makefile
    assert "--scaffold-env-code $(ENV)" in makefile
    assert "scaffold-env-tests:" in makefile
    assert "--scaffold-tests $(ENV)" in makefile
    assert "scaffold-generic-env:" in makefile
    assert "hl_benchmark.artifacts --scaffold-env $(ENV) --scaffold-env-code $(ENV) --scaffold-tests $(ENV)" in makefile
    assert "scaffold-custom-env:" in makefile
    assert "--scaffold-env-code $(ENV) --custom-registration --scaffold-custom-code $(ENV)" in makefile
    assert "--scaffold-tests $(ENV)" in makefile
    assert "hl_benchmark.evaluate --env $(ENV) --policy $(POLICY) --split $(SPLIT) $(ARGS)" in makefile
    assert "hl_benchmark.evaluate --all --split $(SPLIT) $(ARGS)" in makefile
    assert "search-env:" in makefile
    assert "summary:" in makefile
    assert "summary-env:" in makefile
    assert "report-env:" in makefile
    assert "audit-env:" in makefile
    assert "hl_benchmark.artifact_audit --env $(ENV) --write-latest $(ARGS)" in makefile
    assert "hl_benchmark.search --env $(ENV) --split dev --max-candidates $(MAX_CANDIDATES) $(ARGS)" in makefile
    assert "hl_benchmark.search --all --split dev --max-candidates $(MAX_CANDIDATES) $(ARGS)" in makefile
    assert "hl_benchmark.rl_baseline --env $(ENV) --split $(SPLIT) --algo $(ALGO) --train-steps $(TRAIN_STEPS) $(ARGS)" in makefile
    assert "hl_benchmark.summarize --env $(ENV) --env-artifacts $(ARGS)" in makefile
    assert "hl_benchmark.report --env $(ENV) --env-artifacts $(ARGS)" in makefile
    assert "custom-run:" in makefile
    assert "hl_benchmark.custom --env $(ENV) $(CUSTOM_COMMAND)" in makefile
    assert "custom-verify:" in makefile
    assert "hl_benchmark.custom --env $(ENV) verify" in makefile
    assert "check-promotion:" in makefile
    assert "--check-promotion $(ENV) $(ARGS)" in makefile
    assert "check-promotions:" in makefile
    assert "--check-promotions $(ARGS)" in makefile
    assert "check-planned-envs:" in makefile
    assert "--check-planned $(ARGS)" in makefile


def test_verify_target_remains_non_evaluative() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    target = makefile.split("verify:\n", 1)[1]
    target = target.split("\nlist-envs:\n", 1)[0]

    assert "--check-envs" in target
    assert "--check-planned" in target
    assert "--check-artifacts" in target
    assert "-m pytest tests" in target
    for forbidden in (
        "hl_benchmark.evaluate",
        "hl_benchmark.search",
        "hl_benchmark.report",
        "hl_benchmark.artifact_audit",
        "--check-promotions",
        "hl_benchmark.custom",
        "hl_benchmark.deepdive_report",
        "hl_benchmark.rl_baseline",
        "hl_benchmark.slimevolley",
        "--write-latest",
        "custom-verify",
        "custom-run",
        "--split",
        "--policy",
        "--max-candidates",
        "--train-steps",
    ):
        assert forbidden not in target


def test_artifact_layout_issues_catch_missing_placeholders(tmp_path) -> None:
    scaffold_experiment_artifacts(
        "ExampleEnv-v0",
        experiments_dir=tmp_path / "experiments",
    )
    keep_path = tmp_path / "experiments" / "exampleenv_v0" / "notes" / ".gitkeep"
    keep_path.unlink()

    issues = experiment_artifact_layout_issues(
        "ExampleEnv-v0",
        experiments_dir=tmp_path / "experiments",
    )
    assert issues == (f"missing {keep_path.as_posix()}",)


def test_experiment_readme_identity_check_catches_stale_readme(tmp_path) -> None:
    scaffold_experiment_artifacts(
        "ExampleEnv-v0",
        experiments_dir=tmp_path / "experiments",
    )
    assert experiment_readme_identity_issues(
        "ExampleEnv-v0",
        experiments_dir=tmp_path / "experiments",
    ) == ()

    readme_path = tmp_path / "experiments" / "exampleenv_v0" / "README.md"
    readme_path.write_text("# Copied README\n\nWrong environment.\n", encoding="utf-8")
    issues = experiment_readme_identity_issues(
        "ExampleEnv-v0",
        experiments_dir=tmp_path / "experiments",
    )
    joined = " ".join(issues)
    assert "ExampleEnv-v0" in joined
    assert "experiments/exampleenv_v0" in joined


def test_generated_scaffold_sources_are_syntax_valid(tmp_path) -> None:
    package_dir = tmp_path / "hl_benchmark"
    scaffold_environment_code("123 Odd-Env.v0", package_dir=package_dir)
    scaffold_custom_harness_code("123 Odd-Env.v0", package_dir=package_dir)

    generated_paths = [
        *expected_environment_code_files("123 Odd-Env.v0", package_dir=package_dir),
        *expected_custom_harness_files("123 Odd-Env.v0", package_dir=package_dir),
    ]
    assert generated_paths
    for generated_path in generated_paths:
        py_compile.compile(generated_path, doraise=True)

    registration_text = generated_paths[0].read_text(encoding="utf-8")
    assert 'key="env_123_odd_env_v0"' in registration_text
    assert 'policy_module="hl_benchmark.policies.env_123_odd_env_v0"' in registration_text
    assert 'custom_module=' not in registration_text


def test_scaffold_generic_env_cli_creates_complete_contract(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    env_id = "CliGenericProbe-v0"
    experiments_dir = tmp_path / "experiments"
    package_dir = tmp_path / "hl_benchmark"
    tests_dir = tmp_path / "tests"
    argv = [
        "hl_benchmark.artifacts",
        "--scaffold-env",
        env_id,
        "--scaffold-env-code",
        env_id,
        "--scaffold-tests",
        env_id,
        "--experiments-dir",
        str(experiments_dir),
        "--package-dir",
        str(package_dir),
        "--tests-dir",
        str(tests_dir),
        "--format",
        "json",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    artifacts_module.main()

    payload = json.loads(capsys.readouterr().out)
    scaffolds = payload["scaffolds"]
    assert [row["label"] for row in scaffolds] == [
        "Experiment artifact scaffold",
        "Environment registration/policy scaffold",
        "Environment test scaffold",
    ]
    assert {row["env_id"] for row in scaffolds} == {env_id}
    assert {row["slug"] for row in scaffolds} == {"cligenericprobe_v0"}

    experiment_root = experiments_dir / "cligenericprobe_v0"
    registration_path = package_dir / "environments" / "cligenericprobe_v0.py"
    policy_path = package_dir / "policies" / "cligenericprobe_v0.py"
    harness_root = package_dir / "custom_envs" / "cligenericprobe_v0"
    test_path = tests_dir / "test_cligenericprobe_v0_scaffold.py"
    assert (experiment_root / "README.md").is_file()
    assert registration_path.is_file()
    assert policy_path.is_file()
    assert test_path.is_file()
    assert not harness_root.exists()
    registration_text = registration_path.read_text(encoding="utf-8")
    test_text = test_path.read_text(encoding="utf-8")
    assert 'status="planned"' in registration_text
    assert 'policy_module="hl_benchmark.policies.cligenericprobe_v0"' in registration_text
    assert "custom_module=" not in registration_text
    assert "PROMOTION_CHECKS" in test_text
    assert "make check-promotion ENV=CliGenericProbe-v0" in test_text
    assert "make check-planned-envs" in test_text
    assert "results/audit_latest.json" in (
        experiment_root / "README.md"
    ).read_text(encoding="utf-8")
    for generated_path in (registration_path, policy_path, test_path):
        py_compile.compile(generated_path, doraise=True)

    monkeypatch.setattr(sys, "argv", argv)
    artifacts_module.main()
    second_payload = json.loads(capsys.readouterr().out)
    assert all(not row["created"] for row in second_payload["scaffolds"])
    assert all(row["existing"] for row in second_payload["scaffolds"])


def test_scaffold_custom_env_cli_creates_complete_contract(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    env_id = "CliProbe-v0"
    experiments_dir = tmp_path / "experiments"
    package_dir = tmp_path / "hl_benchmark"
    tests_dir = tmp_path / "tests"
    argv = [
        "hl_benchmark.artifacts",
        "--scaffold-env",
        env_id,
        "--scaffold-env-code",
        env_id,
        "--custom-registration",
        "--scaffold-custom-code",
        env_id,
        "--scaffold-tests",
        env_id,
        "--experiments-dir",
        str(experiments_dir),
        "--package-dir",
        str(package_dir),
        "--tests-dir",
        str(tests_dir),
        "--format",
        "json",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    artifacts_module.main()

    payload = json.loads(capsys.readouterr().out)
    scaffolds = payload["scaffolds"]
    assert [row["label"] for row in scaffolds] == [
        "Experiment artifact scaffold",
        "Environment registration/policy scaffold",
        "Custom harness code scaffold",
        "Environment test scaffold",
    ]
    assert {row["env_id"] for row in scaffolds} == {env_id}
    assert {row["slug"] for row in scaffolds} == {"cliprobe_v0"}

    experiment_root = experiments_dir / "cliprobe_v0"
    registration_path = package_dir / "environments" / "cliprobe_v0.py"
    policy_path = package_dir / "policies" / "cliprobe_v0.py"
    harness_root = package_dir / "custom_envs" / "cliprobe_v0"
    test_path = tests_dir / "test_cliprobe_v0_scaffold.py"
    assert (experiment_root / "README.md").is_file()
    assert registration_path.is_file()
    assert policy_path.is_file()
    assert test_path.is_file()
    assert 'custom_module="hl_benchmark.custom_envs.cliprobe_v0"' in (
        registration_path.read_text(encoding="utf-8")
    )
    assert "--output" in (harness_root / "audit.py").read_text(encoding="utf-8")
    assert "--output" not in (harness_root / "evaluate.py").read_text(encoding="utf-8")
    for generated_path in (
        registration_path,
        policy_path,
        test_path,
        *expected_custom_harness_files(env_id, package_dir=package_dir),
    ):
        py_compile.compile(generated_path, doraise=True)

    monkeypatch.setattr(sys, "argv", argv)
    artifacts_module.main()
    second_payload = json.loads(capsys.readouterr().out)
    assert all(not row["created"] for row in second_payload["scaffolds"])
    assert all(row["existing"] for row in second_payload["scaffolds"])


def test_scaffold_environment_code_uses_planned_registration_and_policy(tmp_path) -> None:
    package_dir = tmp_path / "hl_benchmark"
    result = scaffold_environment_code("ExampleEnv-v0", package_dir=package_dir)
    registration_path = package_dir / "environments" / "exampleenv_v0.py"
    policy_path = package_dir / "policies" / "exampleenv_v0.py"

    assert result["env_id"] == "ExampleEnv-v0"
    assert result["slug"] == "exampleenv_v0"
    assert result["root"] == package_dir.as_posix()
    assert (
        environment_registration_path("ExampleEnv-v0", package_dir=package_dir)
        == registration_path
    )
    assert (
        policy_scaffold_path("ExampleEnv-v0", package_dir=package_dir)
        == policy_path
    )
    assert expected_environment_code_files("ExampleEnv-v0", package_dir=package_dir) == (
        registration_path,
        policy_path,
    )
    assert len(result["created"]) == 2

    registration_text = registration_path.read_text(encoding="utf-8")
    policy_text = policy_path.read_text(encoding="utf-8")
    assert registration_text == render_environment_registration_file("ExampleEnv-v0")
    assert policy_text == render_policy_scaffold_file("ExampleEnv-v0")
    assert 'status="planned"' in registration_text
    assert 'policy_module="hl_benchmark.policies.exampleenv_v0"' in registration_text
    assert 'custom_module=' not in registration_text
    assert result["include_custom_module"] is False
    assert "suite_order=1000" in registration_text
    assert "class ExampleEnvV0Policy" in policy_text
    assert "SUPPORTED_POLICY_NAMES" in policy_text
    assert "def candidate_configs(" in policy_text
    assert "define scalar search space for ExampleEnv-v0" in policy_text
    assert "def make_policy(" in policy_text
    assert "NotImplementedError" in policy_text

    rendered = render_scaffold_result(
        dict(result, label="Environment registration/policy scaffold")
    )
    assert "REGISTRATION.custom_module: not included" in rendered

    second = scaffold_environment_code("ExampleEnv-v0", package_dir=package_dir)
    assert second["created"] == []
    assert len(second["existing"]) == 2


def test_scaffold_environment_code_can_emit_custom_registration(tmp_path) -> None:
    package_dir = tmp_path / "hl_benchmark"
    result = scaffold_environment_code(
        "ExampleEnv-v0",
        package_dir=package_dir,
        include_custom_module=True,
    )
    registration_path = package_dir / "environments" / "exampleenv_v0.py"

    registration_text = registration_path.read_text(encoding="utf-8")
    assert result["include_custom_module"] is True
    assert 'custom_module="hl_benchmark.custom_envs.exampleenv_v0"' in registration_text
    assert registration_text == render_environment_registration_file(
        "ExampleEnv-v0",
        include_custom_module=True,
    )
    rendered = render_scaffold_result(
        dict(result, label="Environment registration/policy scaffold")
    )
    assert "REGISTRATION.custom_module: included" in rendered


def test_scaffold_environment_tests_uses_skipped_pytest_contract(tmp_path) -> None:
    tests_dir = tmp_path / "tests"
    result = scaffold_environment_tests("ExampleEnv-v0", tests_dir=tests_dir)
    test_path = tests_dir / "test_exampleenv_v0_scaffold.py"

    assert result["env_id"] == "ExampleEnv-v0"
    assert result["slug"] == "exampleenv_v0"
    assert result["root"] == tests_dir.as_posix()
    assert (
        environment_test_scaffold_path("ExampleEnv-v0", tests_dir=tests_dir)
        == test_path
    )
    assert result["created"] == [test_path.as_posix()]

    text = test_path.read_text(encoding="utf-8")
    assert text == render_environment_test_scaffold_file("ExampleEnv-v0")
    assert 'ENV_ID = "ExampleEnv-v0"' in text
    assert 'MODULE_SLUG = "exampleenv_v0"' in text
    assert "PROMOTION_CHECKS = (" in text
    assert "make check-env ENV=ExampleEnv-v0" in text
    assert 'make check-env ENV=ExampleEnv-v0 ARGS=\"--format json\"' in text
    assert "make check-promotion ENV=ExampleEnv-v0" in text
    assert "make check-planned-envs" in text
    assert "pytest.mark.skip" in text
    assert "test_registry_metadata_contract" in text
    assert "test_planned_readiness_gate_before_promotion" in text
    assert "test_fixed_seed_smoke_evaluation_and_ledger_schema" in text
    assert "test_report_generation_and_holdout_guardrails" in text
    py_compile.compile(test_path, doraise=True)

    second = scaffold_environment_tests("ExampleEnv-v0", tests_dir=tests_dir)
    assert second["created"] == []
    assert second["existing"] == [test_path.as_posix()]


def test_scaffold_custom_harness_code_uses_standard_layout(tmp_path) -> None:
    package_dir = tmp_path / "hl_benchmark"
    result = scaffold_custom_harness_code("ExampleEnv-v0", package_dir=package_dir)
    root = package_dir / "custom_envs" / "exampleenv_v0"

    assert result["env_id"] == "ExampleEnv-v0"
    assert result["slug"] == "exampleenv_v0"
    assert result["root"] == root.as_posix()
    assert custom_harness_module_slug("ExampleEnv-v0") == "exampleenv_v0"
    assert custom_harness_dir("ExampleEnv-v0", package_dir=package_dir) == root
    scaffold_names = {
        path.name
        for path in expected_custom_harness_files(
            "ExampleEnv-v0",
            package_dir=package_dir,
        )
    }
    assert scaffold_names == set(CUSTOM_HARNESS_FILES)
    assert custom_harness_parent_init_path(package_dir=package_dir) == (
        package_dir / "custom_envs" / "__init__.py"
    )
    assert len(result["created"]) == len(CUSTOM_HARNESS_FILES) + 1
    assert (package_dir / "custom_envs" / "__init__.py").read_text(
        encoding="utf-8"
    ) == render_custom_harness_parent_init_file()

    init_text = (root / "__init__.py").read_text(encoding="utf-8")
    adapter_text = (root / "adapter.py").read_text(encoding="utf-8")
    evaluate_text = (root / "evaluate.py").read_text(encoding="utf-8")
    audit_text = (root / "audit.py").read_text(encoding="utf-8")
    assert 'ENV_ID = "ExampleEnv-v0"' in init_text
    assert "TODO: implement dependency check" in adapter_text
    assert "TODO: implement exampleenv_v0.evaluate" in evaluate_text
    assert "--output" not in evaluate_text
    assert "--output" in audit_text
    assert "machine-readable audit JSON output" in audit_text
    assert render_custom_harness_file("ExampleEnv-v0", "audit.py") == audit_text

    second = scaffold_custom_harness_code("ExampleEnv-v0", package_dir=package_dir)
    assert second["created"] == []
    assert len(second["existing"]) == len(CUSTOM_HARNESS_FILES) + 1


def test_scaffold_custom_harness_code_creates_importable_package(tmp_path, monkeypatch) -> None:
    package_dir = tmp_path / "hl_benchmark"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    scaffold_custom_harness_code("ExampleEnv-v0", package_dir=package_dir)
    monkeypatch.syspath_prepend(str(tmp_path))
    for module_name in tuple(sys.modules):
        if module_name == "hl_benchmark" or module_name.startswith("hl_benchmark."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)

    module = importlib.import_module("hl_benchmark.custom_envs.exampleenv_v0.evaluate")

    assert module.ENV_ID == "ExampleEnv-v0"
    assert callable(module.main)


def test_scaffold_experiment_artifacts_uses_standard_layout(tmp_path) -> None:
    result = scaffold_experiment_artifacts(
        "ExampleEnv-v0",
        experiments_dir=tmp_path / "experiments",
    )
    root = tmp_path / "experiments" / "exampleenv_v0"
    assert result["env_id"] == "ExampleEnv-v0"
    assert result["slug"] == "exampleenv_v0"
    assert root.is_dir()
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert readme == render_experiment_readme("ExampleEnv-v0")
    assert "Environment ID: `ExampleEnv-v0`" in readme
    assert "Artifact root: `experiments/exampleenv_v0/`" in readme
    assert "Scaffold-created layout" in readme
    assert "Generated after evaluation/report/audit commands" in readme
    assert "results/trials.jsonl" in readme
    assert "results/summary.csv" in readme
    assert "results/audit_latest.json" in readme
    assert "reports/final_report.md" in readme
    assert "registered as `planned`" in readme
    assert "Do not delete failed ledger rows" in readme
    for child in ("configs", "results", "reports", "notes"):
        assert (root / child).is_dir()
        assert (root / child / ".gitkeep").read_text(encoding="utf-8") == "keep\n"

    second = scaffold_experiment_artifacts(
        "ExampleEnv-v0",
        experiments_dir=tmp_path / "experiments",
    )
    assert second["created"] == []
    assert len(second["existing"]) >= 10


def test_per_environment_artifact_paths_are_stable() -> None:
    assert slug_for_env_id("CartPole-v1") == "cartpole"
    assert slug_for_env_id("SlimeVolley-v0") == "slimevolley"
    assert env_ledger_path("SlimeVolley-v0").as_posix().endswith(
        "experiments/slimevolley/results/trials.jsonl"
    )
    assert [path.name for path in expected_experiment_dirs("SlimeVolley-v0")] == [
        "slimevolley",
        "configs",
        "results",
        "reports",
        "notes",
    ]
    assert slug_for_env_id("CustomEnv-v12") == "customenv_v12"
