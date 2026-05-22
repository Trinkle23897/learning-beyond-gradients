"""Append-only trial ledger utilities."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .envs import discover_runtime_metadata


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
DEFAULT_LEDGER_PATH = RESULTS_DIR / "trials.jsonl"
DEFAULT_SUMMARY_PATH = RESULTS_DIR / "summary.csv"


REQUIRED_FIELDS = {
    "timestamp",
    "environment",
    "policy_version",
    "git_commit",
    "diff_identifier",
    "config",
    "seed_range",
    "episodes",
    "score_stats",
    "environment_steps",
    "wall_clock_seconds",
    "tests_run",
    "pass_fail",
    "change_summary",
    "failure_analysis",
    "next_hypothesis",
    "change_type",
    "agent_iterations",
    "code_edits",
    "llm_cost",
    "runtime_metadata",
}


def utc_now_iso() -> str:
    """Return an audit-friendly UTC timestamp."""

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def git_commit() -> str:
    """Return the current git commit hash or an explicit unavailable marker."""

    return _run_git(["rev-parse", "--short", "HEAD"])


def diff_identifier() -> str:
    """Return a short hash of the current working tree diff."""

    diff = _run_git(["diff", "--", "."])
    if diff == "unavailable":
        return "unavailable"
    if not diff:
        return "clean"
    return hashlib.sha256(diff.encode("utf-8")).hexdigest()[:12]


def llm_cost_from_env() -> dict[str, Any]:
    """Return LLM accounting fields when available, otherwise explicit markers."""

    return {
        "calls": "unavailable",
        "prompt_tokens": "unavailable",
        "completion_tokens": "unavailable",
        "total_tokens": "unavailable",
        "source": "not exposed by local runtime",
    }


def validate_entry(entry: dict[str, Any]) -> None:
    """Validate the stable trial-ledger schema."""

    missing = sorted(REQUIRED_FIELDS.difference(entry))
    if missing:
        raise ValueError(f"ledger entry missing required fields: {missing}")
    score_stats = entry["score_stats"]
    for key in ["mean", "std", "median", "min", "max"]:
        if key not in score_stats:
            raise ValueError(f"score_stats missing {key!r}")
    seed_range = entry["seed_range"]
    for key in ["split", "start", "stop_exclusive", "seeds"]:
        if key not in seed_range:
            raise ValueError(f"seed_range missing {key!r}")


def append_entry(path: Path, entry: dict[str, Any]) -> None:
    """Append one JSONL entry and never mutate older entries."""

    validate_entry(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def read_entries(path: Path = DEFAULT_LEDGER_PATH) -> list[dict[str, Any]]:
    """Read all valid JSONL entries from a ledger."""

    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            entry = json.loads(stripped)
            try:
                validate_entry(entry)
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            entries.append(entry)
    return entries


def make_trial_entry(
    *,
    environment: str,
    policy_version: str,
    config: dict[str, Any],
    seed_split: str,
    seeds: list[int],
    episodes: int,
    score_stats: dict[str, float | None],
    environment_steps: int,
    wall_clock_seconds: float,
    tests_run: list[str],
    pass_fail: str,
    change_summary: str,
    failure_analysis: str,
    next_hypothesis: str,
    change_type: str,
    agent_iterations: int = 0,
    code_edits: int = 0,
    per_episode: list[dict[str, Any]] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Create a complete ledger entry for evaluation or search."""

    if seeds:
        start = min(seeds)
        stop = max(seeds) + 1
    else:
        start = None
        stop = None
    return {
        "timestamp": utc_now_iso(),
        "environment": environment,
        "policy_version": policy_version,
        "git_commit": git_commit(),
        "diff_identifier": diff_identifier(),
        "config": config,
        "seed_range": {
            "split": seed_split,
            "start": start,
            "stop_exclusive": stop,
            "seeds": seeds,
        },
        "episodes": episodes,
        "score_stats": score_stats,
        "environment_steps": environment_steps,
        "wall_clock_seconds": round(float(wall_clock_seconds), 6),
        "tests_run": tests_run,
        "pass_fail": pass_fail,
        "change_summary": change_summary,
        "failure_analysis": failure_analysis,
        "next_hypothesis": next_hypothesis,
        "change_type": change_type,
        "agent_iterations": agent_iterations,
        "code_edits": code_edits,
        "llm_cost": llm_cost_from_env(),
        "runtime_metadata": discover_runtime_metadata(),
        "per_episode": per_episode or [],
        "error": error,
    }


def score_value(entry: dict[str, Any], key: str) -> str:
    value = entry["score_stats"].get(key)
    if value is None:
        return ""
    return f"{float(value):.6g}"


def write_summary_csv(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    summary_path: Path = DEFAULT_SUMMARY_PATH,
) -> None:
    """Regenerate the CSV summary from the append-only ledger."""

    entries = read_entries(ledger_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "timestamp",
        "environment",
        "policy_version",
        "change_type",
        "split",
        "seed_start",
        "seed_stop_exclusive",
        "episodes",
        "mean",
        "std",
        "median",
        "min",
        "max",
        "environment_steps",
        "wall_clock_seconds",
        "pass_fail",
        "git_commit",
        "diff_identifier",
        "agent_iterations",
        "code_edits",
        "change_summary",
        "failure_analysis",
        "next_hypothesis",
    ]
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            seed_range = entry["seed_range"]
            writer.writerow(
                {
                    "timestamp": entry["timestamp"],
                    "environment": entry["environment"],
                    "policy_version": entry["policy_version"],
                    "change_type": entry["change_type"],
                    "split": seed_range["split"],
                    "seed_start": seed_range["start"],
                    "seed_stop_exclusive": seed_range["stop_exclusive"],
                    "episodes": entry["episodes"],
                    "mean": score_value(entry, "mean"),
                    "std": score_value(entry, "std"),
                    "median": score_value(entry, "median"),
                    "min": score_value(entry, "min"),
                    "max": score_value(entry, "max"),
                    "environment_steps": entry["environment_steps"],
                    "wall_clock_seconds": entry["wall_clock_seconds"],
                    "pass_fail": entry["pass_fail"],
                    "git_commit": entry["git_commit"],
                    "diff_identifier": entry["diff_identifier"],
                    "agent_iterations": entry["agent_iterations"],
                    "code_edits": entry["code_edits"],
                    "change_summary": entry["change_summary"],
                    "failure_analysis": entry["failure_analysis"],
                    "next_hypothesis": entry["next_hypothesis"],
                }
            )

