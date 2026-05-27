"""Append-only metadata amendments for the SlimeVolley trial ledger."""

from __future__ import annotations

import argparse
import json
import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Any

from hl_benchmark.ledger import read_entries, utc_now_iso
from hl_benchmark.slimevolley.schema import TESTS_PASS_FAIL_VALUES


AMENDMENT_TYPE = "slimevolley_ledger_metadata_amendment"
AMENDMENT_SCHEMA_VERSION = 1
AMENDABLE_FIELDS = {"tests_pass_fail"}
DEFAULT_AMENDMENT_FILENAME = "trial_amendments.jsonl"
DEFAULT_LEGACY_TEST_STATUS = "not_recorded"


def default_amendments_path(ledger_path: Path) -> Path:
    """Return the conventional amendment ledger path beside a trial ledger."""

    return ledger_path.with_name(DEFAULT_AMENDMENT_FILENAME)


def canonical_entry_hash(entry: dict[str, Any]) -> str:
    """Return a stable hash of a parsed ledger entry."""

    payload = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_ledger_amendments(path: Path) -> list[dict[str, Any]]:
    """Read amendment JSONL rows, returning an empty list when absent."""

    if not path.exists():
        return []
    amendments: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            amendments.append(row)
    return amendments


def build_legacy_tests_pass_fail_amendments(
    entries: list[dict[str, Any]],
    *,
    target_ledger: str,
    timestamp: str,
    value: str = DEFAULT_LEGACY_TEST_STATUS,
) -> list[dict[str, Any]]:
    """Build amendment rows for historical entries missing tests_pass_fail."""

    if value not in TESTS_PASS_FAIL_VALUES:
        raise ValueError(f"tests_pass_fail amendment value must be one of {sorted(TESTS_PASS_FAIL_VALUES)}")
    rows: list[dict[str, Any]] = []
    for row_index, entry in enumerate(entries, start=1):
        if "tests_pass_fail" in entry:
            continue
        rows.append(
            {
                "schema_version": AMENDMENT_SCHEMA_VERSION,
                "amendment_type": AMENDMENT_TYPE,
                "timestamp": timestamp,
                "target_ledger": target_ledger,
                "ledger_row_index": row_index,
                "ledger_entry_sha256": canonical_entry_hash(entry),
                "amended_fields": {"tests_pass_fail": value},
                "reason": "Historical generation-1 row predates the explicit tests_pass_fail field; preserve the original row and record that the test outcome was not separately recorded.",
                "evidence_limitation": "The original row remains authoritative for tests_run and pass_fail; this amendment does not infer a pass/fail result for the test command.",
            }
        )
    return rows


def append_missing_legacy_tests_pass_fail_amendments(
    *,
    ledger_path: Path,
    amendments_path: Path,
    timestamp: str | None = None,
    target_ledger: str | None = None,
    value: str = DEFAULT_LEGACY_TEST_STATUS,
) -> dict[str, Any]:
    """Append deterministic amendments for missing historical tests_pass_fail fields."""

    entries = read_entries(ledger_path)
    target = target_ledger or ledger_path.name
    stamp = timestamp or utc_now_iso()
    proposed = build_legacy_tests_pass_fail_amendments(
        entries,
        target_ledger=target,
        timestamp=stamp,
        value=value,
    )
    existing = read_ledger_amendments(amendments_path)
    existing_keys = {
        (
            row.get("ledger_row_index"),
            row.get("ledger_entry_sha256"),
            field,
        )
        for row in existing
        for field in (row.get("amended_fields") or {})
        if isinstance(row.get("amended_fields"), dict)
    }
    new_rows = [
        row for row in proposed
        if (
            row.get("ledger_row_index"),
            row.get("ledger_entry_sha256"),
            "tests_pass_fail",
        ) not in existing_keys
    ]
    if new_rows:
        amendments_path.parent.mkdir(parents=True, exist_ok=True)
        with amendments_path.open("a", encoding="utf-8") as handle:
            for row in new_rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
    return {
        "ledger_path": str(ledger_path),
        "amendments_path": str(amendments_path),
        "ledger_rows": len(entries),
        "existing_amendment_rows": len(existing),
        "new_amendment_rows": len(new_rows),
        "total_amendment_rows": len(existing) + len(new_rows),
    }


