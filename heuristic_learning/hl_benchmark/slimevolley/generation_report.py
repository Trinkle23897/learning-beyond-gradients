"""Generate SlimeVolley experiment-generation diagnosis reports from persisted rows."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_reports_dir, env_results_dir
from hl_benchmark.ledger import read_entries, score_value
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID, dependency_versions


DEFAULT_GENERATION_LEDGER_PATH = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_trials.jsonl"
DEFAULT_GENERATION_SUMMARY_PATH = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_summary.csv"
DEFAULT_GENERATION_HOLDOUT_PATH = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g2_final.json"
DEFAULT_GENERATION_REPORT_PATH = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_diagnosis.md"
DEFAULT_GENERATION_3_LEDGER_PATH = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_trials.jsonl"
DEFAULT_GENERATION_3_SUMMARY_PATH = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_summary.csv"
DEFAULT_GENERATION_3_HOLDOUT_PATH = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g3_final.json"
DEFAULT_GENERATION_3_REPORT_PATH = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_diagnosis.md"

GENERATION_REPORT_SECTIONS = (
    "## Status",
    "## Evidence Sources",
    "## Trial Rows",
    "## Failure Analysis",
    "## Dependency Status",
    "## Cost So Far",
    "## Holdout Lock",
    "## Next Action",
)


def _read_entries_if_present(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return read_entries(path)


def _shorten(value: Any, *, limit: int = 120) -> str:
    text = "" if value is None else str(value).replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _generation_label(generation: int) -> str:
    return f"generation-{generation}"


def _status_line(entries: list[dict[str, Any]], *, generation: int) -> str:
    label = _generation_label(generation).capitalize()
    if not entries:
        return (
            f"No {_generation_label(generation)} trial rows are present yet, so there is no "
            f"{_generation_label(generation)} performance claim."
        )
    counts = Counter(str(entry.get("pass_fail", "")) for entry in entries)
    if counts.get("pass", 0) == 0:
        return (
            f"{label} has `{len(entries)}` recorded trial row(s), all without "
            "successful environment episodes. This is setup/diagnostic evidence, not "
            "policy-performance evidence."
        )
    return (
        f"{label} has `{len(entries)}` recorded trial row(s): "
        f"`{counts.get('pass', 0)}` pass and `{counts.get('fail', 0)}` fail."
    )


def _evidence_source_lines(
    *,
    ledger_path: Path,
    summary_path: Path,
    holdout_path: Path,
    generation: int,
) -> list[str]:
    label = _generation_label(generation)
    holdout_note = (
        f"- {label.capitalize()} holdout evidence is present and is final-only; it must not be used for policy tuning."
        if holdout_path.exists()
        else f"- No {label} holdout evidence is used in this diagnosis."
    )
    return [
        f"- Ledger: `{ledger_path}` ({'present' if ledger_path.exists() else 'missing'})",
        f"- Summary CSV: `{summary_path}` ({'present' if summary_path.exists() else 'missing'})",
        f"- {label.capitalize()} holdout artifact: `{holdout_path}` ({'present' if holdout_path.exists() else 'missing'})",
        holdout_note,
    ]


def _trial_row_lines(entries: list[dict[str, Any]], *, generation: int) -> list[str]:
    if not entries:
        return [f"No {_generation_label(generation)} trial rows have been recorded."]
    lines = [
        "| Timestamp | Split | Seeds | Policy | Opponent | Pass/fail | Episodes | Steps | Mean | W/L/D | Failure note |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for entry in entries:
        seed_range = entry.get("seed_range", {})
        start = seed_range.get("start")
        stop_exclusive = seed_range.get("stop_exclusive")
        seed_label = (
            f"{start}..{int(stop_exclusive) - 1}"
            if isinstance(start, int) and isinstance(stop_exclusive, int) and stop_exclusive > start
            else ""
        )
        wld = entry.get("win_loss_draw", {})
        lines.append(
            "| {timestamp} | {split} | {seeds} | {policy} | {opponent} | {pass_fail} | {episodes} | {steps} | {mean} | {wld} | {failure} |".format(
                timestamp=_shorten(entry.get("timestamp"), limit=32),
                split=seed_range.get("split", ""),
                seeds=seed_label,
                policy=entry.get("policy_version", ""),
                opponent=entry.get("opponent_name", ""),
                pass_fail=entry.get("pass_fail", ""),
                episodes=entry.get("episodes", ""),
                steps=entry.get("environment_steps", ""),
                mean=score_value(entry, "mean"),
                wld=f"{wld.get('wins', '')}/{wld.get('losses', '')}/{wld.get('draws', '')}",
                failure=_shorten(entry.get("failure_analysis")),
            )
        )
    return lines


def _failure_analysis_lines(entries: list[dict[str, Any]], *, generation: int) -> list[str]:
    failed_entries = [entry for entry in entries if entry.get("pass_fail") == "fail"]
    if not failed_entries:
        return [f"No {_generation_label(generation)} failed trial rows are recorded."]
    lines = [
        "Failed rows remain append-only evidence. They should be fixed by later rows, not deleted.",
        "",
    ]
    for index, entry in enumerate(failed_entries, start=1):
        lines.append(
            f"- Failure {index}: `{entry.get('policy_version', '')}` vs "
            f"`{entry.get('opponent_name', '')}` on split "
            f"`{entry.get('seed_range', {}).get('split', '')}` recorded "
            f"`{entry.get('environment_steps', 0)}` environment steps. "
            f"Failure analysis: {_shorten(entry.get('failure_analysis'), limit=240)}"
        )
    return lines


def _dependency_status_lines(entries: list[dict[str, Any]], *, generation: int) -> list[str]:
    observed = dependency_versions()
    label = _generation_label(generation)
    lines = [
        "Report-generator runtime dependency snapshot:",
        "",
        "| Package | Version |",
        "| --- | --- |",
    ]
    for package, version in sorted(observed.items()):
        lines.append(f"| {package} | `{version}` |")
    latest = entries[-1] if entries else {}
    config_versions = latest.get("config", {}).get("dependency_versions", {})
    if isinstance(config_versions, dict) and config_versions:
        lines.extend(
            [
                "",
                f"Latest {label} evaluation runtime dependency snapshot:",
                "",
                "| Package | Ledger version |",
                "| --- | --- |",
            ]
        )
        for package, version in sorted(config_versions.items()):
            lines.append(f"| {package} | `{version}` |")
    return lines


def _cost_lines(entries: list[dict[str, Any]]) -> list[str]:
    total_steps = sum(int(entry.get("environment_steps") or 0) for entry in entries)
    total_episodes = sum(int(entry.get("episodes") or 0) for entry in entries)
    total_wall_clock = sum(float(entry.get("wall_clock_seconds") or 0.0) for entry in entries)
    max_iterations = max((int(entry.get("agent_iterations") or 0) for entry in entries), default=0)
    code_edit_values = [int(entry.get("code_edits") or 0) for entry in entries]
    max_code_edits = max(code_edit_values, default=0)
    row_summed_code_edits = sum(code_edit_values)
    test_counts = Counter(str(entry.get("tests_pass_fail", "legacy_missing")) for entry in entries)
    return [
        f"- Trial rows: `{len(entries)}`",
        f"- Episodes requested/recorded: `{total_episodes}`",
        f"- Environment steps: `{total_steps}`",
        f"- Wall-clock seconds: `{total_wall_clock:.6g}`",
        f"- Agent iterations recorded: `{max_iterations}`",
        f"- Code edits recorded as max cumulative count: `{max_code_edits}`",
        f"- Code-edit row sum, which can double-count one edit evaluated across opponents: `{row_summed_code_edits}`",
        f"- Test status counts: `{dict(sorted(test_counts.items()))}`",
        "- LLM token accounting: unavailable from the local Codex runtime unless entered manually in ledger rows.",
    ]


def _next_action_lines(entries: list[dict[str, Any]], *, generation: int) -> list[str]:
    label = _generation_label(generation)
    protocol_name = f"generation_{generation}_protocol.md"
    ledger_name = f"generation_{generation}_trials.jsonl"
    holdout_name = f"holdout_g{generation}_final.json"
    dev_start = "3000" if generation == 2 else "6000"
    dev_stop = "3049" if generation == 2 else "6049"

    if not entries:
        return [
            "1. Run `make slimevolley-doctor` as a preflight check.",
            f"2. Run the {label} development trace command from `{protocol_name}`.",
            f"3. Keep all failures in `{ledger_name}`.",
            f"4. Do not inspect {label} holdout until policy code, scalar config, opponent pool, and tests are frozen.",
        ]

    if any(entry.get("seed_range", {}).get("split") == "holdout" for entry in entries):
        return [
            f"1. Treat {label} holdout rows as final evidence only; do not tune current policy/config/opponents on them.",
            f"2. Use this diagnosis, `{holdout_name}`, and audit hashes to write conclusions and limitations.",
            f"3. If more policy work is needed, predeclare a fresh generation with new seeds before any further tuning.",
            "4. Preserve all failed, dev, scalar-search, tournament, and holdout rows append-only.",
        ]

    latest = entries[-1]
    latest_failure = str(latest.get("failure_analysis", ""))
    if latest.get("pass_fail") == "fail" and (
        "SlimeVolleyDependencyError" in latest_failure
        or "optional legacy dependencies" in latest_failure
    ):
        return [
            "1. Install or activate the optional legacy SlimeVolley stack (`gym` and `slimevolleygym`) using the pinned project extra.",
            "2. Rerun `make slimevolley-doctor` and keep the diagnostics artifact.",
            f"3. Rerun the {label} development trace against the built-in opponent on seeds `{dev_start}..{dev_stop}`.",
            f"4. Do not inspect {label} holdout until policy code, scalar config, opponent pool, and tests are frozen.",
        ]

    if latest.get("pass_fail") == "fail":
        return [
            f"1. Diagnose the latest failed {label} row before making another policy edit.",
            "2. Record a replacement row rather than deleting the failed row.",
            "3. Rerun regression tests before another development evaluation.",
            f"4. Do not inspect {label} holdout until policy code, scalar config, opponent pool, and tests are frozen.",
        ]

    return [
        f"1. Inspect {label} development traces and point events from the latest passing rows.",
        "2. Compare any structural change against scalar search and the opponent-pool tournament on development seeds.",
        "3. Rerun regression tests before another development evaluation.",
        f"4. Do not inspect {label} holdout until policy code, scalar config, opponent pool, and tests are frozen.",
    ]


def render_generation_diagnosis_report(
    *,
    generation: int,
    ledger_path: Path,
    summary_path: Path,
    holdout_path: Path,
) -> str:
    """Render a Markdown diagnosis for one SlimeVolley experiment generation."""

    label = _generation_label(generation)
    title_label = f"Generation-{generation}"
    entries = _read_entries_if_present(ledger_path)
    split_counts = Counter(str(entry.get("seed_range", {}).get("split", "")) for entry in entries)
    pass_fail_counts = Counter(str(entry.get("pass_fail", "")) for entry in entries)
    has_holdout_rows = any(entry.get("seed_range", {}).get("split") == "holdout" for entry in entries)
    lines: list[str] = [
        f"# SlimeVolley {title_label} Diagnosis",
        "",
        f"This report is generated from persisted {label} artifacts only. It does not run evaluation and must not be used as holdout feedback.",
        "",
        "## Status",
        "",
        _status_line(entries, generation=generation),
        "",
        f"- Split counts: `{dict(sorted(split_counts.items()))}`",
        f"- Pass/fail counts: `{dict(sorted(pass_fail_counts.items()))}`",
        "",
        "## Evidence Sources",
        "",
        *_evidence_source_lines(
            ledger_path=ledger_path,
            summary_path=summary_path,
            holdout_path=holdout_path,
            generation=generation,
        ),
        "",
        "## Trial Rows",
        "",
        *_trial_row_lines(entries, generation=generation),
        "",
        "## Failure Analysis",
        "",
        *_failure_analysis_lines(entries, generation=generation),
        "",
        "## Dependency Status",
        "",
        *_dependency_status_lines(entries, generation=generation),
        "",
        "## Cost So Far",
        "",
        *_cost_lines(entries),
        "",
        "## Holdout Lock",
        "",
        *(
            [
                f"{title_label} holdout evidence is now present in `{holdout_path.name}` and the {label} ledger. It is final-only evidence; no {label} holdout evidence may be used for further tuning of the current policy, scalar config, or opponent pool.",
                "Further policy work requires a fresh predeclared experiment generation with new seeds.",
            ]
            if has_holdout_rows
            else [
                f"No {label} holdout evidence is used here. The file `{holdout_path.name}` is final-only; do not inspect {label} holdout before the development policy, scalar config, opponent pool, and tests are frozen."
            ]
        ),
        "",
        "## Next Action",
        "",
        *_next_action_lines(entries, generation=generation),
        "",
    ]
    return "\n".join(lines)


def render_generation_2_diagnosis_report(
    *,
    ledger_path: Path = DEFAULT_GENERATION_LEDGER_PATH,
    summary_path: Path = DEFAULT_GENERATION_SUMMARY_PATH,
    holdout_path: Path = DEFAULT_GENERATION_HOLDOUT_PATH,
) -> str:
    """Render a Markdown diagnosis for the current generation-2 evidence state."""

    return render_generation_diagnosis_report(
        generation=2,
        ledger_path=ledger_path,
        summary_path=summary_path,
        holdout_path=holdout_path,
    )


def render_generation_3_diagnosis_report(
    *,
    ledger_path: Path = DEFAULT_GENERATION_3_LEDGER_PATH,
    summary_path: Path = DEFAULT_GENERATION_3_SUMMARY_PATH,
    holdout_path: Path = DEFAULT_GENERATION_3_HOLDOUT_PATH,
) -> str:
    """Render a Markdown diagnosis for the current generation-3 evidence state."""

    return render_generation_diagnosis_report(
        generation=3,
        ledger_path=ledger_path,
        summary_path=summary_path,
        holdout_path=holdout_path,
    )


def write_generation_2_diagnosis_report(
    *,
    output_path: Path = DEFAULT_GENERATION_REPORT_PATH,
    ledger_path: Path = DEFAULT_GENERATION_LEDGER_PATH,
    summary_path: Path = DEFAULT_GENERATION_SUMMARY_PATH,
    holdout_path: Path = DEFAULT_GENERATION_HOLDOUT_PATH,
) -> Path:
    """Write the generation-2 diagnosis Markdown report."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_generation_2_diagnosis_report(
            ledger_path=ledger_path,
            summary_path=summary_path,
            holdout_path=holdout_path,
        ),
        encoding="utf-8",
    )
    return output_path


