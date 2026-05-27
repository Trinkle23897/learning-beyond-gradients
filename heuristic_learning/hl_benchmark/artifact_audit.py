"""Audit generic per-environment artifacts without running evaluations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .artifacts import (
    env_ledger_path,
    env_report_path,
    env_results_dir,
    env_summary_path,
    experiment_artifact_layout_issues,
    experiment_dir,
)
from .envs import CUSTOM_ENV_SPECS, ENV_SPECS, KNOWN_ENV_SPECS
from .ledger import read_entries, write_summary_csv


def _sha256_file(path: Path) -> str:
    if not path.exists():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_summary_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _summary_matches_ledger(ledger_path: Path, summary_path: Path) -> bool:
    with tempfile.TemporaryDirectory() as tmpdir:
        expected_path = Path(tmpdir) / "summary.csv"
        write_summary_csv(ledger_path, expected_path)
        return summary_path.read_text(encoding="utf-8") == expected_path.read_text(
            encoding="utf-8"
        )


def _report_content_issues(env_id: str, report_path: Path) -> list[str]:
    text = report_path.read_text(encoding="utf-8")
    issues: list[str] = []
    expected_title = f"# Heuristic Learning Benchmark Report: {env_id}"
    if expected_title not in text:
        issues.append(f"report missing scoped title {expected_title!r}")
    expected_heading = f"### {env_id}"
    if expected_heading not in text:
        issues.append(f"report missing environment heading {expected_heading!r}")
    for other_env_id in ENV_SPECS:
        if other_env_id == env_id:
            continue
        if f"### {other_env_id}" in text:
            issues.append(f"report includes other environment heading {other_env_id!r}")
    return issues


def audit_environment_artifacts(
    env_id: str,
    *,
    ledger_path: Path | None = None,
    summary_path: Path | None = None,
    report_path: Path | None = None,
) -> dict[str, Any]:
    """Return a machine-readable audit for one generic environment artifact root."""

    ledger_path = ledger_path or env_ledger_path(env_id)
    summary_path = summary_path or env_summary_path(env_id)
    report_path = report_path or env_report_path(env_id)
    issues: list[str] = []
    warnings: list[str] = []
    entries: list[dict[str, Any]] = []
    summary_rows: list[dict[str, str]] = []
    summary_content_checked = False
    report_content_checked = False

    if env_id not in ENV_SPECS:
        if env_id in CUSTOM_ENV_SPECS:
            issues.append(
                f"generic artifact audit expects an active generic environment, got custom environment {env_id!r}; use `make custom-verify ENV={env_id}` or the environment-specific audit command"
            )
        elif env_id in KNOWN_ENV_SPECS:
            issues.append(
                f"generic artifact audit expects an active generic environment, got non-runnable environment {env_id!r}"
            )
        else:
            issues.append(
                f"generic artifact audit expects an active generic environment, got unregistered environment {env_id!r}"
            )
    issues.extend(experiment_artifact_layout_issues(env_id))

    if not ledger_path.exists():
        issues.append(f"missing ledger: {ledger_path}")
    else:
        try:
            entries = read_entries(ledger_path)
        except ValueError as exc:
            issues.append(str(exc))
        else:
            wrong_envs = sorted(
                {entry.get("environment") for entry in entries if entry.get("environment") != env_id}
            )
            if wrong_envs:
                issues.append(
                    "ledger contains rows for other environments: "
                    + ", ".join(str(value) for value in wrong_envs)
                )
            if not entries:
                warnings.append("ledger contains no rows")

    if not summary_path.exists():
        issues.append(f"missing summary: {summary_path}")
    else:
        summary_rows = _read_summary_rows(summary_path)
        wrong_summary_envs = sorted(
            {row.get("environment") for row in summary_rows if row.get("environment") != env_id}
        )
        if wrong_summary_envs:
            issues.append(
                "summary contains rows for other environments: "
                + ", ".join(str(value) for value in wrong_summary_envs)
            )
        if ledger_path.exists() and entries:
            summary_content_checked = True
            if not _summary_matches_ledger(ledger_path, summary_path):
                issues.append("summary.csv does not match ledger regeneration")
        if entries and len(summary_rows) != len(entries):
            issues.append(
                f"summary row count {len(summary_rows)} does not match ledger rows {len(entries)}"
            )

    if not report_path.exists():
        issues.append(f"missing report: {report_path}")
    else:
        report_content_checked = True
        issues.extend(_report_content_issues(env_id, report_path))

    artifact_hashes = {
        "ledger": _sha256_file(ledger_path),
        "summary": _sha256_file(summary_path),
        "report": _sha256_file(report_path),
    }
    return {
        "env_id": env_id,
        "pass_fail": "pass" if not issues else "fail",
        "issues": issues,
        "warnings": warnings,
        "artifact_dir": experiment_dir(env_id).as_posix(),
        "ledger_path": ledger_path.as_posix(),
        "summary_path": summary_path.as_posix(),
        "report_path": report_path.as_posix(),
        "ledger_exists": ledger_path.exists(),
        "summary_exists": summary_path.exists(),
        "report_exists": report_path.exists(),
        "ledger_rows": len(entries),
        "summary_rows": len(summary_rows),
        "summary_content_checked": summary_content_checked,
        "report_content_checked": report_content_checked,
        "artifact_hashes": artifact_hashes,
    }


def render_audit_text(result: dict[str, Any]) -> str:
    """Render a compact human-readable generic artifact audit."""

    lines = [f"Generic environment artifact audit: {result['pass_fail']}"]
    lines.extend(
        [
            f"- Environment: {result['env_id']}",
            f"- Artifact root: {result['artifact_dir']}",
            f"- Ledger rows: {result['ledger_rows']}",
            f"- Summary rows: {result['summary_rows']}",
            f"- Summary content checked: {result['summary_content_checked']}",
            f"- Report content checked: {result['report_content_checked']}",
            f"- Artifact hashes recorded: {all(value != 'missing' for value in result['artifact_hashes'].values())}",
        ]
    )
    if result.get("issues"):
        lines.append("- Issues:")
        lines.extend(f"  - {issue}" for issue in result["issues"])
    if result.get("warnings"):
        lines.append("- Warnings:")
        lines.extend(f"  - {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", required=True, dest="env_id")
    parser.add_argument("--ledger", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path for writing the machine-readable audit JSON.",
    )
    parser.add_argument(
        "--write-latest",
        action="store_true",
        help="Write experiments/<env_slug>/results/audit_latest.json.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    result = audit_environment_artifacts(
        args.env_id,
        ledger_path=args.ledger,
        summary_path=args.summary,
        report_path=args.report,
    )
    output_path = args.output
    if args.write_latest:
        output_path = env_results_dir(args.env_id) / "audit_latest.json"
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
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