def apply_ledger_amendments(
    entries: list[dict[str, Any]],
    amendments: list[dict[str, Any]],
    *,
    target_ledger: str,
) -> tuple[list[dict[str, Any]], list[str], dict[str, int]]:
    """Return effective entries plus validation issues and amendment counts."""

    effective_entries = [deepcopy(entry) for entry in entries]
    issues: list[str] = []
    counts = {
        "amendment_rows": len(amendments),
        "applied_rows": 0,
        "applied_fields": 0,
        "tests_pass_fail_amended": 0,
    }
    applied_fields: set[tuple[int, str]] = set()

    for amendment_index, amendment in enumerate(amendments, start=1):
        prefix = f"ledger amendment row {amendment_index}"
        if amendment.get("schema_version") != AMENDMENT_SCHEMA_VERSION:
            issues.append(f"{prefix}: schema_version is not {AMENDMENT_SCHEMA_VERSION}")
        if amendment.get("amendment_type") != AMENDMENT_TYPE:
            issues.append(f"{prefix}: amendment_type is not {AMENDMENT_TYPE!r}")
        if amendment.get("target_ledger") != target_ledger:
            issues.append(f"{prefix}: target_ledger does not match {target_ledger!r}")
        row_index = amendment.get("ledger_row_index")
        if not isinstance(row_index, int) or isinstance(row_index, bool):
            issues.append(f"{prefix}: ledger_row_index is not an integer")
            continue
        if row_index < 1 or row_index > len(entries):
            issues.append(f"{prefix}: ledger_row_index is outside the ledger")
            continue
        expected_hash = canonical_entry_hash(entries[row_index - 1])
        if amendment.get("ledger_entry_sha256") != expected_hash:
            issues.append(f"{prefix}: ledger_entry_sha256 does not match row {row_index}")
            continue
        amended_fields = amendment.get("amended_fields")
        if not isinstance(amended_fields, dict) or not amended_fields:
            issues.append(f"{prefix}: amended_fields is missing or empty")
            continue
        row_applied = False
        for field, value in sorted(amended_fields.items()):
            field_key = (row_index, field)
            if field not in AMENDABLE_FIELDS:
                issues.append(f"{prefix}: field {field!r} is not amendable")
                continue
            if field_key in applied_fields:
                issues.append(f"{prefix}: duplicate amendment for row {row_index} field {field!r}")
                continue
            if field in entries[row_index - 1]:
                issues.append(f"{prefix}: field {field!r} already exists on row {row_index}")
                continue
            if field == "tests_pass_fail" and value not in TESTS_PASS_FAIL_VALUES:
                issues.append(f"{prefix}: tests_pass_fail value is not one of {sorted(TESTS_PASS_FAIL_VALUES)}")
                continue
            applied_fields.add(field_key)
            effective_entries[row_index - 1][field] = value
            counts["applied_fields"] += 1
            if field == "tests_pass_fail":
                counts["tests_pass_fail_amended"] += 1
            row_applied = True
        if row_applied:
            counts["applied_rows"] += 1
    return effective_entries, issues, counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--timestamp", default="2026-05-26T00:00:00+00:00")
    parser.add_argument("--value", default=DEFAULT_LEGACY_TEST_STATUS, choices=sorted(TESTS_PASS_FAIL_VALUES))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    amendments_path = args.output or default_amendments_path(args.ledger)
    result = append_missing_legacy_tests_pass_fail_amendments(
        ledger_path=args.ledger,
        amendments_path=amendments_path,
        timestamp=args.timestamp,
        value=args.value,
    )
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SlimeVolley ledger amendments: "
            f"new={result['new_amendment_rows']} total={result['total_amendment_rows']} "
            f"path={result['amendments_path']}"
        )


if __name__ == "__main__":
    main()
