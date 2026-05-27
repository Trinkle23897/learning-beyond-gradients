"""Audit SlimeVolley experiment artifacts for consistency."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import (
    PROJECT_ROOT,
    env_configs_dir,
    env_ledger_path,
    env_report_path,
    env_reports_dir,
    env_results_dir,
    env_summary_path,
)
from hl_benchmark.envs import SEED_SPLITS
from hl_benchmark.ledger import read_entries, score_value
from hl_benchmark.search import candidate_configs
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID
from hl_benchmark.slimevolley.amendments import (
    apply_ledger_amendments,
    default_amendments_path,
    read_ledger_amendments,
)
from hl_benchmark.slimevolley.opponents import OPPONENT_POOL
from hl_benchmark.slimevolley.protocol import (
    GENERATION_2_SEED_SPLITS,
    GENERATION_3_PROTOCOL_ID,
    GENERATION_3_SEED_SPLITS,
    GENERATION_4_PROTOCOL_ID,
    GENERATION_4_SEED_SPLITS,
    PROTOCOL_ID as GENERATION_2_PROTOCOL_ID,
    PROTOCOL_STATUS as GENERATION_PROTOCOL_STATUS,
)
from hl_benchmark.slimevolley.schema import (
    CANONICAL_CHANGE_TYPES,
    validate_slimevolley_ledger_entry,
)


RESERVED_TUNING_SPLITS = {"holdout", "audit"}
TUNING_CHANGE_TYPES = {"scalar/config tuning"}
EXPECTED_HOLDOUT_SEEDS = list(SEED_SPLITS["holdout"])
EXPLICIT_TEST_STATUS_REQUIRED_AFTER = datetime(2026, 5, 25, tzinfo=timezone.utc)
EXPLICIT_TEST_STATUS_REQUIRED_AFTER_LABEL = EXPLICIT_TEST_STATUS_REQUIRED_AFTER.isoformat()
VALID_POLICY_REFERENCES = frozenset(
    {
        "random",
        "initial",
        "tuned",
        "improved",
        "improved-v0",
        "improved-v1",
        "improved-v2",
        "improved-v3",
        "improved-v4",
        "improved-v5",
        "improved-v6",
        "improved-tuned",
        "attack",
        "rally-serve",
        "net-pressure",
        "temporal",
        "planner",
        "teacher-assisted",
        "baseline-rnn",
    }
)
SOURCE_HASH_RELATIVE_PATHS = (
    "hl_benchmark/artifacts.py",
    "hl_benchmark/custom.py",
    "hl_benchmark/envs.py",
    "hl_benchmark/ledger.py",
    "hl_benchmark/registry.py",
    "hl_benchmark/custom_envs/slimevolley/__init__.py",
    "hl_benchmark/custom_envs/slimevolley/adapter.py",
    "hl_benchmark/custom_envs/slimevolley/audit.py",
    "hl_benchmark/custom_envs/slimevolley/contact_diagnostics.py",
    "hl_benchmark/custom_envs/slimevolley/doctor.py",
    "hl_benchmark/custom_envs/slimevolley/evaluate.py",
    "hl_benchmark/slimevolley/amendments.py",
    "hl_benchmark/custom_envs/slimevolley/final_eval.py",
    "hl_benchmark/custom_envs/slimevolley/generation_report.py",
    "hl_benchmark/custom_envs/slimevolley/performance_report.py",
    "hl_benchmark/custom_envs/slimevolley/protocol.py",
    "hl_benchmark/custom_envs/slimevolley/report.py",
    "hl_benchmark/custom_envs/slimevolley/search.py",
    "hl_benchmark/custom_envs/slimevolley/summarize.py",
    "hl_benchmark/custom_envs/slimevolley/tournament.py",
    "hl_benchmark/environments/__init__.py",
    "hl_benchmark/environments/base.py",
    "hl_benchmark/environments/slimevolley.py",
    "hl_benchmark/policies/base.py",
    "hl_benchmark/policies/factory.py",
    "hl_benchmark/policies/slimevolley.py",
    "hl_benchmark/slimevolley/adapter.py",
    "hl_benchmark/slimevolley/audit.py",
    "hl_benchmark/slimevolley/contact_diagnostics.py",
    "hl_benchmark/slimevolley/doctor.py",
    "hl_benchmark/slimevolley/evaluate.py",
    "hl_benchmark/slimevolley/final_eval.py",
    "hl_benchmark/slimevolley/opponents.py",
    "hl_benchmark/slimevolley/report.py",
    "hl_benchmark/slimevolley/performance_report.py",
    "hl_benchmark/slimevolley/generation_report.py",
    "hl_benchmark/slimevolley/protocol.py",
    "hl_benchmark/slimevolley/schema.py",
    "hl_benchmark/slimevolley/search.py",
    "hl_benchmark/slimevolley/summarize.py",
    "hl_benchmark/slimevolley/tournament.py",
)


REQUIRED_DIAGNOSTIC_FIELDS = (
    "status",
    "packages",
    "runtime_metadata",
    "expected_observation_space",
    "expected_action_space",
    "expected_step_api",
    "reward_semantics",
    "seed_api_behavior",
    "same_seed_reset_observation_equal",
    "observed_step_api",
    "multiagent_step_api_observed",
)
VALID_STEP_API_LABELS = {"legacy-4-tuple", "gymnasium-5-tuple"}


REQUIRED_REPORT_SECTIONS = (
    "## Status",
    "## Dependency Versions",
    "## Runtime Metadata",
    "## Environment Diagnostics",
    "## Reproduction Commands",
    "## Artifact Integrity Checks",
    "## Artifact Manifest",
    "## Opponent Protocol",
    "## Ledger Summary",
    "## Failure Notes",
    "## Seed Ranges",
    "## Policy Evolution Timeline",
    "## Development Diagnosis",
    "## Diagnostic Coverage",
    "## Trace Diagnostics",
    "## Failed Or Partial Directions",
    "## Round-Robin Tournament",
    "## Holdout Evaluation",
    "## Generation-2 Evidence",
    "## Generation-3 Evidence",
    "## Generation-4 Development Attempt",
    "## Scalar Search Baseline",
    "## Neural/RL Comparator",
    "## Cost Accounting",
    "## Hypothesis Evidence Verdict",
    "## Anti-Cheating And Limitations",
    "## Current Conclusion",
    "## Next Steps",
)

REQUIRED_REPORT_SNIPPETS = (
    "make check-env ENV=SlimeVolley-v0",
    "make check-promotion ENV=SlimeVolley-v0",
    "make check-promotions",
    "make check-envs",
    "make check-env-layout",
    "make custom-run ENV=SlimeVolley-v0",
    "make custom-verify ENV=SlimeVolley-v0",
    "make slimevolley-doctor",
    "make slimevolley-summary",
    "make slimevolley-contact-diagnostics",
    "make slimevolley-audit",
    "make slimevolley-verify",
    "make slimevolley-report",
    "make slimevolley-performance-report",
    "make slimevolley-generation-report",
    "make slimevolley-generation3-report",
    "make slimevolley-protocol",
    "make slimevolley-generation3-protocol",
    "make slimevolley-generation4-protocol",
    "make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev",
    "make slimevolley-search MAX_CANDIDATES=8",
    "make slimevolley-tournament SPLIT=dev",
    "make slimevolley-final-eval",
    "Custom module root: `hl_benchmark.custom_envs.slimevolley`",
    "hl_benchmark/custom_envs/slimevolley/",
    "hl_benchmark/slimevolley/",
    "--tests-pass-fail pass",
    "Use `--tests-pass-fail not_recorded` only when test status is genuinely unavailable",
    "`tests_pass_fail`",
    "trial_amendments.jsonl",
    "results/trials.jsonl",
    "results/summary.csv",
    "results/environment_diagnostics.json",
    "results/search_best_dev.json",
    "results/round_robin_dev.json",
    "results/holdout_final.json",
    "results/audit_latest.json",
    "requirements_audit_status_counts",
    "requirements_audit_partial_rows",
    "requirements_audit_completion_state",
    "requirements_audit_completion_recommendation",
    "requirements_audit_partial_row_details",
    "requirements_audit_partial_row_classifications",
    "results/generation_2_trials.jsonl",
    "results/generation_2_summary.csv",
    "results/generation_3_trials.jsonl",
    "results/generation_3_summary.csv",
    "results/generation_4_trials.jsonl",
    "results/generation_4_summary.csv",
    "results/contact_diagnostics_g3_dev.json",
    "results/search_best_g2_dev.json",
    "results/round_robin_g2_dev.json",
    "results/holdout_g2_final.json",
    "Observed step API",
    "Observed multi-agent step API",
    "Same-seed reset observation match",
    "Reward semantics",
    "reports/final_report.md",
    "reports/performance_deepdive.md",
    "reports/generation_2_diagnosis.md",
    "reports/generation_3_diagnosis.md",
    "reports/contact_diagnostics_g3_dev.md",
    "generation-2 ledger rows use only predeclared generation-2 split seeds",
    "search_best_g2_dev.json",
    "round_robin_g2_dev.json",
    "holdout_g2_final.json",
    "reports/generation_2_protocol.md",
    "configs/generation_2_protocol.json",
    "configs/generation_3_protocol.json",
    "reports/generation_3_protocol.md",
    "configs/generation_4_protocol.json",
    "reports/generation_4_temporal_history_attempt.md",
    "reports/generation_4_protocol.md",
    "9000..9049",
    "10000..10049",
    "11000..11049",
    "notes/generation_3_rear_wall_recovery_attempt.md",
    "notes/generation_3_delayed_low_receive_attempt.md",
    "notes/generation_3_rally_restart_serve_attempt.md",
    "notes/generation_3_rear_wall_press_attempt.md",
    "notes/generation_3_freeze_before_holdout.md",
    "rear_wall_press",
    "improved-v3 | structural archive",
    "improved-v4 | structural archive",
    "improved-v5 | structural archive",
    "improved-v6 | structural archive",
    "Timeline rows aggregate generation-1, generation-2, and generation-3 ledgers",
    "reports/requirements_audit.md",
    "| builtin | slimevolleygym-baseline-rnn | built-in baseline |",
    "| random | v0 | random policy |",
    "| initial | v0 | frozen heuristic |",
    "| improved-v0 | v0 | archived heuristic |",
    "| improved-v1 | v1 | archived heuristic |",
    "| improved-v2 | v2 | archived heuristic |",
    "| improved-v3 | v3 | archived heuristic |",
    "| improved-v4 | v4 | archived heuristic |",
    "| improved-v5 | v5 | archived heuristic |",
    "| improved-v6 | v6 | archived heuristic |",
    "| improved | current | current heuristic |",
    "| improved-tuned | g4-scalar-tuned-v2 | scalar-tuned structural heuristic |",
    "| attack | g4-late-contact-attack-candidate | structural heuristic candidate |",
    "| temporal | g4-candidate | temporal stacked-history heuristic |",
    "| planner | g4-planner-candidate | physics-feature heuristic |",
    "| teacher-assisted | g4-teacher-assisted-candidate | teacher-assisted transparent heuristic |",
    "| baseline-rnn | slimevolleygym-baseline-rnn-wrapper | pretrained neural/RNN comparator |",
    "do not rerun it for policy tuning after holdout evidence exists",
    "Minimum logged fields covered",
    "life-loss/life-win point events",
    "Explicit test pass/fail statuses",
    "Generation-2 ledger rows / evaluation records",
    "Generation-3 ledger rows / evaluation records",
    "Generation-4 ledger rows / evaluation records",
    "Total ledger rows / evaluation records",
    "Rows by change type across all ledgers",
    "generation-2 holdout",
    "Generation-4 Development Attempt",
    "ledger rows at or after `2026-05-25T00:00:00+00:00` include explicit `tests_pass_fail`",
)

REQUIRED_EXPERIMENT_README_SECTIONS = (
    "# SlimeVolley Experiment",
    "## Current Code Paths",
    "## Current Reproduction Commands",
    "## Artifact Manifest",
    "## Current Guardrails",
)

REQUIRED_EXPERIMENT_README_SNIPPETS = (
    "hl_benchmark/custom_envs/slimevolley/",
    "Registry-facing custom harness bridge",
    "python -m hl_benchmark.custom_envs.slimevolley.evaluate",
    "make slimevolley-verify",
    "requirements_audit_status_counts",
    "requirements_audit_partial_rows",
    "requirements_audit_completion_state",
    "requirements_audit_completion_recommendation",
    "requirements_audit_partial_row_details",
    "requirements_audit_partial_row_classifications",
    "`tests_pass_fail`",
    "trial_amendments.jsonl",
    "Holdout seeds `1000..1049`",
)


REQUIRED_PERFORMANCE_REPORT_SECTIONS = (
    "# SlimeVolley Performance Deep Dive",
    "## Status",
    "## Evidence Sources",
    "## Holdout Matrix",
    "## Generation-2 Final Evidence",
    "## Generation-3 Evidence",
    "## Headline Comparisons",
    "## Built-In Opponent Gap",
    "## Opponent-Pool Robustness",
    "## Development Round-Robin",
    "## Scalar Search Context",
    "## Cost Context",
    "## Interpretation",
    "## Next Performance Step",
)

REQUIRED_PERFORMANCE_REPORT_SNIPPETS = (
    "generated from existing artifacts only",
    "do not use it for policy tuning",
    "holdout_final.json",
    "holdout_g2_final.json",
    "round_robin_dev.json",
    "round_robin_g2_dev.json",
    "search_best_dev.json",
    "search_best_g2_dev.json",
    "generation_3_trials.jsonl",
    "search_best_g3_dev.json",
    "round_robin_g3_dev.json",
    "holdout_g3_final.json",
    "Generation-3 holdout",
    "Generation-3 ledger rows",
    "Rows by change type across all performance ledgers",
    "baseline-rnn",
    "improved",
    "tuned",
    "initial",
    "not deep-RL comparable",
    "Recommended next performance step",
)

REQUIRED_GENERATION_PROTOCOL_REPORT_SECTIONS = (
    "# SlimeVolley Generation-2 Protocol",
    "## Prior Holdout Lock",
    "## Generation-2 Seed Ranges",
    "## Opponent Protocol",
    "## Guardrails",
    "## Diagnosis Targets",
    "## Commands",
    "## Promotion Checks",
)

REQUIRED_GENERATION_PROTOCOL_SNIPPETS = (
    "slimevolley-g2",
    "predeclared-not-run",
    "Generation-1 holdout is already opened",
    "3000..3049",
    "4000..4049",
    "5000..5049",
    "generation_2_trials.jsonl",
    "search_best_g2_dev.json",
    "round_robin_g2_dev.json",
    "holdout_g2_final.json",
    "--seed-start 4000",
    "make slimevolley-verify",
    "hl_benchmark.custom_envs.slimevolley.audit",
)

REQUIRED_GENERATION_REPORT_SECTIONS = (
    "# SlimeVolley Generation-2 Diagnosis",
    "## Status",
    "## Evidence Sources",
    "## Trial Rows",
    "## Failure Analysis",
    "## Dependency Status",
    "## Cost So Far",
    "## Holdout Lock",
    "## Next Action",
)

REQUIRED_GENERATION_REPORT_SNIPPETS = (
    "generated from persisted generation-2 artifacts only",
    "generation_2_trials.jsonl",
    "generation_2_summary.csv",
    "holdout_g2_final.json",
    "generation-2 holdout",
    "final-only",
    "Dependency Status",
    "Cost So Far",
)


REQUIRED_GENERATION_3_PROTOCOL_REPORT_SECTIONS = (
    "# SlimeVolley Generation-3 Protocol",
    "## Prior Holdout Locks",
    "## Generation-3 Seed Ranges",
    "## Opponent Protocol",
    "## Guardrails",
    "## Diagnosis Targets",
    "## Commands",
    "## Promotion Checks",
)

REQUIRED_GENERATION_3_PROTOCOL_SNIPPETS = (
    "slimevolley-g3",
    "predeclared-not-run",
    "Generation-1 holdout is already opened",
    "Generation-2 holdout is already opened",
    "6000..6049",
    "7000..7049",
    "8000..8049",
    "generation_3_trials.jsonl",
    "search_best_g3_dev.json",
    "round_robin_g3_dev.json",
    "holdout_g3_final.json",
    "--seed-start 7000",
    "make slimevolley-verify",
    "hl_benchmark.custom_envs.slimevolley.audit",
)

REQUIRED_GENERATION_4_PROTOCOL_REPORT_SECTIONS = (
    "# SlimeVolley Generation-4 Protocol",
    "## Prior Holdout Locks",
    "## Generation-4 Seed Ranges",
    "## Opponent Protocol",
    "## Guardrails",
    "## Diagnosis Targets",
    "## Commands",
    "## Promotion Checks",
)

REQUIRED_GENERATION_4_PROTOCOL_SNIPPETS = (
    "slimevolley-g4",
    "predeclared-not-run",
    "Generation-1 holdout is already opened",
    "Generation-2 holdout is already opened",
    "Generation-3 holdout is already opened",
    "9000..9049",
    "10000..10049",
    "11000..11049",
    "generation_4_trials.jsonl",
    "search_best_g4_dev.json",
    "round_robin_g4_dev.json",
    "holdout_g4_final.json",
    "--seed-start 10000",
    "make slimevolley-verify",
    "hl_benchmark.custom_envs.slimevolley.audit",
)

REQUIRED_GENERATION_3_REPORT_SECTIONS = (
    "# SlimeVolley Generation-3 Diagnosis",
    "## Status",
    "## Evidence Sources",
    "## Trial Rows",
    "## Failure Analysis",
    "## Dependency Status",
    "## Cost So Far",
    "## Holdout Lock",
    "## Next Action",
)

REQUIRED_GENERATION_3_REPORT_SNIPPETS = (
    "generated from persisted generation-3 artifacts only",
    "generation_3_trials.jsonl",
    "generation_3_summary.csv",
    "holdout_g3_final.json",
    "generation-3 holdout",
    "final-only",
    "Dependency Status",
    "Cost So Far",
    "6000..6049",
)


REQUIRED_REQUIREMENTS_AUDIT_SECTIONS = (
    "# SlimeVolley Requirement Coverage Audit",
    "## Verdict",
    "## Completion Checkpoint",
    "## Machine-Readable Completion State",
    "## Coverage Matrix",
    "## Verification Commands",
    "## Known Limitations",
)

REQUIRED_REQUIREMENTS_AUDIT_SNIPPETS = (
    "Working repository",
    "Initial handwritten heuristic",
    "Agent-maintained heuristic policy versions",
    "Scalar/config search baseline",
    "Required command surface",
    "Heuristic-system improvement loop",
    "Replay and diagnostics",
    "Baseline comparison set",
    "Packaged RNN comparator",
    "documented pretrained neural/RNN comparator. No local PPO/DQN/self-play training baseline was run. | Satisfied |",
    "Holdout seeds `1000..1049`",
    "generation-2 holdout seeds `4000..4049`",
    "generation-3 holdout seeds `7000..7049`",
    "make slimevolley-verify",
    "make check-promotions",
    "contact diagnostics and generation protocol refreshes",
    "experiments/slimevolley/results/trials.jsonl",
    "results/trial_amendments.jsonl",
    "hl_benchmark/policies/slimevolley.py",
    "hl_benchmark/custom_envs/slimevolley/",
    "not deep-RL comparable",
    "Current completion gate",
    "Accepted historical caveats",
    "Do not mark the durable goal complete",
    "requirements_audit_completion_state",
    "requirements_audit_completion_recommendation",
    "eligible_for_completion_audit",
    "A passing artifact audit means the evidence is internally consistent",
)
VALID_REQUIREMENTS_AUDIT_STATUSES = {"Satisfied", "Partial", "Not satisfied", "Blocked"}
REQUIREMENTS_AUDIT_PARTIAL_ROW_DETAILS: dict[str, dict[str, str]] = {}
REQUIRED_REQUIREMENTS_AUDIT_ROW_STATUSES = {
    "Working repository": "Satisfied",
    "Reproduction instructions": "Satisfied",
    "SlimeVolley environment wrapper or compatibility layer": "Satisfied",
    "Exact package and runtime metadata": "Satisfied",
    "Initial handwritten heuristic": "Satisfied",
    "Agent-maintained heuristic policy versions": "Satisfied",
    "Opponent protocol": "Satisfied",
    "Fixed development and holdout seed ranges": "Satisfied",
    "Append-only trial ledger": "Satisfied",
    "Evaluation harness": "Satisfied",
    "Scalar/config search baseline": "Satisfied",
    "Round-robin or opponent-pool robustness check": "Satisfied",
    "Final holdout evaluation": "Satisfied",
    "Required command surface": "Satisfied",
    "Heuristic-system improvement loop": "Satisfied",
    "Replay and diagnostics": "Satisfied",
    "Baseline comparison set": "Satisfied",
    "Regression and golden tests": "Satisfied",
    "Failure-analysis notes": "Satisfied",
    "Separation of structural improvement from scalar tuning": "Satisfied",
    "Packaged RNN comparator": "Satisfied",
    "Cost accounting": "Satisfied",
    "Anti-cheating guardrails": "Satisfied",
    "Extensible multi-environment structure": "Satisfied",
    "Final Markdown report": "Satisfied",
}


def _requirements_audit_matrix_rows(requirements_audit_text: str) -> list[dict[str, str]]:
    """Return parsed rows from the requirement coverage matrix."""

    rows: list[dict[str, str]] = []
    for line in requirements_audit_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        requirement, evidence, status = cells[:3]
        if requirement == "Requirement" or set(requirement) <= {"-", " "}:
            continue
        rows.append(
            {
                "requirement": requirement,
                "evidence": evidence,
                "status": status,
            }
        )
    return rows


def _requirements_audit_matrix_issues(requirements_audit_text: str) -> list[str]:
    """Return issues from the requirement coverage matrix."""

    issues: list[str] = []
    rows_by_requirement: dict[str, str] = {}
    for row in _requirements_audit_matrix_rows(requirements_audit_text):
        requirement = row["requirement"]
        status = row["status"]
        if requirement in rows_by_requirement:
            issues.append(f"requirements audit duplicate row: {requirement}")
        rows_by_requirement[requirement] = status
        if status not in VALID_REQUIREMENTS_AUDIT_STATUSES:
            issues.append(
                f"requirements audit row {requirement!r} has unknown status {status!r}"
            )

    if not rows_by_requirement:
        issues.append("requirements audit coverage matrix has no data rows")
        return issues

    for requirement, expected_status in REQUIRED_REQUIREMENTS_AUDIT_ROW_STATUSES.items():
        observed_status = rows_by_requirement.get(requirement)
        if observed_status is None:
            issues.append(f"requirements audit missing coverage row: {requirement}")
        elif observed_status != expected_status:
            issues.append(
                f"requirements audit row {requirement!r} has status "
                f"{observed_status!r}, expected {expected_status!r}"
            )
    for requirement, status in rows_by_requirement.items():
        if status == "Partial" and requirement not in REQUIREMENTS_AUDIT_PARTIAL_ROW_DETAILS:
            issues.append(f"requirements audit partial row lacks classification: {requirement}")
    return issues


def _markdown_line_present(text: str, required_line: str) -> bool:
    """Return True when a required Markdown line appears exactly after trimming."""

    return any(line.strip() == required_line for line in text.splitlines())


def _read_summary_rows(summary_path: Path) -> list[dict[str, str]]:
    if not summary_path.exists():
        return []
    with summary_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_ledger_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _explicit_test_status_issues(entry: dict[str, Any], row_index: int) -> list[str]:
    if "tests_pass_fail" in entry:
        return []
    timestamp = _parse_ledger_timestamp(entry.get("timestamp"))
    if timestamp is None:
        return [
            f"ledger row {row_index}: missing tests_pass_fail and timestamp cannot be parsed as legacy"
        ]
    if timestamp >= EXPLICIT_TEST_STATUS_REQUIRED_AFTER:
        return [
            "ledger row {row_index}: missing tests_pass_fail for row at or after "
            "{cutoff}".format(
                row_index=row_index,
                cutoff=EXPLICIT_TEST_STATUS_REQUIRED_AFTER_LABEL,
            )
        ]
    return []


def _sha256_file(path: Path) -> str:
    if not path.exists():
        return "missing"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_hashes(
    *,
    ledger_path: Path,
    summary_path: Path,
    report_path: Path,
    diagnostics_path: Path,
    holdout_path: Path,
    search_best_path: Path,
    tournament_path: Path,
    ledger_amendments_path: Path | None,
    requirements_audit_path: Path,
    experiment_readme_path: Path | None,
    performance_report_path: Path | None,
    generation_report_path: Path | None,
    generation_ledger_path: Path | None,
    generation_summary_path: Path | None,
    generation_search_best_path: Path | None,
    generation_tournament_path: Path | None,
    generation_holdout_path: Path | None,
    generation_protocol_path: Path | None,
    generation_protocol_report_path: Path | None,
    generation3_report_path: Path | None,
    generation3_ledger_path: Path | None,
    generation3_summary_path: Path | None,
    generation3_search_best_path: Path | None,
    generation3_tournament_path: Path | None,
    generation3_holdout_path: Path | None,
    generation3_protocol_path: Path | None,
    generation3_protocol_report_path: Path | None,
    generation4_protocol_path: Path | None,
    generation4_protocol_report_path: Path | None,
    contact_diagnostics_json_path: Path | None,
    contact_diagnostics_report_path: Path | None,
) -> dict[str, str]:
    return {
        "ledger": _sha256_file(ledger_path),
        "summary": _sha256_file(summary_path),
        "report": _sha256_file(report_path),
        "diagnostics": _sha256_file(diagnostics_path),
        "holdout": _sha256_file(holdout_path),
        "search_best": _sha256_file(search_best_path),
        "tournament": _sha256_file(tournament_path),
        "ledger_amendments": (
            _sha256_file(ledger_amendments_path)
            if ledger_amendments_path is not None
            else "not_checked"
        ),
        "requirements_audit": _sha256_file(requirements_audit_path),
        "experiment_readme": (
            _sha256_file(experiment_readme_path)
            if experiment_readme_path is not None
            else "not_checked"
        ),
        "performance_report": (
            _sha256_file(performance_report_path)
            if performance_report_path is not None
            else "not_checked"
        ),
        "generation_report": (
            _sha256_file(generation_report_path)
            if generation_report_path is not None
            else "not_checked"
        ),
        "generation_ledger": (
            _sha256_file(generation_ledger_path)
            if generation_ledger_path is not None
            else "not_checked"
        ),
        "generation_summary": (
            _sha256_file(generation_summary_path)
            if generation_summary_path is not None
            else "not_checked"
        ),
        "generation_search_best": (
            _sha256_file(generation_search_best_path)
            if generation_search_best_path is not None
            else "not_checked"
        ),
        "generation_tournament": (
            _sha256_file(generation_tournament_path)
            if generation_tournament_path is not None
            else "not_checked"
        ),
        "generation_holdout": (
            _sha256_file(generation_holdout_path)
            if generation_holdout_path is not None
            else "not_checked"
        ),
        "generation_protocol": (
            _sha256_file(generation_protocol_path)
            if generation_protocol_path is not None
            else "not_checked"
        ),
        "generation_protocol_report": (
            _sha256_file(generation_protocol_report_path)
            if generation_protocol_report_path is not None
            else "not_checked"
        ),
        "generation3_report": (
            _sha256_file(generation3_report_path)
            if generation3_report_path is not None
            else "not_checked"
        ),
        "generation3_ledger": (
            _sha256_file(generation3_ledger_path)
            if generation3_ledger_path is not None
            else "not_checked"
        ),
        "generation3_summary": (
            _sha256_file(generation3_summary_path)
            if generation3_summary_path is not None
            else "not_checked"
        ),
        "generation3_search_best": (
            _sha256_file(generation3_search_best_path)
            if generation3_search_best_path is not None
            else "not_checked"
        ),
        "generation3_tournament": (
            _sha256_file(generation3_tournament_path)
            if generation3_tournament_path is not None
            else "not_checked"
        ),
        "generation3_holdout": (
            _sha256_file(generation3_holdout_path)
            if generation3_holdout_path is not None
            else "not_checked"
        ),
        "generation3_protocol": (
            _sha256_file(generation3_protocol_path)
            if generation3_protocol_path is not None
            else "not_checked"
        ),
        "generation3_protocol_report": (
            _sha256_file(generation3_protocol_report_path)
            if generation3_protocol_report_path is not None
            else "not_checked"
        ),
        "generation4_protocol": (
            _sha256_file(generation4_protocol_path)
            if generation4_protocol_path is not None
            else "not_checked"
        ),
        "generation4_protocol_report": (
            _sha256_file(generation4_protocol_report_path)
            if generation4_protocol_report_path is not None
            else "not_checked"
        ),
        "contact_diagnostics_json": (
            _sha256_file(contact_diagnostics_json_path)
            if contact_diagnostics_json_path is not None
            else "not_checked"
        ),
        "contact_diagnostics_report": (
            _sha256_file(contact_diagnostics_report_path)
            if contact_diagnostics_report_path is not None
            else "not_checked"
        ),
    }


def _source_hashes() -> dict[str, str]:
    return {
        relative_path: _sha256_file(PROJECT_ROOT / relative_path)
        for relative_path in SOURCE_HASH_RELATIVE_PATHS
    }


def _csv_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _expected_summary_row(entry: dict[str, Any]) -> dict[str, str]:
    seed_range = entry["seed_range"]
    return {
        "timestamp": _csv_cell(entry["timestamp"]),
        "environment": _csv_cell(entry["environment"]),
        "policy_version": _csv_cell(entry["policy_version"]),
        "opponent_name": _csv_cell(entry.get("opponent_name", "")),
        "opponent_version": _csv_cell(entry.get("opponent_version", "")),
        "opponent_kind": _csv_cell(entry.get("opponent_kind", "")),
        "change_type": _csv_cell(entry["change_type"]),
        "split": _csv_cell(seed_range["split"]),
        "seed_start": _csv_cell(seed_range["start"]),
        "seed_stop_exclusive": _csv_cell(seed_range["stop_exclusive"]),
        "episodes": _csv_cell(entry["episodes"]),
        "mean": score_value(entry, "mean"),
        "std": score_value(entry, "std"),
        "median": score_value(entry, "median"),
        "min": score_value(entry, "min"),
        "max": score_value(entry, "max"),
        "wins": _csv_cell(entry.get("win_loss_draw", {}).get("wins", "")),
        "losses": _csv_cell(entry.get("win_loss_draw", {}).get("losses", "")),
        "draws": _csv_cell(entry.get("win_loss_draw", {}).get("draws", "")),
        "win_rate": _csv_cell(entry.get("win_loss_draw", {}).get("win_rate", "")),
        "life_difference_mean": _csv_cell(entry.get("life_difference_stats", {}).get("mean", "")),
        "environment_steps": _csv_cell(entry["environment_steps"]),
        "wall_clock_seconds": _csv_cell(entry["wall_clock_seconds"]),
        "pass_fail": _csv_cell(entry["pass_fail"]),
        "tests_pass_fail": _csv_cell(entry.get("tests_pass_fail", "legacy_missing")),
        "git_commit": _csv_cell(entry["git_commit"]),
        "diff_identifier": _csv_cell(entry["diff_identifier"]),
        "agent_iterations": _csv_cell(entry["agent_iterations"]),
        "code_edits": _csv_cell(entry["code_edits"]),
        "change_summary": _csv_cell(entry["change_summary"]),
        "failure_analysis": _csv_cell(entry["failure_analysis"]),
        "next_hypothesis": _csv_cell(entry["next_hypothesis"]),
    }


def _summary_content_issues(
    entries: list[dict[str, Any]],
    summary_rows: list[dict[str, str]],
) -> list[str]:
    issues: list[str] = []
    for row_index, (entry, row) in enumerate(zip(entries, summary_rows), start=1):
        expected = _expected_summary_row(entry)
        for column, expected_value in expected.items():
            observed_value = row.get(column)
            if observed_value != expected_value:
                issues.append(
                    f"summary row {row_index} column {column!r} mismatch: "
                    f"expected {expected_value!r}, got {observed_value!r}"
                )
                break
        if len(issues) >= 20:
            issues.append("summary content validation stopped after 20 mismatches")
            break
    return issues


def _unknown_references(values: Any, allowed: set[str] | frozenset[str]) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted({str(value) for value in values if str(value) not in allowed})


def _search_best_artifact_issues(
    payload: dict[str, Any] | None,
    path: Path,
    entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Return integrity issues for the scalar-search selection artifact."""

    if payload is None:
        return []

    entries = entries or []
    issues: list[str] = []
    if payload.get("environment") != SLIMEVOLLEY_ENV_ID:
        issues.append(
            f"scalar-search artifact environment {payload.get('environment')!r} does not match {SLIMEVOLLEY_ENV_ID}"
        )
    if payload.get("split") in RESERVED_TUNING_SPLITS:
        issues.append(
            f"scalar-search artifact uses reserved {payload.get('split')!r} split: {path}"
        )
    if payload.get("split") != "dev":
        issues.append(f"scalar-search artifact split is not dev: {payload.get('split')!r}")
    if not isinstance(payload.get("config"), dict) or not payload.get("config"):
        issues.append("scalar-search artifact missing non-empty config")
    opponents = payload.get("opponents")
    if not isinstance(opponents, list) or not opponents:
        issues.append("scalar-search artifact missing opponents")
    else:
        unknown_opponents = _unknown_references(opponents, set(OPPONENT_POOL))
        if unknown_opponents:
            issues.append(f"scalar-search artifact references unknown opponents: {unknown_opponents}")
    opponent_means = payload.get("opponent_means")
    if not isinstance(opponent_means, dict) or not opponent_means:
        issues.append("scalar-search artifact missing opponent_means")
    elif isinstance(opponents, list) and set(opponent_means) != {str(opponent) for opponent in opponents}:
        issues.append("scalar-search artifact opponent_means keys do not match opponents")
    if not isinstance(payload.get("selection_score"), (int, float)):
        issues.append("scalar-search artifact missing numeric selection_score")
    if not isinstance(payload.get("candidate_count"), int) or payload.get("candidate_count", 0) <= 0:
        issues.append("scalar-search artifact missing positive candidate_count")
    candidate_count = payload.get("candidate_count")
    candidate_index = payload.get("candidate_index")
    if not isinstance(candidate_index, int):
        issues.append("scalar-search artifact missing integer candidate_index")
    elif isinstance(candidate_count, int) and not (
        1 <= candidate_index <= candidate_count
    ):
        issues.append("scalar-search artifact candidate_index outside one-based candidate_count")
    if (
        isinstance(candidate_count, int)
        and candidate_count > 0
        and isinstance(candidate_index, int)
        and 1 <= candidate_index <= candidate_count
        and isinstance(payload.get("config"), dict)
    ):
        candidates = candidate_configs(SLIMEVOLLEY_ENV_ID, max_candidates=candidate_count)
        if len(candidates) != candidate_count:
            issues.append(
                f"scalar-search artifact candidate_count {candidate_count} exceeds registered search space {len(candidates)}"
            )
        else:
            expected_config = candidates[candidate_index - 1]
            if payload.get("config") != expected_config:
                issues.append(
                    "scalar-search artifact config does not match candidate_index: "
                    f"expected {expected_config!r}, got {payload.get('config')!r}"
                )
    issues.extend(_search_best_ledger_content_issues(payload=payload, entries=entries))
    return issues


