"""Generate an agent-process deep-dive report from benchmark artifacts."""

from __future__ import annotations

import argparse
import csv
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from .envs import ENV_SPECS
from .ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH, read_entries, write_summary_csv


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DEEPDIVE_REPORT_PATH = RESULTS_DIR / "agent_deepdive_report.md"

TRANSPARENT_POLICIES = {"initial", "improved", "tuned", "tree"}
RL_POLICIES = {"rl-ppo", "rl-dqn", "rl-sac", "rl-sac-hf"}


def _read_summary(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float_or_none(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _format_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6g}"


def _threshold_cutoff(success_target: float) -> float:
    if success_target >= 0.0:
        return 0.95 * success_target
    return success_target - 0.05 * abs(success_target)


def _best_row(
    rows: list[dict[str, str]],
    *,
    env_id: str,
    policies: set[str],
    split: str = "holdout",
) -> dict[str, str] | None:
    candidates = [
        row
        for row in rows
        if row["environment"] == env_id
        and row["policy_version"] in policies
        and row["split"] == split
        and row["pass_fail"] == "pass"
        and row["mean"] != ""
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: float(row["mean"]))


def _entry_split(entry: dict[str, Any]) -> str:
    return str(entry.get("seed_range", {}).get("split", "unknown"))


def _entry_mean(entry: dict[str, Any]) -> float | None:
    mean = entry.get("score_stats", {}).get("mean")
    return None if mean is None else float(mean)


def _names(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _counter_lines(counter: Counter[str]) -> list[str]:
    if not counter:
        return ["- none"]
    return [f"- {key}: {counter[key]}" for key in sorted(counter)]


def _git_status_for_project() -> str:
    try:
        output = subprocess.check_output(
            ["git", "status", "--short", "--", str(PROJECT_DIR)],
            cwd=PROJECT_DIR,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unavailable"
    return output.replace("\n", "; ") or "clean"


def _benchmark_rows(rows: list[dict[str, str]]) -> tuple[list[str], dict[str, Any]]:
    lines = [
        "| Environment | Best transparent holdout policy | Mean | Strict target | Strict pass? | 5% cutoff | 5% pass? |",
        "| --- | --- | ---: | ---: | --- | ---: | --- |",
    ]
    strict_pass: list[str] = []
    strict_fail: list[str] = []
    tolerance_pass: list[str] = []
    tolerance_fail: list[str] = []
    missing: list[str] = []
    for env_id, spec in ENV_SPECS.items():
        row = _best_row(rows, env_id=env_id, policies=TRANSPARENT_POLICIES)
        mean = _float_or_none(row["mean"]) if row else None
        cutoff = _threshold_cutoff(spec.success_target)
        if row is None or mean is None:
            missing.append(env_id)
            lines.append(
                f"| {env_id} | missing |  | {spec.success_target:.6g} | "
                f"no evidence | {cutoff:.6g} | no evidence |"
            )
            continue
        meets_strict = mean >= spec.success_target
        meets_tolerance = mean >= cutoff
        if meets_strict:
            strict_pass.append(env_id)
        else:
            strict_fail.append(env_id)
        if meets_tolerance:
            tolerance_pass.append(env_id)
        else:
            tolerance_fail.append(env_id)
        lines.append(
            f"| {env_id} | {row['policy_version']} | {mean:.6g} | {spec.success_target:.6g} | "
            f"{'yes' if meets_strict else 'no'} | {cutoff:.6g} | {'yes' if meets_tolerance else 'no'} |"
        )
    summary = {
        "strict_pass": strict_pass,
        "strict_fail": strict_fail,
        "tolerance_pass": tolerance_pass,
        "tolerance_fail": tolerance_fail,
        "missing": missing,
    }
    return lines, summary


def _policy_family_rows(rows: list[dict[str, str]]) -> list[str]:
    families = [
        ("initial", {"initial"}),
        ("structural improved", {"improved"}),
        ("scalar tuned", {"tuned"}),
        ("teacher-distilled tree", {"tree"}),
        ("best recorded RL", RL_POLICIES),
    ]
    lines = [
        "| Environment | Initial | Structural improved | Scalar tuned | Teacher-distilled tree | Best recorded RL |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for env_id in ENV_SPECS:
        cells: list[str] = []
        for _label, policies in families:
            row = _best_row(rows, env_id=env_id, policies=policies)
            mean = _float_or_none(row["mean"]) if row else None
            cells.append("" if row is None or mean is None else f"{row['policy_version']} {_format_float(mean)}")
        lines.append(f"| {env_id} | " + " | ".join(cells) + " |")
    return lines


def _deep_rl_rows(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Environment | Best transparent | Transparent mean | Best recorded RL | RL mean | Strict gap | Comparator status |",
        "| --- | --- | ---: | --- | ---: | ---: | --- |",
    ]
    for env_id in ENV_SPECS:
        transparent = _best_row(rows, env_id=env_id, policies=TRANSPARENT_POLICIES)
        rl = _best_row(rows, env_id=env_id, policies=RL_POLICIES)
        transparent_mean = _float_or_none(transparent["mean"]) if transparent else None
        rl_mean = _float_or_none(rl["mean"]) if rl else None
        if transparent is None or rl is None or transparent_mean is None or rl_mean is None:
            lines.append(f"| {env_id} | missing |  | missing |  |  | no RL evidence |")
            continue
        denominator = max(abs(rl_mean), 1.0)
        gap = abs(transparent_mean - rl_mean) / denominator
        status = "within 5%" if gap <= 0.05 else "outside 5%"
        lines.append(
            f"| {env_id} | {transparent['policy_version']} | {transparent_mean:.6g} | "
            f"{rl['policy_version']} | {rl_mean:.6g} | {gap:.2%} | {status} |"
        )
    return lines


def _environment_process_rows(entries: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Environment | Trials | Dev | Holdout | Audit | Structural | Scalar | RL | Partial/non-pass | First trial | Last trial |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for env_id in ENV_SPECS:
        env_entries = [entry for entry in entries if entry["environment"] == env_id]
        split_counts = Counter(_entry_split(entry) for entry in env_entries)
        change_counts = Counter(entry["change_type"] for entry in env_entries)
        non_pass = sum(1 for entry in env_entries if entry["pass_fail"] != "pass")
        first = min((entry["timestamp"] for entry in env_entries), default="")
        last = max((entry["timestamp"] for entry in env_entries), default="")
        structural = change_counts["structural policy improvement"]
        scalar = change_counts["scalar/config tuning"]
        rl = change_counts["rl/deep learning baseline"]
        lines.append(
            f"| {env_id} | {len(env_entries)} | {split_counts['dev']} | {split_counts['holdout']} | "
            f"{split_counts['audit']} | {structural} | {scalar} | {rl} | {non_pass} | {first} | {last} |"
        )
    return lines


def _environment_deep_dive_lines(
    entries: list[dict[str, Any]],
    rows: list[dict[str, str]],
) -> list[str]:
    lines: list[str] = []
    for env_id, spec in ENV_SPECS.items():
        initial = _best_row(rows, env_id=env_id, policies={"initial"})
        improved = _best_row(rows, env_id=env_id, policies={"improved"})
        tuned = _best_row(rows, env_id=env_id, policies={"tuned"})
        tree = _best_row(rows, env_id=env_id, policies={"tree"})
        best = _best_row(rows, env_id=env_id, policies=TRANSPARENT_POLICIES)
        best_mean = _float_or_none(best["mean"]) if best else None
        cutoff = _threshold_cutoff(spec.success_target)

        lines.extend([f"### {env_id}", ""])
        if best is not None and best_mean is not None:
            lines.append(
                f"- Best transparent holdout result: `{best['policy_version']}` mean `{best_mean:.6g}` "
                f"against strict target `{spec.success_target:.6g}` and 5% cutoff `{cutoff:.6g}`."
            )
        else:
            lines.append("- Best transparent holdout result: no evidence.")

        initial_mean = _float_or_none(initial["mean"]) if initial else None
        improved_mean = _float_or_none(improved["mean"]) if improved else None
        if initial_mean is not None and improved_mean is not None:
            delta = improved_mean - initial_mean
            if delta > 0:
                lines.append(f"- Structural improved policy beat initial by `{delta:.6g}` mean reward.")
            elif delta < 0:
                lines.append(
                    f"- Structural improved policy regressed versus initial by `{abs(delta):.6g}` mean reward."
                )
            else:
                lines.append("- Structural improved policy tied the initial policy.")

        if tuned is not None and best is not None and best["policy_version"] == "tuned":
            lines.append("- Best result came from scalar/config tuning, not a structural policy edit.")
        if tree is not None and best is not None and best["policy_version"] == "tree":
            lines.append("- Best result came from an explicit decision tree distilled from a PPO teacher.")
        if best_mean is not None and best_mean < spec.success_target:
            lines.append("- Strict benchmark target is not met; only tolerance or comparator claims are justified.")

        env_partials = [
            entry
            for entry in entries
            if entry["environment"] == env_id and entry["pass_fail"] != "pass"
        ]
        if env_partials:
            lines.append("- Notable non-pass iterations:")
            for entry in env_partials[:4]:
                mean = _entry_mean(entry)
                lines.append(
                    f"  - `{entry['timestamp']}` `{entry['policy_version']}` `{entry['pass_fail']}` "
                    f"mean `{_format_float(mean)}`: {entry['failure_analysis']}"
                )
        lines.append("")
    return lines


def _partial_trial_rows(entries: list[dict[str, Any]]) -> list[str]:
    non_pass = [entry for entry in entries if entry["pass_fail"] != "pass"]
    if not non_pass:
        return ["No non-pass trials recorded."]
    lines = [
        "| Timestamp | Environment | Policy | Status | Mean | Steps | Failure analysis |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for entry in non_pass:
        mean = _entry_mean(entry)
        analysis = str(entry["failure_analysis"]).replace("|", "\\|")
        lines.append(
            f"| {entry['timestamp']} | {entry['environment']} | {entry['policy_version']} | "
            f"{entry['pass_fail']} | {_format_float(mean)} | {entry['environment_steps']} | {analysis} |"
        )
    return lines


def _cost_lines(entries: list[dict[str, Any]]) -> list[str]:
    status_counts = Counter(entry["pass_fail"] for entry in entries)
    split_counts = Counter(_entry_split(entry) for entry in entries)
    change_counts = Counter(entry["change_type"] for entry in entries)
    tests_recorded = sum(1 for entry in entries if entry.get("tests_run"))
    llm_unavailable = sum(
        1
        for entry in entries
        if entry.get("llm_cost", {}).get("total_tokens") == "unavailable"
    )
    zero_step_runs = [
        entry
        for entry in entries
        if int(entry.get("episodes", 0)) > 0 and int(entry.get("environment_steps", 0)) == 0
    ]
    status_text = ", ".join(f"{key}: {status_counts[key]}" for key in sorted(status_counts)) or "none"
    split_text = ", ".join(f"{key}: {split_counts[key]}" for key in sorted(split_counts)) or "none"
    change_text = ", ".join(f"{key}: {change_counts[key]}" for key in sorted(change_counts)) or "none"
    commit_text = ", ".join(
        f"{key}: {value}" for key, value in Counter(entry["git_commit"] for entry in entries).items()
    ) or "none"
    diff_text = ", ".join(
        f"{key}: {value}" for key, value in Counter(entry["diff_identifier"] for entry in entries).items()
    ) or "none"
    return [
        f"- Trials: {len(entries)}",
        f"- Status counts: {status_text}",
        f"- Split counts: {split_text}",
        f"- Change-type counts: {change_text}",
        f"- Episodes: {sum(int(entry['episodes']) for entry in entries)}",
        f"- Recorded environment steps: {sum(int(entry['environment_steps']) for entry in entries)}",
        f"- Wall-clock seconds: {sum(float(entry['wall_clock_seconds']) for entry in entries):.3f}",
        f"- Max agent iterations recorded: {max([int(entry['agent_iterations']) for entry in entries] or [0])}",
        f"- Max code edits recorded: {max([int(entry['code_edits']) for entry in entries] or [0])}",
        f"- Rows with tests recorded: {tests_recorded}/{len(entries)}",
        f"- Rows with unavailable LLM token totals: {llm_unavailable}/{len(entries)}",
        f"- Runs with episodes but zero recorded environment steps: {len(zero_step_runs)}",
        f"- Ledger git commits: {commit_text}",
        f"- Ledger diff identifiers: {diff_text}",
        f"- Current git status for benchmark path: `{_git_status_for_project()}`",
    ]


def render_deepdive_report(
    *,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    summary_path: Path = DEFAULT_SUMMARY_PATH,
    output_path: Path = DEFAULT_DEEPDIVE_REPORT_PATH,
) -> str:
    """Render and write the agent deep-dive Markdown report."""

    if ledger_path.exists():
        write_summary_csv(ledger_path, summary_path)
    entries = read_entries(ledger_path)
    rows = _read_summary(summary_path)
    benchmark_lines, benchmark_summary = _benchmark_rows(rows)
    strict_pass = benchmark_summary["strict_pass"]
    strict_fail = benchmark_summary["strict_fail"]
    tolerance_pass = benchmark_summary["tolerance_pass"]
    tolerance_fail = benchmark_summary["tolerance_fail"]
    missing = benchmark_summary["missing"]

    lines: list[str] = [
        "# Agent Deep-Dive Report",
        "",
        "## Executive Verdict",
        "",
        "This generated report explains how the coding-agent experiment progressed, what evidence it produced, and where the evidence remains weak.",
        "",
        f"- Strict benchmark targets met: {len(strict_pass)}/{len(ENV_SPECS)} ({_names(strict_pass)})",
        f"- Strict benchmark targets missed: {len(strict_fail)}/{len(ENV_SPECS)} ({_names(strict_fail)})",
        f"- 5% tolerance targets met: {len(tolerance_pass)}/{len(ENV_SPECS)} ({_names(tolerance_pass)})",
        f"- 5% tolerance targets missed: {len(tolerance_fail)}/{len(ENV_SPECS)} ({_names(tolerance_fail)})",
        f"- Missing holdout evidence: {len(missing)}/{len(ENV_SPECS)} ({_names(missing)})",
        "- Deep-RL comparisons are secondary comparators; benchmark solved-score targets are the primary cutoff.",
        "",
        "## Benchmark Outcome",
        "",
    ]
    lines.extend(benchmark_lines)
    lines.extend(
        [
            "",
            "## How The Agent Worked",
            "",
            "Each meaningful trial is represented as a ledger row with a change type, diagnosis, next hypothesis, cost fields, and fixed seed range. The practical loop was: evaluate, inspect reward summaries and failures, edit policy/config/tests, run checks, re-evaluate, and preserve unsuccessful attempts as non-pass or diagnostic rows.",
            "",
            "### Process By Environment",
            "",
        ]
    )
    lines.extend(_environment_process_rows(entries))
    lines.extend(["", "### Change-Type Counts", ""])
    lines.extend(_counter_lines(Counter(entry["change_type"] for entry in entries)))
    lines.extend(
        [
            "",
            "## Structural, Scalar, Teacher-Distilled, And RL Evidence",
            "",
            "This table separates result families so scalar tuning and teacher distillation are not misreported as purely hand-written structural policy improvement.",
            "",
        ]
    )
    lines.extend(_policy_family_rows(rows))
    lines.extend(
        [
            "",
            "## Deep-RL Secondary Comparator",
            "",
            "This section is intentionally secondary. It answers whether the best transparent result looked similar to the best recorded RL comparator, not whether the benchmark was solved.",
            "",
        ]
    )
    lines.extend(_deep_rl_rows(rows))
    lines.extend(["", "## Environment Deep Dives", ""])
    lines.extend(_environment_deep_dive_lines(entries, rows))
    lines.extend(["## Non-Pass And Partial Iterations", ""])
    lines.extend(_partial_trial_rows(entries))
    lines.extend(["", "## Cost And Audit Accounting", ""])
    lines.extend(_cost_lines(entries))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The strongest support is auditability: the ledger preserves successes, regressions, partial trials, and costs.",
            "- Structural improvement is mixed: MountainCar and BipedalWalker improved clearly, CartPole was already solved, and LunarLander regressed structurally.",
            "- The best Acrobot result is transparent at inference time but teacher-distilled, so it should be reported separately from hand-written heuristic learning.",
            "- BipedalWalker is the strict benchmark miss: it is within 5% of the target but below the official solved-score threshold.",
            "- Holdout reuse and limited audit coverage weaken claims of final generalization; fresh audit evaluations should be the next evidence step.",
            "",
        ]
    )

    report = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")
    return report + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_DEEPDIVE_REPORT_PATH)
    args = parser.parse_args()
    render_deepdive_report(
        ledger_path=args.ledger,
        summary_path=args.summary,
        output_path=args.output,
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
