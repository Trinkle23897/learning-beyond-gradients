"""Artifact path helpers for aggregate and per-environment runs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .environments import registration_for


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_RESULTS_DIR = PROJECT_ROOT / "results"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
BENCHMARK_PACKAGE_DIR = PROJECT_ROOT / "hl_benchmark"
TESTS_DIR = PROJECT_ROOT / "tests"
REQUIRED_EXPERIMENT_SUBDIRS = ("configs", "results", "reports", "notes")
REQUIRED_EXPERIMENT_FILES = ("README.md",)
REQUIRED_EXPERIMENT_PLACEHOLDER = ".gitkeep"
ENVIRONMENT_CODE_DIR = "environments"
POLICY_CODE_DIR = "policies"
CUSTOM_HARNESS_CODE_DIR = "custom_envs"
CUSTOM_HARNESS_FILES = (
    "__init__.py",
    "adapter.py",
    "evaluate.py",
    "search.py",
    "summarize.py",
    "report.py",
    "performance_report.py",
    "audit.py",
)


def slug_for_env_id(env_id: str) -> str:
    """Return a stable filesystem slug for a known or arbitrary env id."""

    try:
        return registration_for(env_id).slug
    except KeyError:
        slug = re.sub(r"[^a-z0-9]+", "_", env_id.lower()).strip("_")
        return slug or "unknown_env"


def experiment_dir(env_id: str) -> Path:
    """Return the root artifact directory for one environment."""

    return EXPERIMENTS_DIR / slug_for_env_id(env_id)


def env_results_dir(env_id: str) -> Path:
    """Return the per-environment results directory."""

    return experiment_dir(env_id) / "results"


def env_configs_dir(env_id: str) -> Path:
    """Return the per-environment configs directory."""

    return experiment_dir(env_id) / "configs"


def env_reports_dir(env_id: str) -> Path:
    """Return the per-environment reports directory."""

    return experiment_dir(env_id) / "reports"


def env_notes_dir(env_id: str) -> Path:
    """Return the per-environment notes directory."""

    return experiment_dir(env_id) / "notes"


def _experiment_root(env_id: str, experiments_dir: Path) -> Path:
    return experiments_dir / slug_for_env_id(env_id)


def render_experiment_readme(env_id: str) -> str:
    """Return the standard README text for one environment artifact root."""

    slug = slug_for_env_id(env_id)
    artifact_root = f"experiments/{slug}"
    return (
        f"# {env_id} Artifacts\n\n"
        f"Environment ID: `{env_id}`\n"
        f"Artifact root: `{artifact_root}/`\n\n"
        "This directory is reserved for benchmark evidence: configs, append-only "
        "ledgers, generated summaries, reports, notes, traces, and replay metadata. "
        "Keep scaffold files separate from generated evidence so review can tell "
        "what was created by setup versus what came from evaluation or audit runs.\n\n"
        "Scaffold-created layout:\n\n"
        "```text\n"
        f"{artifact_root}/\n"
        "  README.md\n"
        "  configs/.gitkeep\n"
        "  results/.gitkeep\n"
        "  reports/.gitkeep\n"
        "  notes/.gitkeep\n"
        "```\n\n"
        "Generated after evaluation/report/audit commands:\n\n"
        "```text\n"
        f"{artifact_root}/\n"
        "  results/trials.jsonl\n"
        "  results/summary.csv\n"
        "  results/audit_latest.json\n"
        "  reports/final_report.md\n"
        "```\n\n"
        "Keep new environments registered as `planned` until real policies, smoke "
        "evaluation, ledger/summary/report generation, audit checks, and regression "
        "tests exist. Do not delete failed ledger rows once generated.\n"
    )


def scaffold_experiment_artifacts(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
    overwrite_readme: bool = False,
) -> dict[str, object]:
    """Create the standard per-environment artifact tree for an environment."""

    slug = slug_for_env_id(env_id)
    root = _experiment_root(env_id, experiments_dir)
    created: list[str] = []
    existing: list[str] = []

    for path in expected_experiment_dirs(env_id, experiments_dir=experiments_dir):
        if path.exists():
            existing.append(path.as_posix())
        else:
            path.mkdir(parents=True, exist_ok=True)
            created.append(path.as_posix())

    readme_path = root / "README.md"
    if readme_path.exists() and not overwrite_readme:
        existing.append(readme_path.as_posix())
    else:
        readme_path.write_text(render_experiment_readme(env_id), encoding="utf-8")
        created.append(readme_path.as_posix())

    for keep_path in expected_experiment_placeholder_files(
        env_id, experiments_dir=experiments_dir
    ):
        if keep_path.exists():
            existing.append(keep_path.as_posix())
        else:
            keep_path.write_text("keep\n", encoding="utf-8")
            created.append(keep_path.as_posix())

    return {
        "env_id": env_id,
        "slug": slug,
        "root": root.as_posix(),
        "created": created,
        "existing": existing,
    }


def _python_module_slug(value: str) -> str:
    """Return a lowercase Python-identifier slug from an env or artifact name."""

    slug = re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug) or "unknown_env"
    if not slug.isidentifier() or slug[0].isdigit():
        slug = f"env_{slug}"
    return slug


def custom_harness_module_slug(env_id: str) -> str:
    """Return a Python-package-safe module slug for one environment."""

    return _python_module_slug(slug_for_env_id(env_id))


def _pascal_identifier(value: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", value)
    name = "".join(part[:1].upper() + part[1:] for part in parts)
    return name if name and not name[0].isdigit() else f"Env{name}"


def environment_registration_path(
    env_id: str,
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
) -> Path:
    """Return the scaffold registration file path for one environment."""

    return package_dir / ENVIRONMENT_CODE_DIR / f"{custom_harness_module_slug(env_id)}.py"


def policy_scaffold_path(
    env_id: str,
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
) -> Path:
    """Return the scaffold policy file path for one environment."""

    return package_dir / POLICY_CODE_DIR / f"{custom_harness_module_slug(env_id)}.py"


def expected_environment_code_files(
    env_id: str,
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
) -> tuple[Path, ...]:
    """Return registration and policy scaffold files for one environment."""

    return (
        environment_registration_path(env_id, package_dir=package_dir),
        policy_scaffold_path(env_id, package_dir=package_dir),
    )


def render_environment_registration_file(
    env_id: str,
    *,
    include_custom_module: bool = False,
) -> str:
    """Return a planned registration scaffold for one environment."""

    slug = custom_harness_module_slug(env_id)
    custom_module_line = (
        f'    custom_module="hl_benchmark.custom_envs.{slug}",\n'
        if include_custom_module
        else ""
    )
    return (
        f'"""Planned {env_id} benchmark registration."""\n\n'
        "from __future__ import annotations\n\n"
        "from .base import EnvSpec, EnvironmentRegistration\n\n\n"
        "REGISTRATION = EnvironmentRegistration(\n"
        f'    key="{slug}",\n'
        '    status="planned",\n'
        f'    policy_module="hl_benchmark.policies.{slug}",\n'
        f"{custom_module_line}"
        "    suite_order=1000,\n"
        "    spec=EnvSpec(\n"
        f'        env_id="{env_id}",\n'
        '        category="todo",\n'
        '        observation_summary="TODO: record observation space and state semantics.",\n'
        '        action_summary="TODO: record action space and action semantics.",\n'
        '        reward_interpretation="TODO: record reward semantics and termination rules.",\n'
        "        episode_length=0,\n"
        "        success_target=0.0,\n"
        '        initial_policy="TODO: describe the initial transparent heuristic.",\n'
        "        known_failure_modes=(\n"
        '            "TODO: record known failure modes before promotion.",\n'
        "        ),\n"
        '        docs_url="TODO",\n'
        "    ),\n"
        "    notes=(\n"
        '        "Scaffold only; keep status planned until smoke tests, ledger, report, and audit exist.",\n'
        "    ),\n"
        ")\n"
    )


def render_policy_scaffold_file(env_id: str) -> str:
    """Return a transparent policy scaffold for one environment."""

    slug = custom_harness_module_slug(env_id)
    class_name = f"{_pascal_identifier(env_id)}Policy"
    return (
        f'"""Transparent policy scaffold for {env_id}."""\n\n'
        "from __future__ import annotations\n\n"
        "from typing import Any\n\n"
        "from .base import BasePolicy\n\n\n"
        'SUPPORTED_POLICY_NAMES = ("initial",)\n\n\n'
        f"class {class_name}(BasePolicy):\n"
        '    """TODO: replace with the initial readable heuristic before evaluation."""\n\n'
        '    policy_name = "initial"\n\n'
        "    def act(self, obs: Any) -> Any:\n"
        "        del obs\n"
        f"        raise NotImplementedError(\"implement {env_id} policy logic\")\n\n"
        "    def config(self) -> dict[str, Any]:\n"
        f"        return {{\"env_id\": \"{env_id}\", \"status\": \"scaffold\"}}\n\n\n"
        "def candidate_configs(*, max_candidates: int = 32) -> list[dict[str, Any]]:\n"
        "    \"\"\"Return scalar-only search configs after the real policy exists.\"\"\"\n\n"
        "    del max_candidates\n"
        f"    raise NotImplementedError(\"define scalar search space for {env_id}\")\n\n\n"
        "def make_policy(\n"
        "    policy_name: str,\n"
        "    *,\n"
        "    config: dict[str, Any] | None = None,\n"
        ") -> BasePolicy:\n"
        "    \"\"\"Build a policy from this environment-local scaffold registry.\"\"\"\n\n"
        "    del config\n"
        "    if policy_name not in SUPPORTED_POLICY_NAMES:\n"
        f"        raise ValueError(f\"unsupported {slug} policy {{policy_name!r}}\")\n"
        f"    return {class_name}()\n"
    )


def scaffold_environment_code(
    env_id: str,
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
    overwrite: bool = False,
    include_custom_module: bool = False,
) -> dict[str, object]:
    """Create planned registration and policy scaffold files for an environment."""

    slug = custom_harness_module_slug(env_id)
    created: list[str] = []
    existing: list[str] = []
    renderers = {
        environment_registration_path(
            env_id,
            package_dir=package_dir,
        ): render_environment_registration_file(
            env_id,
            include_custom_module=include_custom_module,
        ),
        policy_scaffold_path(
            env_id,
            package_dir=package_dir,
        ): render_policy_scaffold_file(env_id),
    }
    for path, text in renderers.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            existing.append(path.as_posix())
            continue
        path.write_text(text, encoding="utf-8")
        created.append(path.as_posix())
    return {
        "env_id": env_id,
        "slug": slug,
        "root": package_dir.as_posix(),
        "created": created,
        "existing": existing,
        "include_custom_module": include_custom_module,
    }


def environment_test_scaffold_path(
    env_id: str,
    *,
    tests_dir: Path = TESTS_DIR,
) -> Path:
    """Return the suggested test scaffold path for one environment."""

    return tests_dir / f"test_{custom_harness_module_slug(env_id)}_scaffold.py"


def render_environment_test_scaffold_file(env_id: str) -> str:
    """Return pytest scaffold text for a new environment."""

    slug = custom_harness_module_slug(env_id)
    return (
        f'"""Test scaffold for {env_id}.\n\n'
        "Replace these skipped tests with real registry, policy, ledger, report,\n"
        "determinism, and holdout-guard coverage before promotion.\n"
        '"""\n\n'
        "from __future__ import annotations\n\n"
        "import pytest\n\n"
        f'ENV_ID = "{env_id}"\n'
        f'MODULE_SLUG = "{slug}"\n'
        "PROMOTION_CHECKS = (\n"
        f'    "make check-env ENV={env_id}",\n'
        f"    'make check-env ENV={env_id} ARGS=\"--format json\"',\n"
        f'    "make check-promotion ENV={env_id}",\n'
        '    "make check-planned-envs",\n'
        ")\n\n"
        "pytestmark = pytest.mark.skip(\n"
        f'    reason="TODO: replace {env_id} scaffold tests before promotion"\n'
        ")\n\n\n"
        "def test_registry_metadata_contract() -> None:\n"
        "    assert ENV_ID\n\n\n"
        "def test_planned_readiness_gate_before_promotion() -> None:\n"
        "    assert PROMOTION_CHECKS\n"
        "    assert any(\"make check-planned-envs\" in command for command in PROMOTION_CHECKS)\n"
        "    assert any(\"make check-promotion\" in command for command in PROMOTION_CHECKS)\n\n\n"
        "def test_policy_action_validity_golden_cases() -> None:\n"
        "    assert MODULE_SLUG\n\n\n"
        "def test_fixed_seed_smoke_evaluation_and_ledger_schema() -> None:\n"
        "    assert ENV_ID\n\n\n"
        "def test_report_generation_and_holdout_guardrails() -> None:\n"
        "    assert MODULE_SLUG\n"
    )