def _search_best_ledger_content_issues(
    *,
    payload: dict[str, Any],
    entries: list[dict[str, Any]],
) -> list[str]:
    issues: list[str] = []
    opponents = payload.get("opponents")
    entry_timestamps = payload.get("entry_timestamps")
    if not isinstance(opponents, list) or not opponents:
        return issues
    if not isinstance(entry_timestamps, list) or not entry_timestamps:
        has_scalar_rows = any(
            entry.get("change_type") == "scalar/config tuning" for entry in entries
        )
        return ["scalar-search artifact missing entry_timestamps"] if has_scalar_rows else []
    if len(entry_timestamps) != len(opponents):
        issues.append("scalar-search artifact entry_timestamps length does not match opponents")
        return issues

    entries_by_key = {
        (
            str(entry.get("timestamp")),
            str(entry.get("policy_version")),
            str(entry.get("opponent_name")),
        ): entry
        for entry in entries
    }
    means = payload.get("opponent_means")
    config = payload.get("config")
    std_penalty = payload.get("std_penalty", 0.0)
    selection_scores: list[float] = []
    for timestamp, opponent in zip(entry_timestamps, opponents):
        key = (str(timestamp), "tuned", str(opponent))
        entry = entries_by_key.get(key)
        if entry is None:
            issues.append(
                f"scalar-search artifact row tuned vs {opponent} timestamp {timestamp!r} is not present in ledger"
            )
            continue
        if entry.get("seed_range", {}).get("split") != payload.get("split"):
            issues.append(
                f"scalar-search artifact row tuned vs {opponent} split does not match ledger"
            )
        if entry.get("change_type") != "scalar/config tuning":
            issues.append(
                f"scalar-search artifact row tuned vs {opponent} is not scalar/config tuning"
            )
        entry_policy_config = entry.get("config", {}).get("policy", {})
        if isinstance(config, dict) and isinstance(entry_policy_config, dict):
            for key_name, expected_value in config.items():
                if entry_policy_config.get(key_name) != expected_value:
                    issues.append(
                        f"scalar-search artifact row tuned vs {opponent} config {key_name!r} "
                        f"does not match ledger: expected {expected_value!r}, got {entry_policy_config.get(key_name)!r}"
                    )
                    break
        mean = entry.get("score_stats", {}).get("mean")
        if isinstance(means, dict) and not _float_matches(means.get(str(opponent)), mean):
            issues.append(
                f"scalar-search artifact opponent mean for {opponent} does not match ledger: "
                f"expected {mean!r}, got {means.get(str(opponent))!r}"
            )
        std = entry.get("score_stats", {}).get("std") or 0.0
        if isinstance(mean, (int, float)) and isinstance(std_penalty, (int, float)):
            selection_scores.append(float(mean) - float(std_penalty) * float(std))
    if len(selection_scores) == len(opponents):
        expected_score = sum(selection_scores) / len(selection_scores)
        if not _float_matches(payload.get("selection_score"), expected_score):
            issues.append(
                "scalar-search artifact selection_score does not match ledger: "
                f"expected {expected_score!r}, got {payload.get('selection_score')!r}"
            )
    return issues


