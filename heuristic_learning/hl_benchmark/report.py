"""Generate the final Markdown report from the ledger."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from .envs import ENV_SPECS, SEED_SPLITS, discover_runtime_metadata
from .ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH, read_entries, write_summary_csv


DEFAULT_REPORT_PATH = Path(__file__).resolve().parents[1] / "results" / "final_report.md"


def _read_summary(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _result_rows(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Environment | Policy | Change type | Split | Episodes | Mean | Std | Min | Max | Steps | Status |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {environment} | {policy_version} | {change_type} | {split} | {episodes} | "
            "{mean} | {std} | {min} | {max} | {environment_steps} | {pass_fail} |".format(**row)
        )
    return lines


def _float_or_none(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def _representative_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    representative: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["environment"], row["policy_version"], row["split"])
        current = representative.get(key)
        if current is None:
            representative[key] = row
            continue
        row_mean = _float_or_none(row["mean"])
        current_mean = _float_or_none(current["mean"])
        if row["policy_version"].startswith("rl-"):
            if row_mean is not None and (current_mean is None or row_mean > current_mean):
                representative[key] = row
        elif row["policy_version"] == "tuned" and row["split"] == "dev":
            row_episodes = int(row["episodes"] or 0)
            current_episodes = int(current["episodes"] or 0)
            if row_episodes > current_episodes or (
                row_episodes == current_episodes
                and row_mean is not None
                and (current_mean is None or row_mean > current_mean)
            ):
                representative[key] = row
        else:
            representative[key] = row
    return sorted(
        representative.values(),
        key=lambda item: (item["environment"], item["split"], item["policy_version"]),
    )


def _names(values: list[str]) -> str:
    return ", ".join(values) or "none"


def _holdout_conclusion(rows: list[dict[str, str]]) -> str:
    by_env_policy = {
        (row["environment"], row["policy_version"]): _float_or_none(row["mean"])
        for row in rows
        if row["split"] == "holdout" and row["pass_fail"] == "pass"
    }
    improved_better: list[str] = []
    improved_tied: list[str] = []
    improved_worse: list[str] = []
    tuned_better_than_improved: list[str] = []
    for env_id in ENV_SPECS:
        initial = by_env_policy.get((env_id, "initial"))
        improved = by_env_policy.get((env_id, "improved"))
        tuned = by_env_policy.get((env_id, "tuned"))
        if initial is not None and improved is not None:
            if improved > initial:
                improved_better.append(env_id)
            elif improved == initial:
                improved_tied.append(env_id)
            else:
                improved_worse.append(env_id)
        if tuned is not None and improved is not None and tuned > improved:
            tuned_better_than_improved.append(env_id)
    if not by_env_policy:
        return "No holdout conclusion is justified until frozen holdout evaluations are recorded."
    return (
        f"On holdout, structural improved policies beat the initial heuristic on "
        f"{len(improved_better)}/{len(ENV_SPECS)} environments "
        f"({_names(improved_better)}), tied on {len(improved_tied)} "
        f"({_names(improved_tied)}), and regressed on {len(improved_worse)} "
        f"({_names(improved_worse)}). The dev-selected scalar baseline beat "
        f"the structural policy on {len(tuned_better_than_improved)}/{len(ENV_SPECS)} "
        f"environments ({_names(tuned_better_than_improved)}). This supports "
        "the auditability and preservation parts of the hypothesis, but only partially "
        "supports broad agent-maintained structural improvement: CartPole was already "
        "solved, MountainCar and BipedalWalker improved structurally, and the strongest "
        "Acrobot/LunarLander gains came from scalar tuning. The benchmark-threshold "
        "view is the primary solved-score cutoff; recorded neural/RL runs are secondary "
        "comparators because several local RL baselines remain undertrained."
    )


def _deep_rl_goal_summary(rows: list[dict[str, str]]) -> str:
    rl_versions = {"rl-ppo", "rl-dqn", "rl-sac", "rl-sac-hf"}
    heuristic_versions = {"initial", "improved", "tuned", "tree"}
    strict_within: list[str] = []
    not_strict: list[str] = []
    not_worse_than_rl: list[str] = []
    worse_than_rl: list[str] = []
    missing: list[str] = []
    rl_success: list[str] = []
    for env_id, spec in ENV_SPECS.items():
        rl_row = _best_row(rows, env_id=env_id, policy_versions=rl_versions, split="holdout")
        heuristic_row = _best_row(rows, env_id=env_id, policy_versions=heuristic_versions, split="holdout")
        rl_mean = _row_mean(rl_row)
        heuristic_mean = _row_mean(heuristic_row)
        if rl_mean is None or heuristic_mean is None:
            missing.append(env_id)
            continue
        if rl_mean >= spec.success_target:
            rl_success.append(env_id)
        denominator = max(abs(rl_mean), 1.0)
        relative_gap = abs(heuristic_mean - rl_mean) / denominator
        if relative_gap <= 0.05:
            strict_within.append(env_id)
        else:
            not_strict.append(env_id)
        if heuristic_mean >= rl_mean - 0.05 * denominator:
            not_worse_than_rl.append(env_id)
        else:
            worse_than_rl.append(env_id)
    return (
        f"Against recorded deep-RL baselines, strict ±5% parity is met on "
        f"{len(strict_within)}/{len(ENV_SPECS)} environments ({_names(strict_within)}) and not met on "
        f"{len(not_strict)} ({_names(not_strict)}). The weaker performance target of being "
        f"no more than 5% worse than recorded RL is met on {len(not_worse_than_rl)}/{len(ENV_SPECS)} "
        f"({_names(not_worse_than_rl)}) and missed on {len(worse_than_rl)} ({_names(worse_than_rl)}); "
        f"missing RL evidence remains for {len(missing)} ({_names(missing)}). The best recorded "
        f"RL comparator meets its environment success target on {len(rl_success)}/{len(ENV_SPECS)} "
        f"environments ({_names(rl_success)}). These recorded neural runs are useful reproducible "
        "comparators, while the published benchmark thresholds remain the primary solved-score cutoff."
    )


def _holdout_partial_lines(rows: list[dict[str, str]]) -> list[str]:
    by_env_policy = {
        (row["environment"], row["policy_version"]): _float_or_none(row["mean"])
        for row in rows
        if row["split"] == "holdout" and row["pass_fail"] == "pass"
    }
    lines: list[str] = []
    for env_id in ENV_SPECS:
        initial = by_env_policy.get((env_id, "initial"))
        improved = by_env_policy.get((env_id, "improved"))
        tuned = by_env_policy.get((env_id, "tuned"))
        if initial is not None and improved is not None and improved < initial:
            lines.append(
                f"- {env_id}: structural policy regressed on holdout versus initial "
                f"({improved:.3f} vs {initial:.3f})."
            )
        if tuned is not None and improved is not None and tuned > improved:
            lines.append(
                f"- {env_id}: scalar tuning beat structural improvement on holdout "
                f"({tuned:.3f} vs {improved:.3f})."
            )
    return lines


def _runtime_metadata_lines(entries: list[dict[str, Any]]) -> list[str]:
    if not entries:
        return ["No runtime metadata recorded yet."]
    latest = entries[-1]
    recorded_metadata = latest.get("runtime_metadata", {})
    current_metadata = discover_runtime_metadata()
    packages = {
        **recorded_metadata.get("packages", {}),
        **current_metadata.get("packages", {}),
    }
    lines = [
        f"- Git commit: `{latest.get('git_commit', 'unavailable')}`",
        f"- Latest ledger diff identifier: `{latest.get('diff_identifier', 'unavailable')}`",
        f"- Python: `{current_metadata.get('python', recorded_metadata.get('python', 'unavailable'))}`",
        f"- Platform: `{current_metadata.get('platform', recorded_metadata.get('platform', 'unavailable'))}`",
    ]
    for package_name in sorted(packages):
        lines.append(f"- {package_name}: `{packages[package_name]}`")
    return lines


def _row_mean(row: dict[str, str] | None) -> float | None:
    if row is None:
        return None
    return _float_or_none(row["mean"])


def _best_row(
    rows: list[dict[str, str]],
    *,
    env_id: str,
    policy_versions: set[str],
    split: str,
) -> dict[str, str] | None:
    candidates = [
        row
        for row in rows
        if row["environment"] == env_id
        and row["policy_version"] in policy_versions
        and row["split"] == split
        and row["pass_fail"] == "pass"
        and row["mean"] != ""
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: float(row["mean"]))


def _deep_rl_comparison_lines(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Environment | Split | Best heuristic/search policy | Heuristic mean | Deep-RL policy | Deep-RL mean | Strict gap | Within ±5%? | At least 95% of RL? |",
        "| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |",
    ]
    heuristic_versions = {"initial", "improved", "tuned", "tree"}
    for env_id in ENV_SPECS:
        split = "holdout"
        rl_row = _best_row(rows, env_id=env_id, policy_versions={"rl-ppo", "rl-dqn", "rl-sac", "rl-sac-hf"}, split=split)
        if rl_row is None:
            split = "dev"
            rl_row = _best_row(rows, env_id=env_id, policy_versions={"rl-ppo", "rl-dqn", "rl-sac", "rl-sac-hf"}, split=split)
        heuristic_row = _best_row(rows, env_id=env_id, policy_versions=heuristic_versions, split=split)
        if rl_row is None or heuristic_row is None:
            lines.append(f"| {env_id} | n/a | n/a |  | missing |  |  | no RL evidence | no RL evidence |")
            continue
        rl_mean = _row_mean(rl_row)
        heuristic_mean = _row_mean(heuristic_row)
        if rl_mean is None or heuristic_mean is None:
            lines.append(f"| {env_id} | {split} | {heuristic_row['policy_version']} |  | {rl_row['policy_version']} |  |  | incomplete | incomplete |")
            continue
        denominator = max(abs(rl_mean), 1.0)
        relative_gap = abs(heuristic_mean - rl_mean) / denominator
        strict_within = relative_gap <= 0.05
        not_worse = heuristic_mean >= rl_mean - 0.05 * denominator
        lines.append(
            f"| {env_id} | {split} | {heuristic_row['policy_version']} | {heuristic_mean:.6g} | "
            f"{rl_row['policy_version']} | {rl_mean:.6g} | {relative_gap:.2%} | "
            f"{'yes' if strict_within else 'no'} | {'yes' if not_worse else 'no'} |"
        )
    return lines


def _threshold_cutoff(success_target: float) -> float:
    if success_target >= 0.0:
        return 0.95 * success_target
    return success_target - 0.05 * abs(success_target)


def _benchmark_threshold_lines(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Environment | Best transparent policy | Holdout mean | Success target | 5% tolerance cutoff | Meets target? | Within 5% cutoff? |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    heuristic_versions = {"initial", "improved", "tuned", "tree"}
    for env_id, spec in ENV_SPECS.items():
        row = _best_row(rows, env_id=env_id, policy_versions=heuristic_versions, split="holdout")
        mean = _row_mean(row)
        cutoff = _threshold_cutoff(spec.success_target)
        if row is None or mean is None:
            lines.append(f"| {env_id} | missing |  | {spec.success_target:.6g} | {cutoff:.6g} | no evidence | no evidence |")
            continue
        meets_target = mean >= spec.success_target
        within_cutoff = mean >= cutoff
        lines.append(
            f"| {env_id} | {row['policy_version']} | {mean:.6g} | {spec.success_target:.6g} | "
            f"{cutoff:.6g} | {'yes' if meets_target else 'no'} | {'yes' if within_cutoff else 'no'} |"
        )
    return lines


def _benchmark_threshold_summary(rows: list[dict[str, str]]) -> str:
    heuristic_versions = {"initial", "improved", "tuned", "tree"}
    meets: list[str] = []
    within: list[str] = []
    misses: list[str] = []
    missing: list[str] = []
    for env_id, spec in ENV_SPECS.items():
        row = _best_row(rows, env_id=env_id, policy_versions=heuristic_versions, split="holdout")
        mean = _row_mean(row)
        if mean is None:
            missing.append(env_id)
            continue
        if mean >= spec.success_target:
            meets.append(env_id)
            within.append(env_id)
        elif mean >= _threshold_cutoff(spec.success_target):
            within.append(env_id)
            misses.append(env_id)
        else:
            misses.append(env_id)
    return (
        f"Against benchmark solved-score cutoffs, the best transparent policies meet the target on "
        f"{len(meets)}/{len(ENV_SPECS)} environments ({_names(meets)}). With a 5% below-target "
        f"tolerance, they are within cutoff on {len(within)}/{len(ENV_SPECS)} ({_names(within)}) "
        f"and outside cutoff on {len(set(misses) - set(within))} ({_names([env for env in misses if env not in within])}); "
        f"missing evidence remains for {len(missing)} ({_names(missing)})."
    )


def _audit_threshold_lines(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Environment | Best transparent policy | Audit mean | Success target | 5% tolerance cutoff | Meets target? | Within 5% cutoff? |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    heuristic_versions = {"initial", "improved", "tuned", "tree"}
    for env_id, spec in ENV_SPECS.items():
        row = _best_row(rows, env_id=env_id, policy_versions=heuristic_versions, split="audit")
        mean = _row_mean(row)
        cutoff = _threshold_cutoff(spec.success_target)
        if row is None or mean is None:
            lines.append(f"| {env_id} | missing |  | {spec.success_target:.6g} | {cutoff:.6g} | no evidence | no evidence |")
            continue
        meets_target = mean >= spec.success_target
        within_cutoff = mean >= cutoff
        lines.append(
            f"| {env_id} | {row['policy_version']} | {mean:.6g} | {spec.success_target:.6g} | "
            f"{cutoff:.6g} | {'yes' if meets_target else 'no'} | {'yes' if within_cutoff else 'no'} |"
        )
    return lines


def _audit_threshold_summary(rows: list[dict[str, str]]) -> str | None:
    heuristic_versions = {"initial", "improved", "tuned", "tree"}
    evaluated: list[str] = []
    within: list[str] = []
    misses: list[str] = []
    for env_id, spec in ENV_SPECS.items():
        row = _best_row(rows, env_id=env_id, policy_versions=heuristic_versions, split="audit")
        mean = _row_mean(row)
        if mean is None:
            continue
        evaluated.append(env_id)
        if mean >= _threshold_cutoff(spec.success_target):
            within.append(env_id)
        else:
            misses.append(env_id)
    if not evaluated:
        return None
    return (
        f"On the fresh audit split, transparent policies are within the 5% solved-score cutoff on "
        f"{len(within)}/{len(evaluated)} evaluated environments ({_names(within)}) and outside it on "
        f"{len(misses)} ({_names(misses)}). Audit seeds are separate from development and holdout seeds."
    )


def _rl_baseline_status(entries: list[dict[str, Any]]) -> str:
    rl_entries = [entry for entry in entries if entry["policy_version"].startswith("rl")]
    if rl_entries:
        envs = sorted({entry["environment"] for entry in rl_entries})
        missing = sorted(set(ENV_SPECS) - set(envs))
        suffix = (
            f" Missing environments remain unproven: {', '.join(missing)}."
            if missing
            else " All registered environments have at least one recorded RL entry."
        )
        return (
            f"A neural/RL baseline is present for {len(envs)} environment(s): "
            f"{', '.join(envs)}. The ±5% comparison below is based only on recorded RL entries."
            f"{suffix}"
        )
    stable_baselines = "not_installed"
    if entries:
        stable_baselines = (
            entries[-1]
            .get("runtime_metadata", {})
            .get("packages", {})
            .get("stable-baselines3", "not_installed")
        )
    return (
        "No neural/RL baseline was run. This lean-audit experiment kept the compute budget "
        "focused on fixed-seed heuristic and scalar-search comparisons; the off-the-shelf "
        f"Stable-Baselines3 package was `{stable_baselines}` in the recorded runtime metadata. "
        "The omission weakens claims of competitiveness against neural RL and should be "
        "addressed by a separately budgeted optional run."
    )


def _pretrained_comparator_lines(entries: list[dict[str, Any]]) -> list[str]:
    pretrained_entries = [
        entry
        for entry in entries
        if entry["policy_version"].startswith("rl")
        and entry.get("config", {}).get("pretrained_repo_id")
    ]
    if not pretrained_entries:
        return []
    latest_by_key: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for entry in pretrained_entries:
        config = entry.get("config", {})
        split = str(entry.get("split") or entry.get("seed_range", {}).get("split", "unavailable"))
        key = (
            entry["environment"],
            entry["policy_version"],
            split,
            str(config.get("pretrained_repo_id", "")),
            str(config.get("pretrained_filename", "")),
        )
        latest_by_key[key] = entry
    lines: list[str] = []
    for (env_id, policy_version, split, repo_id, filename), entry in sorted(latest_by_key.items()):
        mean = entry.get("score_stats", {}).get("mean", "unavailable")
        url = f"https://huggingface.co/{repo_id}"
        lines.append(
            f"- {env_id} `{policy_version}` `{split}`: `{repo_id}` / `{filename}` "
            f"({url}), evaluated locally with the fixed-seed protocol; mean `{mean}`."
        )
    return lines


def _cost_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "trials": len(entries),
        "failed_trials": sum(1 for entry in entries if entry["pass_fail"] != "pass"),
        "environment_steps": sum(int(entry["environment_steps"]) for entry in entries),
        "wall_clock_seconds": sum(float(entry["wall_clock_seconds"]) for entry in entries),
        "episodes": sum(int(entry["episodes"]) for entry in entries),
        "agent_iterations": max([int(entry["agent_iterations"]) for entry in entries] or [0]),
        "code_edits": max([int(entry["code_edits"]) for entry in entries] or [0]),
    }


def render_report(
    *,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    summary_path: Path = DEFAULT_SUMMARY_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> str:
    """Render and write the final Markdown report."""

    if ledger_path.exists():
        write_summary_csv(ledger_path, summary_path)
    entries = read_entries(ledger_path)
    rows = _read_summary(summary_path)
    latest_rows = _representative_rows(rows)
    cost = _cost_summary(entries)
    failures_by_env: dict[str, list[str]] = defaultdict(list)
    benign_analysis = {"No failure observed.", "Holdout was not used during scalar selection."}
    for entry in entries:
        if entry["pass_fail"] != "pass" or entry["failure_analysis"] not in benign_analysis:
            failures_by_env[entry["environment"]].append(entry["failure_analysis"])

    lines: list[str] = [
        "# Heuristic Learning Benchmark Report",
        "",
        "## Experimental Setup",
        "",
        "This report is generated from the append-only trial ledger. The experiment compares random policies, initial handwritten heuristics, scalar/config search, and structurally improved heuristic policies over fixed seed ranges.",
        "",
        f"- Development seeds: `{SEED_SPLITS['dev'].start}..{SEED_SPLITS['dev'].stop - 1}`",
        f"- Holdout seeds: `{SEED_SPLITS['holdout'].start}..{SEED_SPLITS['holdout'].stop - 1}`",
        f"- Audit seeds: `{SEED_SPLITS['audit'].start}..{SEED_SPLITS['audit'].stop - 1}`",
        "- Holdout and audit seeds are reserved for frozen comparisons and must not be used by `search.py`.",
        "- Later Acrobot diagnostics also use explicit non-holdout development ranges recorded in each ledger row; the seed range in the ledger is authoritative.",
        "",
        "## Environments",
        "",
    ]
    for spec in ENV_SPECS.values():
        lines.extend(
            [
                f"### {spec.env_id}",
                "",
                f"- Category: {spec.category}",
                f"- Observation: {spec.observation_summary}",
                f"- Action: {spec.action_summary}",
                f"- Reward: {spec.reward_interpretation}",
                f"- Episode length: {spec.episode_length}",
                f"- Success target: {spec.success_target}",
                f"- Initial policy: {spec.initial_policy}",
                f"- Known failure modes: {'; '.join(spec.known_failure_modes)}",
                f"- Reference: {spec.docs_url}",
                "",
            ]
        )

    lines.extend(
        [
            "## Runtime Metadata",
            "",
        ]
    )
    lines.extend(_runtime_metadata_lines(entries))
    lines.extend(
        [
            "",
            "## Neural/RL Baseline Status",
            "",
            _rl_baseline_status(entries),
            "",
        ]
    )
    pretrained_lines = _pretrained_comparator_lines(entries)
    if pretrained_lines:
        lines.extend(
            [
                "### Pretrained Comparator Sources",
                "",
            ]
        )
        lines.extend(pretrained_lines)
        lines.append("")

    lines.extend(
        [
            "## Quantitative Results",
            "",
        ]
    )
    if latest_rows:
        lines.extend(_result_rows(latest_rows))
    else:
        lines.append("No successful or failed evaluation entries have been recorded yet.")
    lines.extend(
        [
            "",
            "## Deep-RL ±5% Comparison",
            "",
            "This table compares the best recorded transparent heuristic/search result against the best recorded `rl-*` result on the same split. This is a secondary comparator, not the primary pass/fail cutoff. `Within ±5%?` is strict parity; `At least 95% of RL?` treats outperforming the recorded RL baseline as satisfying a non-inferiority check. Missing RL entries mean the neural/RL comparison is unavailable for that environment.",
            "",
        ]
    )
    lines.extend(_deep_rl_comparison_lines(rows))
    lines.extend(
        [
            "",
            "## Benchmark Threshold Cutoff",
            "",
            "This table compares the best transparent holdout result against the environment success target used as a solved-score cutoff. `5% tolerance cutoff` means 95% of a positive target or 5% worse than a negative target.",
            "",
        ]
    )
    lines.extend(_benchmark_threshold_lines(rows))
    lines.extend(
        [
            "",
            "## Fresh Audit Solved-Score Check",
            "",
            "This table uses the separate audit split for post-holdout confirmation. Missing entries mean that environment has not been audited on the fresh split yet.",
            "",
        ]
    )
    lines.extend(_audit_threshold_lines(rows))
    lines.extend(
        [
            "",
            "## Policy Evolution Timeline",
            "",
        ]
    )
    if rows:
        for row in rows:
            lines.append(
                f"- `{row['timestamp']}` `{row['environment']}` `{row['policy_version']}` "
                f"({row['change_type']}): {row['change_summary']}"
            )
    else:
        lines.append("- No policy-evolution trials recorded yet.")

    lines.extend(
        [
            "",
            "## Structural Changes",
            "",
            "- CartPole improved policy adds a center-cart guard that activates only when pole angle and angular velocity are already safe.",
            "- MountainCar improved policy adds a transparent finite-horizon planner over the known MountainCar dynamics.",
            "- Acrobot improved policy adds an upright-region mode and a later stateful low-height recovery experiment; the separate `tree` policy is an explicit decision tree distilled from the recorded PPO comparator on non-holdout seeds.",
            "- LunarLander improved policy adds leg-contact and low-altitude landing guards.",
            "- BipedalWalker improved policy uses an explicit support/swing/push-off state-machine gait adapted from Gymnasium's transparent heuristic and tuned only on development seeds.",
            "",
            "## Failed Or Partial Directions",
            "",
        ]
    )
    partial_lines = _holdout_partial_lines(latest_rows)
    if failures_by_env:
        for env_id, failures in sorted(failures_by_env.items()):
            for failure in failures:
                lines.append(f"- {env_id}: {failure}")
    if partial_lines:
        lines.extend(partial_lines)
    if not failures_by_env and not partial_lines:
        lines.append("- No failed or partial trials recorded yet.")

    lines.extend(
        [
            "",
            "## Cost Accounting",
            "",
            f"- Ledger trials: {cost['trials']}",
            f"- Failed trials: {cost['failed_trials']}",
            f"- Episodes: {cost['episodes']}",
            f"- Environment steps: {cost['environment_steps']}",
            f"- Wall-clock seconds: {cost['wall_clock_seconds']:.3f}",
            f"- Agent iterations recorded: {cost['agent_iterations']}",
            f"- Code edits recorded: {cost['code_edits']}",
            "- LLM token counts: recorded as unavailable unless exposed by the runtime.",
            "",
            "## Limitations",
            "",
            "- This is a minimal benchmark, not a definitive control benchmark.",
            "- Structural heuristic quality is constrained by the small implementation budget.",
            "- Box2D installation failures are treated as experiment failures unless resolved and rerun.",
            "- Scalar search is capped and should be interpreted as a small baseline, not as exhaustive optimization.",
            "- The neural/RL section mixes locally trained Stable-Baselines3 runs with optional pretrained comparators; local runs use limited fixed budgets and several attempts remain undertrained.",
            "- The Acrobot `tree` policy is transparent at inference time but distilled from a PPO teacher, so it should be interpreted separately from purely hand-written structural rules.",
            "",
            "## Conclusion",
            "",
        ]
    )
    if rows:
        lines.append(_holdout_conclusion(latest_rows))
        lines.append("")
        lines.append(_deep_rl_goal_summary(rows))
        lines.append("")
        lines.append(_benchmark_threshold_summary(rows))
        audit_summary = _audit_threshold_summary(rows)
        if audit_summary is not None:
            lines.append("")
            lines.append(audit_summary)
    else:
        lines.append(
            "No conclusion is justified until evaluation entries are recorded in the append-only ledger."
        )

    report = "\n".join(lines) + "\n"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    render_report(ledger_path=args.ledger, summary_path=args.summary, report_path=args.report)
    print(f"wrote {args.report}")


if __name__ == "__main__":
    main()