def write_generation_3_diagnosis_report(
    *,
    output_path: Path = DEFAULT_GENERATION_3_REPORT_PATH,
    ledger_path: Path = DEFAULT_GENERATION_3_LEDGER_PATH,
    summary_path: Path = DEFAULT_GENERATION_3_SUMMARY_PATH,
    holdout_path: Path = DEFAULT_GENERATION_3_HOLDOUT_PATH,
) -> Path:
    """Write the generation-3 diagnosis Markdown report."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_generation_3_diagnosis_report(
            ledger_path=ledger_path,
            summary_path=summary_path,
            holdout_path=holdout_path,
        ),
        encoding="utf-8",
    )
    return output_path


def _default_paths_for_generation(generation: int) -> tuple[Path, Path, Path, Path]:
    if generation == 3:
        return (
            DEFAULT_GENERATION_3_LEDGER_PATH,
            DEFAULT_GENERATION_3_SUMMARY_PATH,
            DEFAULT_GENERATION_3_HOLDOUT_PATH,
            DEFAULT_GENERATION_3_REPORT_PATH,
        )
    return (
        DEFAULT_GENERATION_LEDGER_PATH,
        DEFAULT_GENERATION_SUMMARY_PATH,
        DEFAULT_GENERATION_HOLDOUT_PATH,
        DEFAULT_GENERATION_REPORT_PATH,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", type=int, choices=(2, 3), default=2)
    parser.add_argument("--ledger", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--holdout", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    default_ledger, default_summary, default_holdout, default_output = _default_paths_for_generation(args.generation)
    ledger_path = args.ledger or default_ledger
    summary_path = args.summary or default_summary
    holdout_path = args.holdout or default_holdout
    output_path = args.output or default_output
    if args.generation == 3:
        path = write_generation_3_diagnosis_report(
            output_path=output_path,
            ledger_path=ledger_path,
            summary_path=summary_path,
            holdout_path=holdout_path,
        )
    else:
        path = write_generation_2_diagnosis_report(
            output_path=output_path,
            ledger_path=ledger_path,
            summary_path=summary_path,
            holdout_path=holdout_path,
        )
    print(path)


if __name__ == "__main__":
    main()
