"""CLI wrapper for regenerating the ledger summary CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from .ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH, write_summary_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    args = parser.parse_args()
    write_summary_csv(args.ledger, args.summary)
    print(f"wrote {args.summary}")


if __name__ == "__main__":
    main()

