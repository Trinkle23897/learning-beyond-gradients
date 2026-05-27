"""Regenerate the SlimeVolley summary CSV from the append-only ledger."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_ledger_path, env_summary_path
from hl_benchmark.ledger import read_entries, write_summary_csv
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID
from hl_benchmark.slimevolley.amendments import (
    apply_ledger_amendments,
    default_amendments_path,
    read_ledger_amendments,
)


def _count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _row in csv.DictReader(handle))


def summarize_slimevolley_ledger(
    *,
    ledger_path: Path = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    summary_path: Path = env_summary_path(SLIMEVOLLEY_ENV_ID),
    amendments_path: Path | None = None,
) -> dict[str, Any]:
    """Regenerate the SlimeVolley CSV summary and return row counts."""

    if not ledger_path.exists():
        raise FileNotFoundError(f"missing SlimeVolley ledger: {ledger_path}")
    entries = read_entries(ledger_path)
    resolved_amendments_path = amendments_path or default_amendments_path(ledger_path)
    amendments = read_ledger_amendments(resolved_amendments_path)
    effective_entries, amendment_issues, amendment_counts = apply_ledger_amendments(
        entries,
        amendments,
        target_ledger=ledger_path.name,
    )
    if amendment_issues:
        raise ValueError("invalid SlimeVolley ledger amendments: " + "; ".join(amendment_issues[:5]))
    write_summary_csv(ledger_path, summary_path, entries=effective_entries)
    summary_rows = _count_csv_rows(summary_path)
    return {
        "ledger_path": str(ledger_path),
        "summary_path": str(summary_path),
        "amendments_path": str(resolved_amendments_path),
        "ledger_rows": len(entries),
        "summary_rows": summary_rows,
        "amendment_rows": amendment_counts["amendment_rows"],
        "amended_tests_pass_fail": amendment_counts["tests_pass_fail_amended"],
        "pass_fail": "pass" if summary_rows == len(entries) else "fail",
    }


def render_summary_text(result: dict[str, Any]) -> str:
    """Render a compact human-readable summary regeneration result."""

    lines = [
        f"SlimeVolley summary regeneration: {result['pass_fail']}",
        f"- Ledger rows: {result['ledger_rows']}",
        f"- Summary rows: {result['summary_rows']}",
        f"- Amendment rows: {result.get('amendment_rows', 0)}",
        f"- tests_pass_fail amendments: {result.get('amended_tests_pass_fail', 0)}",
        f"- Summary CSV: {result['summary_path']}",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--summary", type=Path, default=env_summary_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--amendments", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    result = summarize_slimevolley_ledger(
        ledger_path=args.ledger,
        summary_path=args.summary,
        amendments_path=args.amendments,
    )
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_summary_text(result), end="")
    if result["pass_fail"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