def scaffold_environment_tests(
    env_id: str,
    *,
    tests_dir: Path = TESTS_DIR,
    overwrite: bool = False,
) -> dict[str, object]:
    """Create a pytest scaffold for a new environment."""

    slug = custom_harness_module_slug(env_id)
    path = environment_test_scaffold_path(env_id, tests_dir=tests_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    existing: list[str] = []
    if path.exists() and not overwrite:
        existing.append(path.as_posix())
    else:
        path.write_text(render_environment_test_scaffold_file(env_id), encoding="utf-8")
        created.append(path.as_posix())
    return {
        "env_id": env_id,
        "slug": slug,
        "root": tests_dir.as_posix(),
        "created": created,
        "existing": existing,
    }


def custom_harness_parent_init_path(
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
) -> Path:
    """Return the package marker for the custom harness parent package."""

    return package_dir / CUSTOM_HARNESS_CODE_DIR / "__init__.py"


def render_custom_harness_parent_init_file() -> str:
    """Return source for the custom harness parent package marker."""

    return (
        '"""Preferred package root for custom benchmark harnesses."""\n\n'
        "from __future__ import annotations\n"
    )


def custom_harness_dir(
    env_id: str,
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
) -> Path:
    """Return the package directory for one custom harness."""

    return package_dir / CUSTOM_HARNESS_CODE_DIR / custom_harness_module_slug(env_id)


def expected_custom_harness_files(
    env_id: str,
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
) -> tuple[Path, ...]:
    """Return the standard custom-harness scaffold files."""

    root = custom_harness_dir(env_id, package_dir=package_dir)
    return tuple(root / file_name for file_name in CUSTOM_HARNESS_FILES)


def render_custom_harness_file(env_id: str, file_name: str) -> str:
    """Return scaffold source for one custom-harness module."""

    slug = custom_harness_module_slug(env_id)
    title = f"{env_id} custom harness"
    if file_name == "__init__.py":
        return (
            f'"""{title}."""\n\n'
            "from __future__ import annotations\n\n"
            f'ENV_ID = "{env_id}"\n'
        )
    if file_name == "adapter.py":
        return (
            f'"""Dependency and API adapter for {env_id}."""\n\n'
            "from __future__ import annotations\n\n"
            "from typing import Any\n\n"
            f'ENV_ID = "{env_id}"\n\n\n'
            "def dependency_versions() -> dict[str, str]:\n"
            "    \"\"\"Return exact package versions used by this environment.\"\"\"\n\n"
            "    return {}\n\n\n"
            "def check_environment_available() -> tuple[bool, str]:\n"
            "    \"\"\"Return whether runtime dependencies are installed.\"\"\"\n\n"
            "    return False, \"TODO: implement dependency check\"\n\n\n"
            "def make_environment(*_args: Any, **_kwargs: Any) -> Any:\n"
            "    \"\"\"Construct the environment after compatibility checks pass.\"\"\"\n\n"
            f"    raise NotImplementedError(\"implement {slug}.adapter.make_environment\")\n"
        )
    command_name = file_name.removesuffix(".py")
    extra_arguments = ""
    if command_name == "audit":
        extra_arguments = (
            "    parser.add_argument(\n"
            "        \"--output\",\n"
            "        default=None,\n"
            "        help=\"Optional path for machine-readable audit JSON output.\",\n"
            "    )\n"
        )
    return (
        f'"""{command_name} command scaffold for {env_id}."""\n\n'
        "from __future__ import annotations\n\n"
        "import argparse\n\n"
        f'ENV_ID = "{env_id}"\n\n\n'
        "def main() -> None:\n"
        f"    parser = argparse.ArgumentParser(description=__doc__)\n"
        "    parser.add_argument(\"--format\", choices=(\"text\", \"json\"), default=\"text\")\n"
        f"{extra_arguments}"
        "    parser.parse_args()\n"
        f"    raise SystemExit(\"TODO: implement {slug}.{command_name}\")\n\n\n"
        "if __name__ == \"__main__\":\n"
        "    main()\n"
    )


def scaffold_custom_harness_code(
    env_id: str,
    *,
    package_dir: Path = BENCHMARK_PACKAGE_DIR,
    overwrite: bool = False,
) -> dict[str, object]:
    """Create placeholder custom-harness modules for a new environment."""

    slug = custom_harness_module_slug(env_id)
    root = custom_harness_dir(env_id, package_dir=package_dir)
    created: list[str] = []
    existing: list[str] = []

    parent_init = custom_harness_parent_init_path(package_dir=package_dir)
    parent_init.parent.mkdir(parents=True, exist_ok=True)
    if parent_init.exists() and not overwrite:
        existing.append(parent_init.as_posix())
    else:
        parent_init.write_text(render_custom_harness_parent_init_file(), encoding="utf-8")
        created.append(parent_init.as_posix())

    root.mkdir(parents=True, exist_ok=True)
    for path in expected_custom_harness_files(env_id, package_dir=package_dir):
        if path.exists() and not overwrite:
            existing.append(path.as_posix())
            continue
        path.write_text(render_custom_harness_file(env_id, path.name), encoding="utf-8")
        created.append(path.as_posix())
    return {
        "env_id": env_id,
        "slug": slug,
        "root": root.as_posix(),
        "created": created,
        "existing": existing,
    }


def expected_experiment_dirs(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[Path, ...]:
    """Return the required artifact directories for one environment."""

    root = _experiment_root(env_id, experiments_dir)
    return (root,) + tuple(root / child for child in REQUIRED_EXPERIMENT_SUBDIRS)


def expected_experiment_files(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[Path, ...]:
    """Return the required artifact files for one environment."""

    root = _experiment_root(env_id, experiments_dir)
    return tuple(root / child for child in REQUIRED_EXPERIMENT_FILES)


def expected_experiment_placeholder_files(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[Path, ...]:
    """Return required placeholder files that keep artifact dirs in git."""

    root = _experiment_root(env_id, experiments_dir)
    return tuple(
        root / child / REQUIRED_EXPERIMENT_PLACEHOLDER
        for child in REQUIRED_EXPERIMENT_SUBDIRS
    )


def missing_experiment_dirs(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[Path, ...]:
    """Return required per-environment artifact directories that do not exist."""

    return tuple(
        path
        for path in expected_experiment_dirs(env_id, experiments_dir=experiments_dir)
        if not path.is_dir()
    )


def missing_experiment_files(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[Path, ...]:
    """Return required per-environment artifact files that do not exist."""

    return tuple(
        path
        for path in expected_experiment_files(env_id, experiments_dir=experiments_dir)
        if not path.is_file()
    )


def missing_experiment_placeholder_files(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[Path, ...]:
    """Return required per-environment placeholder files that do not exist."""

    return tuple(
        path
        for path in expected_experiment_placeholder_files(
            env_id, experiments_dir=experiments_dir
        )
        if not path.is_file()
    )


def missing_experiment_artifacts(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[Path, ...]:
    """Return required artifact directories and files that do not exist."""

    return (
        missing_experiment_dirs(env_id, experiments_dir=experiments_dir)
        + missing_experiment_files(env_id, experiments_dir=experiments_dir)
        + missing_experiment_placeholder_files(env_id, experiments_dir=experiments_dir)
    )


def experiment_readme_identity_issues(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[str, ...]:
    """Return README identity issues for one environment artifact root."""

    slug = slug_for_env_id(env_id)
    readme_path = _experiment_root(env_id, experiments_dir) / "README.md"
    if not readme_path.is_file():
        return ()
    text = readme_path.read_text(encoding="utf-8")
    issues: list[str] = []
    if env_id not in text:
        issues.append(f"README.md does not identify environment id {env_id!r}")
    artifact_root = f"experiments/{slug}"
    if artifact_root not in text:
        issues.append(f"README.md does not identify artifact root {artifact_root!r}")
    return tuple(issues)


def experiment_artifact_layout_issues(
    env_id: str,
    *,
    experiments_dir: Path = EXPERIMENTS_DIR,
) -> tuple[str, ...]:
    """Return missing-artifact and README identity issues for one environment."""

    missing = tuple(
        f"missing {path.as_posix()}"
        for path in missing_experiment_artifacts(
            env_id, experiments_dir=experiments_dir
        )
    )
    return missing + experiment_readme_identity_issues(
        env_id, experiments_dir=experiments_dir
    )


def env_ledger_path(env_id: str) -> Path:
    """Return the default per-environment append-only ledger path."""

    return env_results_dir(env_id) / "trials.jsonl"


def env_summary_path(env_id: str) -> Path:
    """Return the default per-environment summary CSV path."""

    return env_results_dir(env_id) / "summary.csv"


def env_report_path(env_id: str) -> Path:
    """Return the default per-environment report path."""

    return env_reports_dir(env_id) / "final_report.md"


def render_scaffold_result(result: dict[str, object]) -> str:
    """Render scaffold output for humans."""

    created = result.get("created", [])
    existing = result.get("existing", [])
    label = result.get("label", "Experiment artifact scaffold")
    lines = [
        f"{label}: {result['env_id']}",
        f"- Slug: {result['slug']}",
        f"- Root: {result['root']}",
    ]
    if "include_custom_module" in result:
        custom_module_state = (
            "included" if result["include_custom_module"] else "not included"
        )
        lines.append(f"- REGISTRATION.custom_module: {custom_module_state}")
    lines.extend(
        [
            f"- Created paths: {len(created)}",
            f"- Existing paths: {len(existing)}",
        ]
    )
    if created:
        lines.append("- Created:")
        lines.extend(f"  - {path}" for path in created)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scaffold-env",
        metavar="ENV_ID",
        help="Create the standard experiments/<env_slug>/ artifact tree for one environment.",
    )
    parser.add_argument(
        "--scaffold-env-code",
        metavar="ENV_ID",
        help="Create planned registration and policy scaffold modules.",
    )
    parser.add_argument(
        "--custom-registration",
        action="store_true",
        help="When used with --scaffold-env-code, include REGISTRATION.custom_module for a custom harness.",
    )
    parser.add_argument(
        "--scaffold-custom-code",
        metavar="ENV_ID",
        help="Create placeholder hl_benchmark/custom_envs/<env_slug>/ custom harness modules.",
    )
    parser.add_argument(
        "--scaffold-tests",
        metavar="ENV_ID",
        help="Create a skipped pytest scaffold for one environment.",
    )
    parser.add_argument(
        "--experiments-dir",
        type=Path,
        default=EXPERIMENTS_DIR,
        help="Artifact root to scaffold under; defaults to the project experiments/ directory.",
    )
    parser.add_argument(
        "--package-dir",
        type=Path,
        default=BENCHMARK_PACKAGE_DIR,
        help="Package root for custom harness scaffolds; defaults to hl_benchmark/.",
    )
    parser.add_argument(
        "--tests-dir",
        type=Path,
        default=TESTS_DIR,
        help="Test root for generated pytest scaffolds; defaults to tests/.",
    )
    parser.add_argument(
        "--overwrite-readme",
        action="store_true",
        help="Rewrite an existing per-environment README.md with the standard template.",
    )
    parser.add_argument(
        "--overwrite-code",
        action="store_true",
        help="Rewrite existing custom-harness scaffold modules.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    results: list[dict[str, object]] = []
    if args.scaffold_env:
        result = scaffold_experiment_artifacts(
            args.scaffold_env,
            experiments_dir=args.experiments_dir,
            overwrite_readme=args.overwrite_readme,
        )
        result["label"] = "Experiment artifact scaffold"
        results.append(result)
    if args.scaffold_env_code:
        result = scaffold_environment_code(
            args.scaffold_env_code,
            package_dir=args.package_dir,
            overwrite=args.overwrite_code,
            include_custom_module=args.custom_registration,
        )
        result["label"] = "Environment registration/policy scaffold"
        results.append(result)
    if args.scaffold_custom_code:
        result = scaffold_custom_harness_code(
            args.scaffold_custom_code,
            package_dir=args.package_dir,
            overwrite=args.overwrite_code,
        )
        result["label"] = "Custom harness code scaffold"
        results.append(result)
    if args.scaffold_tests:
        result = scaffold_environment_tests(
            args.scaffold_tests,
            tests_dir=args.tests_dir,
            overwrite=args.overwrite_code,
        )
        result["label"] = "Environment test scaffold"
        results.append(result)
    if not results:
        parser.error(
            "one of --scaffold-env, --scaffold-env-code, "
            "--scaffold-custom-code, or --scaffold-tests is required"
        )
    output: object = results[0] if len(results) == 1 else {"scaffolds": results}
    if args.format == "json":
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        for result in results:
            print(render_scaffold_result(result), end="")


if __name__ == "__main__":
    main()