def _float_matches(left: Any, right: Any, *, tolerance: float = 1e-12) -> bool:
    if left is None or right is None:
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= tolerance
    return left == right


def _expected_holdout_cell(entry: dict[str, Any]) -> dict[str, Any]:
    wld = entry.get("win_loss_draw", {})
    score_stats = entry.get("score_stats", {})
    return {
        "timestamp": entry.get("timestamp"),
        "policy": entry.get("policy_version"),
        "opponent": entry.get("opponent_name"),
        "mean": score_stats.get("mean"),
        "std": score_stats.get("std"),
        "wins": wld.get("wins"),
        "losses": wld.get("losses"),
        "draws": wld.get("draws"),
        "win_rate": wld.get("win_rate"),
        "episodes": entry.get("episodes"),
        "environment_steps": entry.get("environment_steps"),
        "pass_fail": entry.get("pass_fail"),
    }


def _holdout_cell_content_issues(
    *,
    holdout_entries: list[dict[str, Any]],
    cells: Any,
) -> list[str]:
    if not holdout_entries:
        return []
    if not isinstance(cells, list):
        return ["holdout artifact cells is missing or not a list"]

    issues: list[str] = []
    cells_by_matchup = {
        (str(cell.get("policy")), str(cell.get("opponent"))): cell
        for cell in cells
        if isinstance(cell, dict)
    }
    for entry in holdout_entries:
        key = (str(entry.get("policy_version")), str(entry.get("opponent_name")))
        cell = cells_by_matchup.get(key)
        if cell is None:
            issues.append(f"holdout artifact missing cell for {key[0]} vs {key[1]}")
            continue
        expected = _expected_holdout_cell(entry)
        for field, expected_value in expected.items():
            observed_value = cell.get(field)
            if not _float_matches(observed_value, expected_value):
                issues.append(
                    f"holdout artifact cell {key[0]} vs {key[1]} field {field!r} "
                    f"does not match ledger: expected {expected_value!r}, got {observed_value!r}"
                )
                break
        if len(issues) >= 20:
            issues.append("holdout artifact cell validation stopped after 20 mismatches")
            break
    return issues


