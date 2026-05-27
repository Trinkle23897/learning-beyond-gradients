"""CLI wrapper for regenerating the ledger summary CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import env_ledger_path, env_summary_path
from .ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH, write_summary_csv


def resolve_summary_paths(
    *,
    env_id: str | None,
    ledger_path: Path | None,
    summary_path: Path | None,
    env_artifacts: bool = False,
) -> tuple[Path, Path]:
    """Return ledger and summary paths for summary regeneration."""

    if env_artifacts:
        if env_id is None:
            raise ValueError("--env is required with --env-artifacts")
        return (
            ledger_path or env_ledger_path(env_id),
            summary_path or env_summary_path(env_id),
        )
    return (
        ledger_path or DEFAULT_LEDGER_PATH,
        summary_path or DEFAULT_SUMMARY_PATH,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", dest="env_id", default=None)
    parser.add_argument("--ledger", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument(
        "--env-artifacts",
        action="store_true",
        help="Regenerate summary from experiments/<env_slug>/results/trials.jsonl.",
    )
    args = parser.parse_args()
    try:
        ledger_path, summary_path = resolve_summary_paths(
            env_id=args.env_id,
            ledger_path=args.ledger,
            summary_path=args.summary,
            env_artifacts=args.env_artifacts,
        )
    except ValueError as exc:
        parser.error(str(exc))
    write_summary_csv(ledger_path, summary_path)
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()