def _expected_tournament_cell(entry: dict[str, Any]) -> dict[str, Any]:
    expected = _expected_holdout_cell(entry)
    expected["split"] = entry.get("seed_range", {}).get("split")
    return expected


def _tournament_cell_content_issues(
    *,
    entries: list[dict[str, Any]],
    cells: Any,
    entry_timestamps: Any,
) -> list[str]:
    if not isinstance(cells, list) or not isinstance(entry_timestamps, list):
        return []

    issues: list[str] = []
    entries_by_key = {
        (
            str(entry.get("timestamp")),
            str(entry.get("policy_version")),
            str(entry.get("opponent_name")),
        ): entry
        for entry in entries
    }
    cell_timestamps = [str(cell.get("timestamp")) for cell in cells if isinstance(cell, dict)]
    if sorted(cell_timestamps) != sorted(str(timestamp) for timestamp in entry_timestamps):
        issues.append("tournament artifact entry_timestamps do not match cell timestamps")
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        timestamp = str(cell.get("timestamp"))
        if not timestamp or timestamp == "None":
            issues.append("tournament artifact timestamped cells are missing a cell timestamp")
            continue
        key = (timestamp, str(cell.get("policy")), str(cell.get("opponent")))
        entry = entries_by_key.get(key)
        if entry is None:
            issues.append(
                "tournament artifact cell "
                f"{key[1]} vs {key[2]} timestamp {timestamp!r} is not present in ledger"
            )
            continue
        expected = _expected_tournament_cell(entry)
        key = (str(cell.get("policy")), str(cell.get("opponent")))
        for field, expected_value in expected.items():
            observed_value = cell.get(field)
            if not _float_matches(observed_value, expected_value):
                issues.append(
                    f"tournament artifact cell {key[0]} vs {key[1]} field {field!r} "
                    f"does not match ledger: expected {expected_value!r}, got {observed_value!r}"
                )
                break
        if len(issues) >= 20:
            issues.append("tournament artifact cell validation stopped after 20 mismatches")
            break
    return issues


def _tournament_artifact_issues(
    payload: dict[str, Any] | None,
    path: Path,
    entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Return integrity issues for the opponent-pool tournament artifact."""

    if payload is None:
        return []

    entries = entries or []
    issues: list[str] = []
    if payload.get("environment") != SLIMEVOLLEY_ENV_ID:
        issues.append(
            f"tournament artifact environment {payload.get('environment')!r} does not match {SLIMEVOLLEY_ENV_ID}"
        )
    if payload.get("split") in RESERVED_TUNING_SPLITS:
        issues.append(f"tournament artifact uses reserved {payload.get('split')!r} split: {path}")
    if payload.get("split") != "dev":
        issues.append(f"tournament artifact split is not dev: {payload.get('split')!r}")
    participants = payload.get("participants")
    cells = payload.get("cells")
    standings = payload.get("standings")
    if not isinstance(participants, list) or not participants:
        issues.append("tournament artifact missing participants")
    else:
        unknown_participants = _unknown_references(participants, VALID_POLICY_REFERENCES)
        if unknown_participants:
            issues.append(f"tournament artifact references unknown participants: {unknown_participants}")
    if not isinstance(cells, list) or not cells:
        issues.append("tournament artifact missing cells")
    if not isinstance(standings, list) or not standings:
        issues.append("tournament artifact missing standings")
    if isinstance(participants, list) and isinstance(cells, list):
        expected_matchups = len(participants) * len(participants)
        if payload.get("matchup_count") != expected_matchups:
            issues.append(
                f"tournament artifact matchup_count {payload.get('matchup_count')} does not match participant matrix size {expected_matchups}"
            )
        if len(cells) != expected_matchups:
            issues.append(
                f"tournament artifact cells length {len(cells)} does not match participant matrix size {expected_matchups}"
            )
        observed_matchups = {
            (str(cell.get("policy")), str(cell.get("opponent")))
            for cell in cells
            if isinstance(cell, dict)
        }
        expected_pairs = {
            (str(policy), str(opponent))
            for policy in participants
            for opponent in participants
        }
        if observed_matchups != expected_pairs:
            issues.append("tournament artifact cells do not cover the full participant matrix")
        bad_cell_totals = [
            index
            for index, cell in enumerate(cells, start=1)
            if isinstance(cell, dict)
            and isinstance(cell.get("episodes"), int)
            and isinstance(cell.get("wins"), int)
            and isinstance(cell.get("losses"), int)
            and isinstance(cell.get("draws"), int)
            and cell["wins"] + cell["losses"] + cell["draws"] != cell["episodes"]
        ]
        if bad_cell_totals:
            issues.append(
                f"tournament artifact win/loss/draw totals do not match episodes for cells {bad_cell_totals[:5]}"
            )
        issues.extend(
            _tournament_cell_content_issues(
                entries=entries,
                cells=cells,
                entry_timestamps=payload.get("entry_timestamps"),
            )
        )
    if isinstance(participants, list) and isinstance(standings, list):
        standings_policies = {str(row.get("policy")) for row in standings if isinstance(row, dict)}
        if standings_policies != {str(participant) for participant in participants}:
            issues.append("tournament artifact standings do not cover all participants")
    return issues


def _ranges_overlap(left: range, right: range) -> bool:
    return left.start < right.stop and right.start < left.stop


def _generation_seed_values(
    split: str,
    seed_splits: dict[str, dict[str, Any]],
) -> list[int] | None:
    spec = seed_splits.get(split)
    if spec is None:
        return None
    return list(range(int(spec["start"]), int(spec["stop_exclusive"])))


def _generation_1_prior_ranges() -> dict[str, range]:
    return {
        "generation-1 dev": SEED_SPLITS["dev"],
        "generation-1 holdout": SEED_SPLITS["holdout"],
        "generation-1 audit": SEED_SPLITS["audit"],
    }


def _generation_2_prior_ranges() -> dict[str, range]:
    prior = _generation_1_prior_ranges()
    for split, spec in GENERATION_2_SEED_SPLITS.items():
        prior[f"generation-2 {split}"] = range(int(spec["start"]), int(spec["stop_exclusive"]))
    return prior


def _generation_3_prior_ranges() -> dict[str, range]:
    prior = _generation_2_prior_ranges()
    for split, spec in GENERATION_3_SEED_SPLITS.items():
        prior[f"generation-3 {split}"] = range(int(spec["start"]), int(spec["stop_exclusive"]))
    return prior


def _generation_ledger_issues(
    entries: list[dict[str, Any]],
    *,
    generation: int,
    seed_splits: dict[str, dict[str, Any]],
    prior_ranges: dict[str, range],
) -> list[str]:
    label = f"generation-{generation}"
    issues: list[str] = []
    if not entries:
        return [f"{label} ledger exists but has no entries"]
    for row_index, entry in enumerate(entries, start=1):
        split = str(entry.get("seed_range", {}).get("split", ""))
        policy_version = str(entry.get("policy_version", ""))
        opponent_name = str(entry.get("opponent_name", ""))
        if policy_version not in VALID_POLICY_REFERENCES:
            issues.append(
                f"{label} ledger row {row_index}: unknown SlimeVolley policy_version {policy_version!r}"
            )
        if opponent_name and opponent_name not in OPPONENT_POOL:
            issues.append(
                f"{label} ledger row {row_index}: unknown SlimeVolley opponent_name {opponent_name!r}"
            )
        for issue in validate_slimevolley_ledger_entry(entry):
            issues.append(f"{label} ledger row {row_index}: {issue}")
        issues.extend(
            issue.replace("ledger row", f"{label} ledger row", 1)
            for issue in _explicit_test_status_issues(entry, row_index)
        )

        expected_seeds = _generation_seed_values(split, seed_splits)
        seed_range = entry.get("seed_range", {})
        observed_seeds = seed_range.get("seeds")
        if expected_seeds is None:
            issues.append(f"{label} ledger row {row_index}: unknown {label} split {split!r}")
        elif observed_seeds != expected_seeds:
            issues.append(
                f"{label} ledger row {row_index}: {split} seeds do not match predeclared "
                f"{expected_seeds[0]}..{expected_seeds[-1]}"
            )
        if isinstance(observed_seeds, list) and all(isinstance(seed, int) for seed in observed_seeds):
            observed_range = range(min(observed_seeds), max(observed_seeds) + 1)
            for prior_name, prior_range in prior_ranges.items():
                if _ranges_overlap(observed_range, prior_range):
                    issues.append(f"{label} ledger row {row_index}: seeds overlap {prior_name}")

        change_type = entry.get("change_type")
        if split in RESERVED_TUNING_SPLITS and change_type in TUNING_CHANGE_TYPES:
            issues.append(
                f"{label} ledger row {row_index}: tuning change_type {change_type!r} uses reserved {split!r} split"
            )
        if split == "holdout":
            change_summary = str(entry.get("change_summary", ""))
            next_hypothesis = str(entry.get("next_hypothesis", ""))
            if "Final SlimeVolley holdout matchup" not in change_summary:
                issues.append(
                    f"{label} ledger row {row_index}: holdout row is not marked as a final SlimeVolley holdout matchup"
                )
            if "Do not tune on holdout results" not in next_hypothesis:
                issues.append(
                    f"{label} ledger row {row_index}: holdout row is missing the anti-tuning next_hypothesis"
                )
    return issues


def _generation_2_ledger_issues(entries: list[dict[str, Any]]) -> list[str]:
    return _generation_ledger_issues(
        entries,
        generation=2,
        seed_splits=GENERATION_2_SEED_SPLITS,
        prior_ranges=_generation_1_prior_ranges(),
    )


def _generation_3_ledger_issues(entries: list[dict[str, Any]]) -> list[str]:
    return _generation_ledger_issues(
        entries,
        generation=3,
        seed_splits=GENERATION_3_SEED_SPLITS,
        prior_ranges=_generation_2_prior_ranges(),
    )


def _generation_holdout_artifact_issues(
    *,
    generation: int,
    holdout_entries: list[dict[str, Any]],
    payload: dict[str, Any] | None,
    path: Path,
) -> list[str]:
    label = f"generation-{generation}"
    issues: list[str] = []
    if not holdout_entries and payload is None:
        return issues
    if holdout_entries and payload is None:
        return [f"{label} holdout rows exist but artifact is missing: {path}"]
    if payload is None:
        return issues
    if not holdout_entries:
        issues.append(f"{label} holdout artifact exists but ledger has no holdout rows: {path}")
    if payload.get("split") != "holdout":
        issues.append(f"{label} holdout artifact split is not holdout")
    if not payload.get("anti_tuning_note"):
        issues.append(f"{label} holdout artifact missing anti_tuning_note")
    matchup_count = payload.get("matchup_count")
    if holdout_entries and matchup_count != len(holdout_entries):
        issues.append(
            f"{label} holdout artifact matchup_count {matchup_count} does not match holdout ledger rows {len(holdout_entries)}"
        )
    payload_policies = payload.get("policies")
    payload_opponents = payload.get("opponents")
    if isinstance(payload_policies, list) and isinstance(payload_opponents, list):
        unknown_policies = _unknown_references(payload_policies, VALID_POLICY_REFERENCES)
        unknown_opponents = _unknown_references(payload_opponents, set(OPPONENT_POOL))
        if unknown_policies:
            issues.append(f"{label} holdout artifact references unknown policies: {unknown_policies}")
        if unknown_opponents:
            issues.append(f"{label} holdout artifact references unknown opponents: {unknown_opponents}")
        expected_matchups = {
            (str(policy), str(opponent))
            for policy in payload_policies
            for opponent in payload_opponents
        }
        observed_matchups = {
            (str(entry.get("policy_version")), str(entry.get("opponent_name")))
            for entry in holdout_entries
        }
        if holdout_entries and expected_matchups != observed_matchups:
            issues.append(f"{label} holdout artifact policy/opponent matrix does not match holdout ledger rows")
        if matchup_count != len(expected_matchups):
            issues.append(
                f"{label} holdout artifact matchup_count {matchup_count} does not match policy/opponent matrix size {len(expected_matchups)}"
            )
        issues.extend(
            f"{label} " + issue
            for issue in _holdout_cell_content_issues(
                holdout_entries=holdout_entries,
                cells=payload.get("cells"),
            )
        )
    else:
        issues.append(f"{label} holdout artifact missing policies/opponents matrix")
    return issues


def _generation_2_holdout_artifact_issues(
    *,
    holdout_entries: list[dict[str, Any]],
    payload: dict[str, Any] | None,
    path: Path,
) -> list[str]:
    return _generation_holdout_artifact_issues(
        generation=2,
        holdout_entries=holdout_entries,
        payload=payload,
        path=path,
    )


def _generation_artifact_issues(
    *,
    generation: int,
    ledger_path: Path,
    summary_path: Path,
    search_best_path: Path,
    tournament_path: Path,
    holdout_path: Path,
) -> tuple[list[str], list[str], list[dict[str, Any]], list[dict[str, str]]]:
    label = f"generation-{generation}"
    issues: list[str] = []
    warnings: list[str] = []
    entries: list[dict[str, Any]] = []
    summary_rows: list[dict[str, str]] = []

    if not ledger_path.exists():
        issues.append(f"missing {label} ledger: {ledger_path}")
        return issues, warnings, entries, summary_rows

    entries = read_entries(ledger_path)
    if generation == 3:
        issues.extend(_generation_3_ledger_issues(entries))
    else:
        issues.extend(_generation_2_ledger_issues(entries))
    summary_rows = _read_summary_rows(summary_path)
    if not summary_path.exists():
        issues.append(f"missing {label} summary CSV: {summary_path}")
    elif len(summary_rows) != len(entries):
        issues.append(
            f"{label} summary row count {len(summary_rows)} does not match ledger row count {len(entries)}"
        )
    else:
        issues.extend(
            f"{label} " + issue
            for issue in _summary_content_issues(entries, summary_rows)
        )

    search_best_payload = _read_json(search_best_path)
    if not search_best_path.exists():
        warnings.append(f"missing {label} scalar-search artifact: {search_best_path}")
    else:
        issues.extend(
            f"{label} " + issue
            for issue in _search_best_artifact_issues(search_best_payload, search_best_path, entries)
        )

    tournament_payload = _read_json(tournament_path)
    if not tournament_path.exists():
        warnings.append(f"missing {label} tournament artifact: {tournament_path}")
    else:
        issues.extend(
            f"{label} " + issue
            for issue in _tournament_artifact_issues(tournament_payload, tournament_path, entries)
        )

    holdout_entries = [
        entry for entry in entries
        if entry.get("seed_range", {}).get("split") == "holdout"
    ]
    holdout_payload = _read_json(holdout_path)
    issues.extend(
        _generation_holdout_artifact_issues(
            generation=generation,
            holdout_entries=holdout_entries,
            payload=holdout_payload,
            path=holdout_path,
        )
    )
    return issues, warnings, entries, summary_rows


def _generation_2_artifact_issues(
    *,
    ledger_path: Path,
    summary_path: Path,
    search_best_path: Path,
    tournament_path: Path,
    holdout_path: Path,
) -> tuple[list[str], list[str], list[dict[str, Any]], list[dict[str, str]]]:
    return _generation_artifact_issues(
        generation=2,
        ledger_path=ledger_path,
        summary_path=summary_path,
        search_best_path=search_best_path,
        tournament_path=tournament_path,
        holdout_path=holdout_path,
    )


def _generation_3_artifact_issues(
    *,
    ledger_path: Path,
    summary_path: Path,
    search_best_path: Path,
    tournament_path: Path,
    holdout_path: Path,
) -> tuple[list[str], list[str], list[dict[str, Any]], list[dict[str, str]]]:
    return _generation_artifact_issues(
        generation=3,
        ledger_path=ledger_path,
        summary_path=summary_path,
        search_best_path=search_best_path,
        tournament_path=tournament_path,
        holdout_path=holdout_path,
    )


def _generation_protocol_issues(
    payload: dict[str, Any] | None,
    report_text: str,
    *,
    generation: int = 2,
) -> list[str]:
    label = f"generation-{generation}"
    protocol_ids = {
        2: GENERATION_2_PROTOCOL_ID,
        3: GENERATION_3_PROTOCOL_ID,
        4: GENERATION_4_PROTOCOL_ID,
    }
    seed_split_by_generation = {
        2: GENERATION_2_SEED_SPLITS,
        3: GENERATION_3_SEED_SPLITS,
        4: GENERATION_4_SEED_SPLITS,
    }
    required_artifacts_by_generation = {
        2: {
            "search_best": "search_best_g2_dev.json",
            "round_robin": "round_robin_g2_dev.json",
            "holdout": "holdout_g2_final.json",
        },
        3: {
            "search_best": "search_best_g3_dev.json",
            "round_robin": "round_robin_g3_dev.json",
            "holdout": "holdout_g3_final.json",
        },
        4: {
            "search_best": "search_best_g4_dev.json",
            "round_robin": "round_robin_g4_dev.json",
            "holdout": "holdout_g4_final.json",
        },
    }
    required_commands_by_generation = {
        2: [
            "make slimevolley-protocol",
            "generation_2_trials.jsonl",
            "--seed-start 3000",
            "--seed-start 4000",
            "holdout_g2_final.json",
        ],
        3: [
            "make slimevolley-generation3-protocol",
            "generation_3_trials.jsonl",
            "--seed-start 6000",
            "--seed-start 7000",
            "holdout_g3_final.json",
        ],
        4: [
            "make slimevolley-generation4-protocol",
            "generation_4_trials.jsonl",
            "--seed-start 9000",
            "--seed-start 10000",
            "holdout_g4_final.json",
        ],
    }
    required_sections_by_generation = {
        2: REQUIRED_GENERATION_PROTOCOL_REPORT_SECTIONS,
        3: REQUIRED_GENERATION_3_PROTOCOL_REPORT_SECTIONS,
        4: REQUIRED_GENERATION_4_PROTOCOL_REPORT_SECTIONS,
    }
    required_snippets_by_generation = {
        2: REQUIRED_GENERATION_PROTOCOL_SNIPPETS,
        3: REQUIRED_GENERATION_3_PROTOCOL_SNIPPETS,
        4: REQUIRED_GENERATION_4_PROTOCOL_SNIPPETS,
    }
    if generation not in protocol_ids:
        return [f"unsupported SlimeVolley protocol generation: {generation}"]
    protocol_id = protocol_ids[generation]
    generation_key = f"generation_{generation}"
    seed_splits = seed_split_by_generation[generation]
    required_artifacts = required_artifacts_by_generation[generation]
    required_commands = required_commands_by_generation[generation]
    required_sections = required_sections_by_generation[generation]
    required_snippets = required_snippets_by_generation[generation]
    issues: list[str] = []
    if payload is None:
        return [f"{label} protocol JSON is missing or unreadable"]
    if payload.get("environment") != SLIMEVOLLEY_ENV_ID:
        issues.append(f"{label} protocol environment does not match SlimeVolley-v0")
    if payload.get("protocol_id") != protocol_id:
        issues.append(f"{label} protocol_id is not {protocol_id}")
    if payload.get("status") != GENERATION_PROTOCOL_STATUS:
        issues.append(f"{label} protocol status is not predeclared-not-run")

    if generation >= 3:
        expected_prior_locks = [
            ("slimevolley-g1", SEED_SPLITS["holdout"].start, SEED_SPLITS["holdout"].stop),
            ("slimevolley-g2", 4000, 4050),
        ]
        if generation >= 4:
            expected_prior_locks.append(("slimevolley-g3", 7000, 7050))
        prior_generations = payload.get("prior_generations")
        if not isinstance(prior_generations, list) or len(prior_generations) < len(expected_prior_locks):
            issues.append(f"{label} protocol missing prior_generations locks")
        else:
            by_id = {str(item.get("id")): item for item in prior_generations if isinstance(item, dict)}
            for prior_id, expected_start, expected_stop in expected_prior_locks:
                prior = by_id.get(prior_id)
                if not isinstance(prior, dict):
                    issues.append(f"{label} protocol missing {prior_id} prior lock")
                    continue
                holdout = prior.get("holdout_seeds")
                if not isinstance(holdout, dict) or holdout.get("start") != expected_start or holdout.get("stop_exclusive") != expected_stop:
                    issues.append(f"{label} protocol does not lock {prior_id} holdout seed range")
                if "do not tune" not in str(prior.get("rule", "")).lower():
                    issues.append(f"{label} protocol {prior_id} rule does not forbid tuning")
    else:
        source = payload.get("source_generation")
        if not isinstance(source, dict):
            issues.append("generation-2 protocol missing source_generation object")
        else:
            holdout = source.get("holdout_seeds")
            if not isinstance(holdout, dict) or holdout.get("start") != SEED_SPLITS["holdout"].start or holdout.get("stop_exclusive") != SEED_SPLITS["holdout"].stop:
                issues.append("generation-2 protocol does not lock the generation-1 holdout seed range")
            if "do not tune" not in str(source.get("rule", "")).lower():
                issues.append("generation-2 protocol source_generation rule does not forbid tuning on generation-1 holdout")

    generation_payload = payload.get(generation_key)
    if not isinstance(generation_payload, dict):
        issues.append(f"{label} protocol missing {generation_key} object")
        return issues
    if generation_payload.get("id") != protocol_id:
        issues.append(f"{generation_key}.id is not {protocol_id}")
    ledger_name = f"generation_{generation}_trials.jsonl"
    summary_name = f"generation_{generation}_summary.csv"
    if ledger_name not in str(generation_payload.get("ledger", "")):
        issues.append(f"{label} protocol does not use a fresh {ledger_name} ledger")
    if summary_name not in str(generation_payload.get("summary", "")):
        issues.append(f"{label} protocol does not use a fresh {summary_name} summary")

    observed_seed_splits = generation_payload.get("seed_splits")
    if not isinstance(observed_seed_splits, dict):
        issues.append(f"{label} protocol missing seed_splits")
    else:
        if generation == 4:
            prior_ranges = _generation_3_prior_ranges()
        elif generation == 3:
            prior_ranges = _generation_2_prior_ranges()
        else:
            prior_ranges = _generation_1_prior_ranges()
        for split, expected in seed_splits.items():
            observed = observed_seed_splits.get(split)
            if not isinstance(observed, dict):
                issues.append(f"{label} protocol missing seed split: {split}")
                continue
            start = observed.get("start")
            stop_exclusive = observed.get("stop_exclusive")
            if start != expected["start"] or stop_exclusive != expected["stop_exclusive"]:
                issues.append(
                    f"{label} {split} seed range {start}..{stop_exclusive} does not match predeclared {expected['start']}..{expected['stop_exclusive']}"
                )
                continue
            observed_range = range(int(start), int(stop_exclusive))
            for prior_name, prior_range in prior_ranges.items():
                if _ranges_overlap(observed_range, prior_range):
                    issues.append(f"{label} {split} seeds overlap {prior_name}")

    artifacts = generation_payload.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append(f"{label} protocol missing artifacts object")
    else:
        for key, required_name in required_artifacts.items():
            if required_name not in str(artifacts.get(key, "")):
                issues.append(f"{label} protocol artifact {key!r} does not use {required_name}")

    guardrails = " ".join(str(item) for item in payload.get("guardrails", []))
    guardrail_requirements_by_generation = {
        2: ["generation-2 ledger", "Do not inspect generation-2 holdout", "Do not use generation-1 holdout"],
        3: ["generation-3 ledger", "Do not inspect generation-3 holdout", "Do not use generation-1 or generation-2 holdout"],
        4: ["generation-4 ledger", "Do not inspect generation-4 holdout", "Do not use generation-1, generation-2, or generation-3 holdout"],
    }
    guardrail_requirements = guardrail_requirements_by_generation[generation]
    for required in guardrail_requirements:
        if required.lower() not in guardrails.lower():
            issues.append(f"{label} protocol guardrails missing: {required}")

    commands = payload.get("commands")
    if not isinstance(commands, dict):
        issues.append(f"{label} protocol missing commands object")
    else:
        command_text = " ".join(str(value) for value in commands.values())
        for required in required_commands:
            if required not in command_text:
                issues.append(f"{label} protocol commands missing: {required}")

    if not report_text:
        issues.append(f"{label} protocol Markdown report is missing or empty")
    else:
        for section in required_sections:
            if not _markdown_line_present(report_text, section):
                issues.append(f"{label} protocol report missing section: {section}")
        for snippet in required_snippets:
            if snippet not in report_text:
                issues.append(f"{label} protocol report missing required snippet: {snippet}")
    return issues


def audit_slimevolley_artifacts(
    *,
    ledger_path: Path = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    summary_path: Path = env_summary_path(SLIMEVOLLEY_ENV_ID),
    report_path: Path = env_report_path(SLIMEVOLLEY_ENV_ID),
    diagnostics_path: Path | None = None,
    holdout_path: Path | None = None,
    search_best_path: Path | None = None,
    tournament_path: Path | None = None,
    ledger_amendments_path: Path | None = None,
    requirements_audit_path: Path | None = None,
    experiment_readme_path: Path | None = None,
    performance_report_path: Path | None = None,
    generation_report_path: Path | None = None,
    generation_ledger_path: Path | None = None,
    generation_summary_path: Path | None = None,
    generation_search_best_path: Path | None = None,
    generation_tournament_path: Path | None = None,
    generation_holdout_path: Path | None = None,
    generation_protocol_path: Path | None = None,
    generation_protocol_report_path: Path | None = None,
    generation3_report_path: Path | None = None,
    generation3_ledger_path: Path | None = None,
    generation3_summary_path: Path | None = None,
    generation3_search_best_path: Path | None = None,
    generation3_tournament_path: Path | None = None,
    generation3_holdout_path: Path | None = None,
    generation3_protocol_path: Path | None = None,
    generation3_protocol_report_path: Path | None = None,
    generation4_protocol_path: Path | None = None,
    generation4_protocol_report_path: Path | None = None,
    contact_diagnostics_json_path: Path | None = None,
    contact_diagnostics_report_path: Path | None = None,
    require_holdout: bool = False,
) -> dict[str, Any]:
    """Return a machine-readable audit result for SlimeVolley artifacts."""

    if holdout_path is None:
        holdout_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json"
    if diagnostics_path is None:
        diagnostics_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "environment_diagnostics.json"
    if ledger_amendments_path is None:
        ledger_amendments_path = default_amendments_path(ledger_path)
    if search_best_path is None:
        search_best_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json"
    if tournament_path is None:
        tournament_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_dev.json"
    if requirements_audit_path is None:
        requirements_audit_path = report_path.with_name("requirements_audit.md")
    default_report_path = env_report_path(SLIMEVOLLEY_ENV_ID)
    canonical_report = report_path.resolve() == default_report_path.resolve()
    if experiment_readme_path is None and canonical_report:
        experiment_readme_path = PROJECT_ROOT / "experiments" / "slimevolley" / "README.md"
    if performance_report_path is None and canonical_report:
        performance_report_path = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "performance_deepdive.md"
    if generation_report_path is None and canonical_report:
        generation_report_path = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_diagnosis.md"
    if generation_ledger_path is None and canonical_report:
        generation_ledger_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_trials.jsonl"
    if generation_summary_path is None and canonical_report:
        generation_summary_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_summary.csv"
    if generation_search_best_path is None and canonical_report:
        generation_search_best_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g2_dev.json"
    if generation_tournament_path is None and canonical_report:
        generation_tournament_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g2_dev.json"
    if generation_holdout_path is None and canonical_report:
        generation_holdout_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g2_final.json"
    if generation_protocol_path is None and canonical_report:
        generation_protocol_path = env_configs_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_protocol.json"
    if generation_protocol_report_path is None and canonical_report:
        generation_protocol_report_path = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_protocol.md"
    if generation3_report_path is None and canonical_report:
        generation3_report_path = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_diagnosis.md"
    if generation3_ledger_path is None and canonical_report:
        generation3_ledger_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_trials.jsonl"
    if generation3_summary_path is None and canonical_report:
        generation3_summary_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_summary.csv"
    if generation3_search_best_path is None and canonical_report:
        generation3_search_best_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g3_dev.json"
    if generation3_tournament_path is None and canonical_report:
        generation3_tournament_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g3_dev.json"
    if generation3_holdout_path is None and canonical_report:
        generation3_holdout_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g3_final.json"
    if generation3_protocol_path is None and canonical_report:
        generation3_protocol_path = env_configs_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_protocol.json"
    if generation3_protocol_report_path is None and canonical_report:
        generation3_protocol_report_path = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_protocol.md"
    if generation4_protocol_path is None and canonical_report:
        generation4_protocol_path = env_configs_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_protocol.json"
    if generation4_protocol_report_path is None and canonical_report:
        generation4_protocol_report_path = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_protocol.md"
    if contact_diagnostics_json_path is None and canonical_report:
        contact_diagnostics_json_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "contact_diagnostics_g3_dev.json"
    if contact_diagnostics_report_path is None and canonical_report:
        contact_diagnostics_report_path = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "contact_diagnostics_g3_dev.md"

    issues: list[str] = []
    warnings: list[str] = []
    raw_entries: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    ledger_amendments: list[dict[str, Any]] = []
    ledger_amendment_counts = {
        "amendment_rows": 0,
        "applied_rows": 0,
        "applied_fields": 0,
        "tests_pass_fail_amended": 0,
    }
    if not ledger_path.exists():
        issues.append(f"missing ledger: {ledger_path}")
    else:
        raw_entries = read_entries(ledger_path)
        if not raw_entries:
            issues.append("ledger exists but has no entries")
        ledger_amendments = read_ledger_amendments(ledger_amendments_path)
        entries, amendment_issues, ledger_amendment_counts = apply_ledger_amendments(
            raw_entries,
            ledger_amendments,
            target_ledger=ledger_path.name,
        )
        issues.extend(amendment_issues)

    summary_rows = _read_summary_rows(summary_path)
    if not summary_path.exists():
        issues.append(f"missing summary CSV: {summary_path}")
    elif len(summary_rows) != len(entries):
        issues.append(
            f"summary row count {len(summary_rows)} does not match ledger row count {len(entries)}"
        )
    else:
        issues.extend(_summary_content_issues(entries, summary_rows))

    diagnostics_payload = _read_json(diagnostics_path)
    evidence_splits_requiring_available_diagnostics = {"dev", "holdout"}
    successful_evidence_rows = [
        entry
        for entry in entries
        if entry.get("pass_fail") == "pass"
        and entry.get("seed_range", {}).get("split") in evidence_splits_requiring_available_diagnostics
    ]
    if diagnostics_payload is None:
        issues.append(f"missing environment diagnostics: {diagnostics_path}")
    else:
        for field in REQUIRED_DIAGNOSTIC_FIELDS:
            if field not in diagnostics_payload:
                issues.append(f"environment diagnostics missing field: {field}")
        if diagnostics_payload.get("environment_id") not in {None, SLIMEVOLLEY_ENV_ID}:
            issues.append(
                f"environment diagnostics environment_id {diagnostics_payload.get('environment_id')!r} does not match {SLIMEVOLLEY_ENV_ID}"
            )
        diagnostics_packages = diagnostics_payload.get("packages")
        runtime_metadata = diagnostics_payload.get("runtime_metadata")
        runtime_packages: dict[str, Any] | None = None
        if not isinstance(diagnostics_packages, dict) or not diagnostics_packages:
            issues.append("environment diagnostics packages is missing or empty")
        if not isinstance(runtime_metadata, dict):
            issues.append("environment diagnostics runtime_metadata is missing or not an object")
        else:
            candidate_runtime_packages = runtime_metadata.get("packages")
            if not isinstance(runtime_metadata.get("python"), str) or not runtime_metadata.get("python"):
                issues.append("environment diagnostics runtime_metadata.python is missing")
            if not isinstance(runtime_metadata.get("platform"), str) or not runtime_metadata.get("platform"):
                issues.append("environment diagnostics runtime_metadata.platform is missing")
            if not isinstance(candidate_runtime_packages, dict) or not candidate_runtime_packages:
                issues.append("environment diagnostics runtime_metadata.packages is missing or empty")
            else:
                runtime_packages = candidate_runtime_packages
        if isinstance(diagnostics_packages, dict) and runtime_packages:
            for package_name, diagnostic_version in sorted(diagnostics_packages.items()):
                runtime_version = runtime_packages.get(package_name)
                if runtime_version is None:
                    issues.append(
                        f"environment diagnostics runtime_metadata.packages missing {package_name!r}"
                    )
                elif str(runtime_version) != str(diagnostic_version):
                    issues.append(
                        "environment diagnostics package mismatch for "
                        f"{package_name!r}: packages={diagnostic_version!r}, "
                        f"runtime_metadata.packages={runtime_version!r}"
                    )
        if diagnostics_payload.get("status") not in {"available", "unavailable"}:
            issues.append(
                f"environment diagnostics status {diagnostics_payload.get('status')!r} is not available/unavailable"
            )
        if diagnostics_payload.get("status") == "unavailable" and successful_evidence_rows:
            issues.append(
                "environment diagnostics are unavailable but successful dev/holdout SlimeVolley evidence exists"
            )
        if diagnostics_payload.get("status") == "available":
            if diagnostics_payload.get("has_seed_method") is not True:
                issues.append("environment diagnostics available env does not report has_seed_method=True")
            if diagnostics_payload.get("same_seed_reset_observation_equal") is not True:
                issues.append("environment diagnostics same-seed reset probe is not reproducible")
            if diagnostics_payload.get("observed_step_api") not in VALID_STEP_API_LABELS:
                issues.append(
                    f"environment diagnostics observed_step_api {diagnostics_payload.get('observed_step_api')!r} is not recognized"
                )
            if diagnostics_payload.get("multiagent_step_api_observed") not in VALID_STEP_API_LABELS:
                issues.append(
                    "environment diagnostics multiagent_step_api_observed "
                    f"{diagnostics_payload.get('multiagent_step_api_observed')!r} is not recognized"
                )
            if diagnostics_payload.get("max_episode_steps") != 3000:
                issues.append(
                    f"environment diagnostics max_episode_steps {diagnostics_payload.get('max_episode_steps')!r} does not match 3000"
                )

    for row_index, entry in enumerate(entries, start=1):
        split = entry.get("seed_range", {}).get("split")
        change_type = entry.get("change_type")
        policy_version = str(entry.get("policy_version", ""))
        opponent_name = str(entry.get("opponent_name", ""))
        if policy_version not in VALID_POLICY_REFERENCES:
            issues.append(f"ledger row {row_index}: unknown SlimeVolley policy_version {policy_version!r}")
        if opponent_name and opponent_name not in OPPONENT_POOL:
            issues.append(f"ledger row {row_index}: unknown SlimeVolley opponent_name {opponent_name!r}")
        for issue in validate_slimevolley_ledger_entry(entry):
            issues.append(f"ledger row {row_index}: {issue}")
        issues.extend(_explicit_test_status_issues(entry, row_index))
        if split in RESERVED_TUNING_SPLITS and change_type in TUNING_CHANGE_TYPES:
            issues.append(
                f"ledger row {row_index}: tuning change_type {change_type!r} uses reserved {split!r} split"
            )
        if split == "holdout":
            seed_range = entry.get("seed_range", {})
            if seed_range.get("seeds") != EXPECTED_HOLDOUT_SEEDS:
                issues.append(
                    f"ledger row {row_index}: holdout seeds do not match predeclared {EXPECTED_HOLDOUT_SEEDS[0]}..{EXPECTED_HOLDOUT_SEEDS[-1]}"
                )
            if entry.get("episodes") != len(EXPECTED_HOLDOUT_SEEDS):
                issues.append(
                    f"ledger row {row_index}: holdout episodes do not match {len(EXPECTED_HOLDOUT_SEEDS)} predeclared seeds"
                )
            change_summary = str(entry.get("change_summary", ""))
            next_hypothesis = str(entry.get("next_hypothesis", ""))
            if "Final SlimeVolley holdout matchup" not in change_summary:
                issues.append(
                    f"ledger row {row_index}: holdout row is not marked as a final SlimeVolley holdout matchup"
                )
            if "Do not tune on holdout results" not in next_hypothesis:
                issues.append(
                    f"ledger row {row_index}: holdout row is missing the anti-tuning next_hypothesis"
                )

    report_text = ""
    if not report_path.exists():
        issues.append(f"missing report: {report_path}")
    else:
        report_text = report_path.read_text(encoding="utf-8")
        for section in REQUIRED_REPORT_SECTIONS:
            if not _markdown_line_present(report_text, section):
                issues.append(f"report missing section: {section}")
        for snippet in REQUIRED_REPORT_SNIPPETS:
            if snippet not in report_text:
                issues.append(f"report missing required reproduction snippet: {snippet}")

    requirements_audit_text = ""
    requirements_audit_rows: list[dict[str, str]] = []
    if not requirements_audit_path.exists():
        issues.append(f"missing requirements audit: {requirements_audit_path}")
    else:
        requirements_audit_text = requirements_audit_path.read_text(encoding="utf-8")
        requirements_audit_rows = _requirements_audit_matrix_rows(requirements_audit_text)
        for section in REQUIRED_REQUIREMENTS_AUDIT_SECTIONS:
            if not _markdown_line_present(requirements_audit_text, section):
                issues.append(f"requirements audit missing section: {section}")
        for snippet in REQUIRED_REQUIREMENTS_AUDIT_SNIPPETS:
            if snippet not in requirements_audit_text:
                issues.append(f"requirements audit missing required snippet: {snippet}")
        issues.extend(_requirements_audit_matrix_issues(requirements_audit_text))

    experiment_readme_text = ""
    if experiment_readme_path is not None:
        if not experiment_readme_path.exists():
            issues.append(f"missing experiment README: {experiment_readme_path}")
        else:
            experiment_readme_text = experiment_readme_path.read_text(encoding="utf-8")
            for section in REQUIRED_EXPERIMENT_README_SECTIONS:
                if not _markdown_line_present(experiment_readme_text, section):
                    issues.append(f"experiment README missing section: {section}")
            for snippet in REQUIRED_EXPERIMENT_README_SNIPPETS:
                if snippet not in experiment_readme_text:
                    issues.append(f"experiment README missing required snippet: {snippet}")

    performance_report_text = ""
    if performance_report_path is not None:
        if not performance_report_path.exists():
            issues.append(f"missing performance report: {performance_report_path}")
        else:
            performance_report_text = performance_report_path.read_text(encoding="utf-8")
            for section in REQUIRED_PERFORMANCE_REPORT_SECTIONS:
                if not _markdown_line_present(performance_report_text, section):
                    issues.append(f"performance report missing section: {section}")
            for snippet in REQUIRED_PERFORMANCE_REPORT_SNIPPETS:
                if snippet not in performance_report_text:
                    issues.append(f"performance report missing required snippet: {snippet}")

    generation_report_text = ""
    if generation_report_path is not None:
        if not generation_report_path.exists():
            issues.append(f"missing generation-2 diagnosis report: {generation_report_path}")
        else:
            generation_report_text = generation_report_path.read_text(encoding="utf-8")
            for section in REQUIRED_GENERATION_REPORT_SECTIONS:
                if not _markdown_line_present(generation_report_text, section):
                    issues.append(f"generation-2 diagnosis report missing section: {section}")
            for snippet in REQUIRED_GENERATION_REPORT_SNIPPETS:
                if snippet not in generation_report_text:
                    issues.append(f"generation-2 diagnosis report missing required snippet: {snippet}")

    generation3_report_text = ""
    if generation3_report_path is not None:
        if not generation3_report_path.exists():
            issues.append(f"missing generation-3 diagnosis report: {generation3_report_path}")
        else:
            generation3_report_text = generation3_report_path.read_text(encoding="utf-8")
            for section in REQUIRED_GENERATION_3_REPORT_SECTIONS:
                if not _markdown_line_present(generation3_report_text, section):
                    issues.append(f"generation-3 diagnosis report missing section: {section}")
            for snippet in REQUIRED_GENERATION_3_REPORT_SNIPPETS:
                if snippet not in generation3_report_text:
                    issues.append(f"generation-3 diagnosis report missing required snippet: {snippet}")

    generation_protocol_payload = None
    generation_protocol_report_text = ""
    if generation_protocol_path is not None:
        if not generation_protocol_path.exists():
            issues.append(f"missing generation-2 protocol: {generation_protocol_path}")
        else:
            generation_protocol_payload = _read_json(generation_protocol_path)
    if generation_protocol_report_path is not None:
        if not generation_protocol_report_path.exists():
            issues.append(f"missing generation-2 protocol report: {generation_protocol_report_path}")
        else:
            generation_protocol_report_text = generation_protocol_report_path.read_text(encoding="utf-8")
    if generation_protocol_path is not None or generation_protocol_report_path is not None:
        issues.extend(_generation_protocol_issues(generation_protocol_payload, generation_protocol_report_text, generation=2))

    generation3_protocol_payload = None
    generation3_protocol_report_text = ""
    if generation3_protocol_path is not None:
        if not generation3_protocol_path.exists():
            issues.append(f"missing generation-3 protocol: {generation3_protocol_path}")
        else:
            generation3_protocol_payload = _read_json(generation3_protocol_path)
    if generation3_protocol_report_path is not None:
        if not generation3_protocol_report_path.exists():
            issues.append(f"missing generation-3 protocol report: {generation3_protocol_report_path}")
        else:
            generation3_protocol_report_text = generation3_protocol_report_path.read_text(encoding="utf-8")
    if generation3_protocol_path is not None or generation3_protocol_report_path is not None:
        issues.extend(_generation_protocol_issues(generation3_protocol_payload, generation3_protocol_report_text, generation=3))

    generation4_protocol_payload = None
    generation4_protocol_report_text = ""
    if generation4_protocol_path is not None:
        if not generation4_protocol_path.exists():
            issues.append(f"missing generation-4 protocol: {generation4_protocol_path}")
        else:
            generation4_protocol_payload = _read_json(generation4_protocol_path)
    if generation4_protocol_report_path is not None:
        if not generation4_protocol_report_path.exists():
            issues.append(f"missing generation-4 protocol report: {generation4_protocol_report_path}")
        else:
            generation4_protocol_report_text = generation4_protocol_report_path.read_text(encoding="utf-8")
    if generation4_protocol_path is not None or generation4_protocol_report_path is not None:
        issues.extend(_generation_protocol_issues(generation4_protocol_payload, generation4_protocol_report_text, generation=4))

    generation_entries: list[dict[str, Any]] = []
    generation_summary_rows: list[dict[str, str]] = []
    generation_holdout_entries: list[dict[str, Any]] = []
    if generation_ledger_path is not None:
        if generation_summary_path is None:
            issues.append("generation-2 summary path is not configured")
        elif generation_search_best_path is None:
            issues.append("generation-2 scalar-search path is not configured")
        elif generation_tournament_path is None:
            issues.append("generation-2 tournament path is not configured")
        elif generation_holdout_path is None:
            issues.append("generation-2 holdout path is not configured")
        else:
            generation_issues, generation_warnings, generation_entries, generation_summary_rows = (
                _generation_2_artifact_issues(
                    ledger_path=generation_ledger_path,
                    summary_path=generation_summary_path,
                    search_best_path=generation_search_best_path,
                    tournament_path=generation_tournament_path,
                    holdout_path=generation_holdout_path,
                )
            )
            issues.extend(generation_issues)
            warnings.extend(generation_warnings)
            generation_holdout_entries = [
                entry for entry in generation_entries
                if entry.get("seed_range", {}).get("split") == "holdout"
            ]

    generation3_entries: list[dict[str, Any]] = []
    generation3_summary_rows: list[dict[str, str]] = []
    generation3_holdout_entries: list[dict[str, Any]] = []
    if generation3_ledger_path is not None:
        if generation3_summary_path is None:
            issues.append("generation-3 summary path is not configured")
        elif generation3_search_best_path is None:
            issues.append("generation-3 scalar-search path is not configured")
        elif generation3_tournament_path is None:
            issues.append("generation-3 tournament path is not configured")
        elif generation3_holdout_path is None:
            issues.append("generation-3 holdout path is not configured")
        else:
            generation3_issues, generation3_warnings, generation3_entries, generation3_summary_rows = (
                _generation_3_artifact_issues(
                    ledger_path=generation3_ledger_path,
                    summary_path=generation3_summary_path,
                    search_best_path=generation3_search_best_path,
                    tournament_path=generation3_tournament_path,
                    holdout_path=generation3_holdout_path,
                )
            )
            issues.extend(generation3_issues)
            warnings.extend(generation3_warnings)
            generation3_holdout_entries = [
                entry for entry in generation3_entries
                if entry.get("seed_range", {}).get("split") == "holdout"
            ]

    split_counts = Counter(str(entry.get("seed_range", {}).get("split", "")) for entry in entries)
    pass_fail_counts = Counter(str(entry.get("pass_fail", "")) for entry in entries)
    tests_pass_fail_counts = Counter(
        str(entry.get("tests_pass_fail", "legacy_missing")) for entry in entries
    )
    change_type_counts = Counter(str(entry.get("change_type", "")) for entry in entries)
    holdout_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") == "holdout"]
    noncanonical_change_types = sorted(
        change_type
        for change_type in change_type_counts
        if change_type and change_type not in CANONICAL_CHANGE_TYPES
    )
    if noncanonical_change_types:
        warnings.append(
            "noncanonical change_type values remain append-only: "
            + ", ".join(noncanonical_change_types)
        )
    raw_tests_pass_fail_counts = Counter(
        str(entry.get("tests_pass_fail", "legacy_missing")) for entry in raw_entries
    )
    if raw_tests_pass_fail_counts.get("legacy_missing", 0):
        if ledger_amendment_counts.get("tests_pass_fail_amended", 0) >= raw_tests_pass_fail_counts["legacy_missing"]:
            warnings.append(
                "legacy rows missing tests_pass_fail are covered by append-only amendments: "
                + str(raw_tests_pass_fail_counts["legacy_missing"])
            )
        else:
            issues.append(
                "legacy rows missing tests_pass_fail are not fully covered by append-only amendments: "
                + str(raw_tests_pass_fail_counts["legacy_missing"])
            )

    holdout_payload = _read_json(holdout_path)
    if require_holdout and not holdout_entries:
        issues.append("holdout rows are required but absent")
    if holdout_entries and holdout_payload is None:
        issues.append(f"holdout rows exist but artifact is missing: {holdout_path}")
    if holdout_payload is not None:
        if holdout_payload.get("split") != "holdout":
            issues.append("holdout artifact split is not holdout")
        matchup_count = holdout_payload.get("matchup_count")
        if holdout_entries and matchup_count != len(holdout_entries):
            issues.append(
                f"holdout artifact matchup_count {matchup_count} does not match holdout ledger rows {len(holdout_entries)}"
            )
        if not holdout_payload.get("anti_tuning_note"):
            issues.append("holdout artifact missing anti_tuning_note")
        payload_policies = holdout_payload.get("policies")
        payload_opponents = holdout_payload.get("opponents")
        if isinstance(payload_policies, list) and isinstance(payload_opponents, list):
            unknown_policies = _unknown_references(payload_policies, VALID_POLICY_REFERENCES)
            unknown_opponents = _unknown_references(payload_opponents, set(OPPONENT_POOL))
            if unknown_policies:
                issues.append(f"holdout artifact references unknown policies: {unknown_policies}")
            if unknown_opponents:
                issues.append(f"holdout artifact references unknown opponents: {unknown_opponents}")
            expected_matchups = {
                (str(policy), str(opponent))
                for policy in payload_policies
                for opponent in payload_opponents
            }
            observed_matchups = {
                (str(entry.get("policy_version")), str(entry.get("opponent_name")))
                for entry in holdout_entries
            }
            if expected_matchups != observed_matchups:
                issues.append("holdout artifact policy/opponent matrix does not match holdout ledger rows")
            if matchup_count != len(expected_matchups):
                issues.append(
                    f"holdout artifact matchup_count {matchup_count} does not match policy/opponent matrix size {len(expected_matchups)}"
                )
            issues.extend(
                _holdout_cell_content_issues(
                    holdout_entries=holdout_entries,
                    cells=holdout_payload.get("cells"),
                )
            )
        else:
            issues.append("holdout artifact missing policies/opponents matrix")

    search_best_payload = _read_json(search_best_path)
    if not search_best_path.exists():
        warnings.append(f"missing scalar-search artifact: {search_best_path}")
    else:
        issues.extend(_search_best_artifact_issues(search_best_payload, search_best_path, entries))

    tournament_payload = _read_json(tournament_path)
    if not tournament_path.exists():
        warnings.append(f"missing tournament artifact: {tournament_path}")
    else:
        issues.extend(_tournament_artifact_issues(tournament_payload, tournament_path, entries))
    if report_text and holdout_entries and "final-only" not in report_text:
        issues.append("report does not mark holdout evidence as final-only")
    if report_text and generation_holdout_entries:
        for snippet in (
            "Primary evidence source for this verdict",
            "generation-2 holdout",
            "generation-3",
            "4000..4049",
        ):
            if snippet not in report_text:
                issues.append(f"report missing generation-2 holdout verdict snippet: {snippet}")

    requirements_audit_completion_blockers = [
        row["requirement"]
        for row in requirements_audit_rows
        if row["status"] != "Satisfied"
    ]
    if not requirements_audit_rows:
        requirements_audit_completion_state = "unknown"
    elif requirements_audit_completion_blockers:
        requirements_audit_completion_state = "partial"
    else:
        requirements_audit_completion_state = "satisfied"
    requirements_audit_completion_recommendation = (
        "eligible_for_completion_audit"
        if requirements_audit_completion_state == "satisfied"
        else "keep_goal_active"
    )
    requirements_audit_partial_row_details = []
    for requirement in requirements_audit_completion_blockers:
        detail = REQUIREMENTS_AUDIT_PARTIAL_ROW_DETAILS.get(requirement)
        if detail is None:
            continue
        requirements_audit_partial_row_details.append(
            {
                "requirement": requirement,
                **detail,
            }
        )
    requirements_audit_partial_row_classifications = {
        row["requirement"]: row["classification"]
        for row in requirements_audit_partial_row_details
    }

    return {
        "pass_fail": "pass" if not issues else "fail",
        "issues": issues,
        "warnings": warnings,
        "ledger_path": str(ledger_path),
        "summary_path": str(summary_path),
        "ledger_amendments_path": str(ledger_amendments_path),
        "ledger_amendment_rows": len(ledger_amendments),
        "ledger_amendment_counts": ledger_amendment_counts,
        "raw_tests_pass_fail_counts": dict(sorted(raw_tests_pass_fail_counts.items())),
        "report_path": str(report_path),
        "diagnostics_path": str(diagnostics_path),
        "diagnostics_status": diagnostics_payload.get("status") if diagnostics_payload else None,
        "artifact_hashes": _artifact_hashes(
            ledger_path=ledger_path,
            summary_path=summary_path,
            report_path=report_path,
            diagnostics_path=diagnostics_path,
            holdout_path=holdout_path,
            search_best_path=search_best_path,
            tournament_path=tournament_path,
            ledger_amendments_path=ledger_amendments_path,
            requirements_audit_path=requirements_audit_path,
            experiment_readme_path=experiment_readme_path,
            performance_report_path=performance_report_path,
            generation_report_path=generation_report_path,
            generation_ledger_path=generation_ledger_path,
            generation_summary_path=generation_summary_path,
            generation_search_best_path=generation_search_best_path,
            generation_tournament_path=generation_tournament_path,
            generation_holdout_path=generation_holdout_path,
            generation_protocol_path=generation_protocol_path,
            generation_protocol_report_path=generation_protocol_report_path,
            generation3_report_path=generation3_report_path,
            generation3_ledger_path=generation3_ledger_path,
            generation3_summary_path=generation3_summary_path,
            generation3_search_best_path=generation3_search_best_path,
            generation3_tournament_path=generation3_tournament_path,
            generation3_holdout_path=generation3_holdout_path,
            generation3_protocol_path=generation3_protocol_path,
            generation3_protocol_report_path=generation3_protocol_report_path,
            generation4_protocol_path=generation4_protocol_path,
            generation4_protocol_report_path=generation4_protocol_report_path,
            contact_diagnostics_json_path=contact_diagnostics_json_path,
            contact_diagnostics_report_path=contact_diagnostics_report_path,
        ),
        "requirements_audit_path": str(requirements_audit_path),
        "requirements_audit_rows": requirements_audit_rows,
        "requirements_audit_row_count": len(requirements_audit_rows),
        "requirements_audit_required_row_count": len(REQUIRED_REQUIREMENTS_AUDIT_ROW_STATUSES),
        "requirements_audit_status_counts": dict(
            sorted(Counter(row["status"] for row in requirements_audit_rows).items())
        ),
        "requirements_audit_partial_rows": [
            row["requirement"]
            for row in requirements_audit_rows
            if row["status"] == "Partial"
        ],
        "requirements_audit_completion_state": requirements_audit_completion_state,
        "requirements_audit_completion_recommendation": requirements_audit_completion_recommendation,
        "requirements_audit_completion_blockers": requirements_audit_completion_blockers,
        "requirements_audit_partial_row_details": requirements_audit_partial_row_details,
        "requirements_audit_partial_row_classifications": requirements_audit_partial_row_classifications,
        "experiment_readme_path": str(experiment_readme_path) if experiment_readme_path is not None else None,
        "performance_report_path": str(performance_report_path) if performance_report_path is not None else None,
        "generation_report_path": str(generation_report_path) if generation_report_path is not None else None,
        "generation_ledger_path": str(generation_ledger_path) if generation_ledger_path is not None else None,
        "generation_summary_path": str(generation_summary_path) if generation_summary_path is not None else None,
        "generation_search_best_path": str(generation_search_best_path) if generation_search_best_path is not None else None,
        "generation_tournament_path": str(generation_tournament_path) if generation_tournament_path is not None else None,
        "generation_holdout_path": str(generation_holdout_path) if generation_holdout_path is not None else None,
        "generation_protocol_path": str(generation_protocol_path) if generation_protocol_path is not None else None,
        "generation_protocol_report_path": str(generation_protocol_report_path) if generation_protocol_report_path is not None else None,
        "generation3_report_path": str(generation3_report_path) if generation3_report_path is not None else None,
        "generation3_ledger_path": str(generation3_ledger_path) if generation3_ledger_path is not None else None,
        "generation3_summary_path": str(generation3_summary_path) if generation3_summary_path is not None else None,
        "generation3_search_best_path": str(generation3_search_best_path) if generation3_search_best_path is not None else None,
        "generation3_tournament_path": str(generation3_tournament_path) if generation3_tournament_path is not None else None,
        "generation3_holdout_path": str(generation3_holdout_path) if generation3_holdout_path is not None else None,
        "generation3_protocol_path": str(generation3_protocol_path) if generation3_protocol_path is not None else None,
        "generation3_protocol_report_path": str(generation3_protocol_report_path) if generation3_protocol_report_path is not None else None,
        "generation4_protocol_path": str(generation4_protocol_path) if generation4_protocol_path is not None else None,
        "generation4_protocol_report_path": str(generation4_protocol_report_path) if generation4_protocol_report_path is not None else None,
        "generation4_protocol_status": (
            generation4_protocol_payload.get("status")
            if isinstance(generation4_protocol_payload, dict)
            else None
        ),
        "generation4_seed_ranges": _protocol_seed_range_labels(generation4_protocol_payload, 4),
        "contact_diagnostics_json_path": str(contact_diagnostics_json_path) if contact_diagnostics_json_path is not None else None,
        "contact_diagnostics_report_path": str(contact_diagnostics_report_path) if contact_diagnostics_report_path is not None else None,
        "source_hashes": _source_hashes(),
        "ledger_rows": len(entries),
        "summary_rows": len(summary_rows),
        "summary_content_checked": summary_path.exists() and len(summary_rows) == len(entries),
        "generation_ledger_rows": len(generation_entries),
        "generation_summary_rows": len(generation_summary_rows),
        "generation_summary_content_checked": (
            generation_summary_path is not None
            and generation_summary_path.exists()
            and len(generation_summary_rows) == len(generation_entries)
        ),
        "generation_split_counts": dict(sorted(Counter(str(entry.get("seed_range", {}).get("split", "")) for entry in generation_entries).items())),
        "generation_holdout_rows": len(generation_holdout_entries),
        "generation3_ledger_rows": len(generation3_entries),
        "generation3_summary_rows": len(generation3_summary_rows),
        "generation3_summary_content_checked": (
            generation3_summary_path is not None
            and generation3_summary_path.exists()
            and len(generation3_summary_rows) == len(generation3_entries)
        ),
        "generation3_split_counts": dict(sorted(Counter(str(entry.get("seed_range", {}).get("split", "")) for entry in generation3_entries).items())),
        "generation3_holdout_rows": len(generation3_holdout_entries),
        "split_counts": dict(sorted(split_counts.items())),
        "pass_fail_counts": dict(sorted(pass_fail_counts.items())),
        "tests_pass_fail_counts": dict(sorted(tests_pass_fail_counts.items())),
        "change_type_counts": dict(sorted(change_type_counts.items())),
        "noncanonical_change_types": noncanonical_change_types,
        "holdout_rows": len(holdout_entries),
        "holdout_artifact": str(holdout_path),
        "search_best_artifact": str(search_best_path),
        "tournament_artifact": str(tournament_path),
        "expected_holdout_seeds": EXPECTED_HOLDOUT_SEEDS,
        "reserved_tuning_splits": sorted(RESERVED_TUNING_SPLITS),
        "explicit_tests_pass_fail_required_after": EXPLICIT_TEST_STATUS_REQUIRED_AFTER_LABEL,
    }



def _protocol_seed_range_labels(payload: dict[str, Any] | None, generation: int) -> dict[str, str]:
    """Return split-to-label mappings for one generation protocol payload."""

    if not isinstance(payload, dict):
        return {}
    generation_payload = payload.get(f"generation_{generation}")
    if not isinstance(generation_payload, dict):
        return {}
    seed_splits = generation_payload.get("seed_splits")
    if not isinstance(seed_splits, dict):
        return {}
    labels: dict[str, str] = {}
    for split, spec in seed_splits.items():
        if not isinstance(spec, dict):
            continue
        label = spec.get("label")
        if isinstance(label, str) and label:
            labels[str(split)] = label
    return dict(sorted(labels.items()))



def render_audit_text(result: dict[str, Any]) -> str:
    """Render a compact human-readable artifact audit."""

    lines = [
        f"SlimeVolley artifact audit: {result['pass_fail']}",
        f"- Ledger rows: {result['ledger_rows']}",
        f"- Summary rows: {result['summary_rows']}",
        f"- Summary content checked: {result.get('summary_content_checked')}",
        f"- Diagnostics status: {result.get('diagnostics_status')}",
        f"- Artifact hashes recorded: {bool(result.get('artifact_hashes'))}",
        f"- Source hashes recorded: {bool(result.get('source_hashes'))}",
        f"- Reserved tuning splits: {result.get('reserved_tuning_splits')}",
        f"- Holdout rows: {result['holdout_rows']}",
        f"- Splits: {result['split_counts']}",
        f"- Generation-2 ledger rows: {result.get('generation_ledger_rows')}",
        f"- Generation-2 splits: {result.get('generation_split_counts')}",
        f"- Generation-3 ledger rows: {result.get('generation3_ledger_rows')}",
        f"- Generation-3 splits: {result.get('generation3_split_counts')}",
    ]
    if result.get("generation4_protocol_status"):
        lines.append(f"- Generation-4 protocol status: {result.get('generation4_protocol_status')}")
    if result.get("generation4_seed_ranges"):
        lines.append(f"- Generation-4 seed ranges: {result.get('generation4_seed_ranges')}")
    if result.get("requirements_audit_status_counts"):
        lines.append(
            f"- Requirements audit statuses: {result.get('requirements_audit_status_counts')}"
        )
    if result.get("requirements_audit_partial_rows"):
        lines.append(
            f"- Requirements audit partial rows: {result.get('requirements_audit_partial_rows')}"
        )
    if result.get("requirements_audit_completion_state"):
        lines.append(
            f"- Requirements audit completion state: {result.get('requirements_audit_completion_state')}"
        )
    if result.get("requirements_audit_completion_recommendation"):
        lines.append(
            f"- Requirements audit completion recommendation: {result.get('requirements_audit_completion_recommendation')}"
        )
    if result.get("requirements_audit_partial_row_classifications"):
        lines.append(
            f"- Requirements audit partial classifications: {result.get('requirements_audit_partial_row_classifications')}"
        )
    if result["issues"]:
        lines.append("- Issues:")
        lines.extend(f"  - {issue}" for issue in result["issues"])
    if result["warnings"]:
        lines.append("- Warnings:")
        lines.extend(f"  - {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--summary", type=Path, default=env_summary_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--report", type=Path, default=env_report_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument(
        "--diagnostics",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "environment_diagnostics.json",
    )
    parser.add_argument(
        "--holdout",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json",
    )
    parser.add_argument(
        "--search-best",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json",
    )
    parser.add_argument(
        "--tournament",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_dev.json",
    )
    parser.add_argument(
        "--ledger-amendments",
        type=Path,
        default=None,
        help="Optional append-only metadata amendment JSONL path; defaults beside the main ledger.",
    )
    parser.add_argument(
        "--requirements-audit",
        type=Path,
        default=None,
        help="Optional requirements-audit Markdown path; defaults to the report directory.",
    )
    parser.add_argument(
        "--experiment-readme",
        type=Path,
        default=None,
        help="Optional SlimeVolley experiment README path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--performance-report",
        type=Path,
        default=None,
        help="Optional performance deep-dive Markdown path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-report",
        type=Path,
        default=None,
        help="Optional generation-2 diagnosis Markdown path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-ledger",
        type=Path,
        default=None,
        help="Optional generation-2 ledger JSONL path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-summary",
        type=Path,
        default=None,
        help="Optional generation-2 summary CSV path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-search-best",
        type=Path,
        default=None,
        help="Optional generation-2 scalar-search artifact path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-tournament",
        type=Path,
        default=None,
        help="Optional generation-2 round-robin artifact path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-holdout",
        type=Path,
        default=None,
        help="Optional generation-2 holdout artifact path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-protocol",
        type=Path,
        default=None,
        help="Optional generation-2 protocol JSON path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation-protocol-report",
        type=Path,
        default=None,
        help="Optional generation-2 protocol Markdown path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-report",
        type=Path,
        default=None,
        help="Optional generation-3 diagnosis Markdown path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-ledger",
        type=Path,
        default=None,
        help="Optional generation-3 ledger JSONL path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-summary",
        type=Path,
        default=None,
        help="Optional generation-3 summary CSV path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-search-best",
        type=Path,
        default=None,
        help="Optional generation-3 scalar-search artifact path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-tournament",
        type=Path,
        default=None,
        help="Optional generation-3 round-robin artifact path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-holdout",
        type=Path,
        default=None,
        help="Optional generation-3 holdout artifact path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-protocol",
        type=Path,
        default=None,
        help="Optional generation-3 protocol JSON path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation3-protocol-report",
        type=Path,
        default=None,
        help="Optional generation-3 protocol Markdown path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation4-protocol",
        type=Path,
        default=None,
        help="Optional generation-4 protocol JSON path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--generation4-protocol-report",
        type=Path,
        default=None,
        help="Optional generation-4 protocol Markdown path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--contact-diagnostics-json",
        type=Path,
        default=None,
        help="Optional generation-3 contact diagnostics JSON path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument(
        "--contact-diagnostics-report",
        type=Path,
        default=None,
        help="Optional generation-3 contact diagnostics Markdown path; checked by default for the canonical SlimeVolley report.",
    )
    parser.add_argument("--require-holdout", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path for writing the machine-readable audit result as JSON.",
    )
    args = parser.parse_args()
    result = audit_slimevolley_artifacts(
        ledger_path=args.ledger,
        summary_path=args.summary,
        report_path=args.report,
        diagnostics_path=args.diagnostics,
        holdout_path=args.holdout,
        search_best_path=args.search_best,
        tournament_path=args.tournament,
        ledger_amendments_path=args.ledger_amendments,
        requirements_audit_path=args.requirements_audit,
        experiment_readme_path=args.experiment_readme,
        performance_report_path=args.performance_report,
        generation_report_path=args.generation_report,
        generation_ledger_path=args.generation_ledger,
        generation_summary_path=args.generation_summary,
        generation_search_best_path=args.generation_search_best,
        generation_tournament_path=args.generation_tournament,
        generation_holdout_path=args.generation_holdout,
        generation_protocol_path=args.generation_protocol,
        generation_protocol_report_path=args.generation_protocol_report,
        generation3_report_path=args.generation3_report,
        generation3_ledger_path=args.generation3_ledger,
        generation3_summary_path=args.generation3_summary,
        generation3_search_best_path=args.generation3_search_best,
        generation3_tournament_path=args.generation3_tournament,
        generation3_holdout_path=args.generation3_holdout,
        generation3_protocol_path=args.generation3_protocol,
        generation3_protocol_report_path=args.generation3_protocol_report,
        generation4_protocol_path=args.generation4_protocol,
        generation4_protocol_report_path=args.generation4_protocol_report,
        contact_diagnostics_json_path=args.contact_diagnostics_json,
        contact_diagnostics_report_path=args.contact_diagnostics_report,
        require_holdout=args.require_holdout,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_audit_text(result), end="")
    if result["pass_fail"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
