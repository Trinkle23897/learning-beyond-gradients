"""Generate a SlimeVolley-specific experiment report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_ledger_path, env_report_path, env_results_dir, env_summary_path
from hl_benchmark.envs import SEED_SPLITS
from hl_benchmark.environments import registration_for
from hl_benchmark.ledger import read_entries, write_summary_csv
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID, dependency_versions
from hl_benchmark.slimevolley.critic import CRITIC_FILENAME_PREFIX, DEFAULT_CRITIC_REPORT_DIR, DEFAULT_OMX_ARTIFACT_DIR
from hl_benchmark.slimevolley.amendments import (
    apply_ledger_amendments,
    default_amendments_path,
    read_ledger_amendments,
)
from hl_benchmark.slimevolley.opponents import OPPONENT_POOL
from hl_benchmark.slimevolley.schema import CANONICAL_CHANGE_TYPES


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stats(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _score_mean(entry: dict[str, Any] | None) -> float | None:
    if entry is None:
        return None
    value = entry.get("score_stats", {}).get("mean")
    return float(value) if isinstance(value, (int, float)) else None


def _latest_runtime_metadata(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the newest ledger runtime metadata captured during evaluation."""

    for entry in reversed(entries):
        metadata = entry.get("runtime_metadata")
        if isinstance(metadata, dict):
            return metadata
    return {}


def _package_versions_for_report(
    *,
    diagnostics: dict[str, Any] | None,
    runtime_metadata: dict[str, Any],
    generator_package_versions: dict[str, str],
) -> dict[str, str]:
    """Prefer recorded evaluation metadata over the current report process."""

    versions: dict[str, str] = {}
    runtime_packages = runtime_metadata.get("packages")
    if isinstance(runtime_packages, dict):
        versions.update({str(key): str(value) for key, value in runtime_packages.items()})
    if diagnostics:
        diagnostic_packages = diagnostics.get("packages")
        if isinstance(diagnostic_packages, dict):
            versions.update({str(key): str(value) for key, value in diagnostic_packages.items()})
    if not versions:
        versions.update(generator_package_versions)
    return versions


def _runtime_metadata_lines(runtime_metadata: dict[str, Any]) -> list[str]:
    if not runtime_metadata:
        return ["No ledger runtime metadata recorded yet."]
    lines = [
        "Runtime metadata is taken from the latest ledger row, not from the current report-generation process.",
        "",
        f"- Python: `{runtime_metadata.get('python', 'unknown')}`",
        f"- Platform: `{runtime_metadata.get('platform', 'unknown')}`",
    ]
    packages = runtime_metadata.get("packages")
    if isinstance(packages, dict) and packages:
        lines.append("- Package snapshot: recorded in the dependency table above.")
    return lines


def _sum_numeric(entries: list[dict[str, Any]], key: str) -> float:
    total = 0.0
    for entry in entries:
        value = entry.get(key)
        if isinstance(value, (int, float)):
            total += float(value)
    return total


def _latest_entry_map(entries: list[dict[str, Any]], split: str) -> dict[tuple[Any, Any], dict[str, Any]]:
    latest: dict[tuple[Any, Any], dict[str, Any]] = {}
    for entry in entries:
        if entry.get("pass_fail") != "pass":
            continue
        if entry.get("seed_range", {}).get("split") != split:
            continue
        latest[(entry.get("policy_version"), entry.get("opponent_name"))] = entry
    return latest


def _seed_range_lines(entries: list[dict[str, Any]]) -> list[str]:
    lines = [
        "Fixed seed ranges are declared centrally in `hl_benchmark.envs.SEED_SPLITS`.",
        "",
        "| Split | Seeds | Intended use | Recorded rows | Recorded episodes | Recorded steps |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    intended_use = {
        "smoke": "dependency and harness smoke checks",
        "dev": "diagnosis, policy iteration, and scalar search",
        "holdout": "final-only evaluation after policies are frozen",
        "audit": "reserved future audit seeds; not used in this SlimeVolley run",
    }
    for split, seed_range in SEED_SPLITS.items():
        split_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") == split]
        if seed_range:
            seed_label = f"{seed_range.start}..{seed_range.stop - 1}"
        else:
            seed_label = "empty"
        lines.append(
            "| {split} | `{seeds}` | {use} | {rows} | {episodes} | {steps} |".format(
                split=split,
                seeds=seed_label,
                use=intended_use.get(split, ""),
                rows=len(split_entries),
                episodes=int(_sum_numeric(split_entries, "episodes")),
                steps=int(_sum_numeric(split_entries, "environment_steps")),
            )
        )
    if any(entry.get("seed_range", {}).get("split") == "holdout" for entry in entries):
        lines.append("")
        lines.append(
            "Holdout rows are already present, so future policy changes must use a new, predeclared experiment generation rather than reusing these final seeds."
        )
    return lines


def _policy_evolution_lines(entries: list[dict[str, Any]]) -> list[str]:
    policy_descriptions = [
        (
            "random",
            "random baseline",
            "Seeded MultiBinary(3) actions; not an interpretable controller.",
        ),
        (
            "initial",
            "initial handwritten heuristic",
            "Tracks the ball, predicts a short landing x position, jumps near descending contact, and returns home otherwise.",
        ),
        (
            "improved-v0",
            "structural archive",
            "Adds serve, recovery, and high-arc handling. Frozen before low_ball_rescue.",
        ),
        (
            "improved-v1",
            "structural archive",
            "Adds low_ball_rescue for fast low balls on the agent side. Frozen before late_low_ball_guard.",
        ),
        (
            "improved-v2",
            "structural archive",
            "Adds late_low_ball_guard to avoid jumping when already above a late low ball. Frozen before grounded_low_receive.",
        ),
        (
            "improved-v3",
            "structural archive",
            "Adds grounded_low_receive and is frozen before the kept generation-3 rear_wall_press branch.",
        ),
        (
            "improved-v4",
            "structural archive",
            "Adds generation-3 rear_wall_press and is frozen before generation-4 front_hit_suppression.",
        ),
        (
            "improved-v5",
            "structural archive",
            "Adds generation-4 front_hit_suppression and is frozen before rear_wall_low_jump.",
        ),
        (
            "improved-v6",
            "structural archive",
            "Adds rear_wall_low_jump and is frozen before front_net_low_scoop.",
        ),
        (
            "improved",
            "current structural heuristic",
            "Retains rear_wall_low_jump after the front_net_low_scoop attempt was rolled back for weaker development performance.",
        ),
        (
            "improved-tuned",
            "generation-4 scalar/config tuned heuristic",
            "Keeps the current structural rules but tunes contact_x_window, high_arc_horizon, overcommit_guard_x, low_ball_rescue_x_window, grounded_low_receive_airborne_margin, x_margin, and low_ball_rescue_horizon on development seeds; counted separately from structural improvements.",
        ),
        (
            "attack",
            "generation-4 structural attack candidate",
            "Adds a narrow late_contact_attack forward+jump rule to improved-tuned v2; partial evidence only because it improves built-in score but regresses nearest archived opponents and remains below baseline-rnn.",
        ),
        (
            "temporal",
            "generation-4 temporal candidate",
            "Adds short stacked-history contact/phase features as a development-only candidate; not promoted over improved because evidence is mixed.",
        ),
        (
            "planner",
            "generation-4 physics planner candidate",
            "Adds time-to-floor, net-clearance, one-wall-bounce, opponent-commitment, and jump-budget features as a pure structural heuristic candidate.",
        ),
        (
            "teacher-assisted",
            "generation-4 teacher-assisted planner candidate",
            "Keeps the planner transparent while reserving labeled margins/rules for hand-audited baseline-rnn development-trace suggestions; no RNN runtime calls.",
        ),
        (
            "tuned",
            "scalar/config search baseline",
            "Uses scalar changes to the initial heuristic; it is not counted as structural policy improvement.",
        ),
        (
            "baseline-rnn",
            "pretrained neural/RNN comparator",
            "Wraps slimevolleygym's shipped 120-parameter BaselinePolicy; included only as a labeled neural comparator.",
        ),
    ]
    first_seen: dict[str, str] = {}
    last_seen: dict[str, str] = {}
    row_counts: Counter[str] = Counter()
    for entry in entries:
        policy = str(entry.get("policy_version", ""))
        if not policy:
            continue
        row_counts[policy] += 1
        first_seen.setdefault(policy, entry.get("timestamp", ""))
        last_seen[policy] = entry.get("timestamp", "")

    lines = [
        "Policy code lives in `hl_benchmark/policies/slimevolley.py`; construction is routed through `hl_benchmark/policies/factory.py`.",
        "Timeline rows aggregate generation-1, generation-2, and generation-3 ledgers when those artifacts are present, plus generation-4 development rows when present.",
        "",
        "| Version | Classification | Interpretable change | Ledger rows | First seen | Last seen |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for policy, classification, description in policy_descriptions:
        lines.append(
            "| {policy} | {classification} | {description} | {rows} | {first} | {last} |".format(
                policy=policy,
                classification=classification,
                description=description,
                rows=row_counts.get(policy, 0),
                first=first_seen.get(policy, ""),
                last=last_seen.get(policy, ""),
            )
        )
    return lines


def _artifact_manifest_lines() -> list[str]:
    return [
        "| Artifact | Role | Produced or refreshed by | Verified by |",
        "| --- | --- | --- | --- |",
        "| `hl_benchmark/custom_envs/slimevolley/` | Registry-facing custom harness bridge; delegates to `hl_benchmark/slimevolley/` for the established implementation. | registration and Makefile targets | `make check-env ENV=SlimeVolley-v0` custom-harness import and entrypoint checks |",
        "| `results/trials.jsonl` | Append-only SlimeVolley trial ledger, including failed rows. | evaluation/search/tournament/holdout commands | `make slimevolley-audit` |",
        "| `results/trial_amendments.jsonl` | Append-only metadata amendments for historical generation-1 ledger rows. | `python -m hl_benchmark.slimevolley.amendments --ledger results/trials.jsonl` | audit checks row indexes, entry SHA256 hashes, and amended `tests_pass_fail` values |",
        "| `results/summary.csv` | Regenerated CSV projection of the ledger. | `make slimevolley-summary` or `make slimevolley-verify` | `make slimevolley-audit` field-by-field summary check |",
        "| `results/environment_diagnostics.json` | Recorded package/API/runtime diagnostics for the legacy SlimeVolley stack. | `make slimevolley-doctor` | `make slimevolley-audit` diagnostics schema check |",
        "| `results/search_best_dev.json` | Scalar/config-search selection artifact from development seeds only. | `make slimevolley-search` | `make slimevolley-audit` schema, split, presence, and hash check |",
        "| `results/round_robin_dev.json` | Development-seed opponent-pool tournament artifact. | `make slimevolley-tournament SPLIT=dev` | `make slimevolley-audit` schema, split, matrix, standings, and hash check |",
        "| `results/holdout_final.json` | Final-only holdout matrix over frozen policies and opponents. | `make slimevolley-final-eval` once per experiment generation | `make slimevolley-audit` seed/matrix/anti-tuning checks |",
        "| `results/audit_latest.json` | Latest machine-readable artifact audit snapshot, including artifact/source SHA256 hashes plus parsed requirement status rows. | `make slimevolley-verify` | inspect `pass_fail`, `issues`, `artifact_hashes`, `source_hashes`, `requirements_audit_status_counts`, `requirements_audit_partial_rows`, `requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, `requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications` |",
        "| `configs/generation_2_protocol.json` | Predeclared fresh SlimeVolley generation-2 seed, ledger, opponent, and anti-tuning protocol. | `make slimevolley-protocol` or `make slimevolley-verify` | `make slimevolley-audit` seed-overlap, command, guardrail, and hash checks |",
        "| `results/generation_2_trials.jsonl` | Append-only generation-2 ledger for fresh development, scalar-search, tournament, and final-only holdout rows. | generation-2 evaluation/search/tournament/holdout commands | `make slimevolley-audit` generation-2 ledger schema, seed-range, and hash checks |",
        "| `results/generation_2_summary.csv` | Regenerated CSV projection of the generation-2 ledger. | generation-2 ledger-producing commands | `make slimevolley-audit` generation-2 summary row-count/content/hash checks |",
        "| `results/search_best_g2_dev.json` | Generation-2 scalar/config-search selection artifact from development seeds only. | generation-2 scalar-search command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 search artifact checks |",
        "| `results/round_robin_g2_dev.json` | Generation-2 development-seed opponent-pool tournament artifact. | generation-2 tournament command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 tournament matrix/content/hash checks |",
        "| `results/holdout_g2_final.json` | Generation-2 final-only holdout matrix once policy/config/opponent pool are frozen. | generation-2 final holdout command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 holdout anti-tuning and matrix checks when present |",
        "| `reports/final_report.md` | Generated final report and conclusion. | `make slimevolley-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/hash checks |",
        "| `reports/performance_deepdive.md` | Generated performance-focused explanation of current SlimeVolley scores. | `make slimevolley-performance-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/hash checks |",
        "| `reports/generation_2_diagnosis.md` | Generated diagnosis of generation-2 trial rows, failures, dependency state, costs, and holdout lock. | `make slimevolley-generation-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |",
        "| `reports/generation_2_protocol.md` | Human-readable generation-2 protocol for reviewers. | `make slimevolley-protocol` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |",
        "| `configs/generation_3_protocol.json` | Predeclared generation-3 seed, ledger, opponent, and anti-tuning protocol. | `make slimevolley-generation3-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |",
        "| `results/generation_3_trials.jsonl` | Append-only generation-3 ledger for fresh development rows after generation-2 holdout consumption. | generation-3 development/search/tournament/holdout commands in `generation_3_protocol.md` | targeted report tests and reviewer inspection |",
        "| `results/generation_3_summary.csv` | Regenerated CSV projection of the generation-3 ledger. | generation-3 ledger-producing commands | targeted report tests and reviewer inspection |",
        "| `results/contact_diagnostics_g3_dev.json` | Machine-readable contact/return diagnostic summary from generation-3 development traces only. | `make slimevolley-contact-diagnostics` or `make slimevolley-verify` | report/audit manifest checks and reviewer inspection |",
        "| `reports/contact_diagnostics_g3_dev.md` | Markdown contact/return diagnostic report for generation-3 development traces. | `make slimevolley-contact-diagnostics` or `make slimevolley-verify` | report/audit manifest checks and reviewer inspection |",
        "| `reports/generation_3_diagnosis.md` | Generated diagnosis of generation-3 trial rows, dependency failures, costs, and holdout lock. | `make slimevolley-generation3-report` or `make slimevolley-verify` | targeted report tests and reviewer inspection |",
        "| `reports/generation_3_protocol.md` | Human-readable generation-3 protocol for reviewers and final-only holdout guardrails. | `make slimevolley-generation3-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |",
        "| `configs/generation_4_protocol.json` | Predeclared generation-4 seed, ledger, opponent, and anti-tuning protocol for any future SlimeVolley policy work. | `make slimevolley-generation4-protocol` or `make slimevolley-verify` | `make slimevolley-audit` seed-overlap, command, guardrail, and hash checks |",
        "| `reports/generation_4_protocol.md` | Human-readable generation-4 protocol for reviewers before any future SlimeVolley tuning. | `make slimevolley-generation4-protocol` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |",
        "| `configs/generation_5_protocol.json` | Predeclared generation-5 seed, ledger, opponent, and anti-tuning protocol for post-generation-4 SlimeVolley work. | `make slimevolley-generation5-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |",
        "| `reports/generation_5_protocol.md` | Human-readable generation-5 protocol for reviewers before fresh post-generation-4 tuning. | `make slimevolley-generation5-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |",
        "| `notes/generation_5_net_pressure_attempt.md` | Development-only note for the `net-pressure` structural probe, fixed seed results, and no-holdout promotion recommendation. | maintained with generation-5 dev-only evidence | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `notes/generation_5_fixed_pool_comparator.md` | Development-only fixed-pool comparator note for `net-pressure`, `baseline-rnn`, and `rally-serve` on generation-5 dev seeds. | maintained after generation-5 fixed-pool comparator rows | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `notes/generation_5_hard_opponent_trace_and_probe.md` | Development-only hard-opponent trace and failed/mixed front-net, brace-action, and contact-quality probe note for generation-5. | maintained after generation-5 hard-opponent diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `notes/generation_5_post_contact_comparison.md` | Development-only post-contact transfer and net-post-contact combination note for generation-5; records ledgered fixed-pool rows and no-promotion decision. | maintained after generation-5 post-contact comparison rows | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `notes/generation_5_aggressive_pressure_and_brace_probe.md` | Development-only aggressive pressure, brace-serve, and conditional brace probe note for generation-5; records rejected broad jump/brace directions. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `notes/generation_5_stacked_followthrough_and_posture_probe.md` | Development-only stacked followthrough, front-low recovery, and opponent-posture gated pressure note for generation-5; records mixed/rejected no-ledger probes. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `notes/generation_5_phase_pressure_probe.md` | Development-only phase-pressure note for generation-5; records mixed two-frame opponent-side pressure probes and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_phase_pressure_probe.py` | Development-only phase-pressure probe script for temporary generation-5 structural/history candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_phase_pressure_probe.json` | JSON results for the development-only phase-pressure probe; records screen and full fixed-pool rows with no promotion. | `python experiments/slimevolley/probes/g5_phase_pressure_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_teacher_serve_probe.md` | Development-only teacher-serve macro note for generation-5; records archived short-screen gains, built-in regression, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_teacher_serve_probe.py` | Development-only teacher-serve macro probe script for fixed reset/serve candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_teacher_serve_probe.json` | JSON results for the development-only teacher-serve macro probe; records short-screen rows and a full fixed-pool check for `serve_110_10`. | `python experiments/slimevolley/probes/g5_teacher_serve_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_context_reset_probe.md` | Development-only context-reset macro note for generation-5; records an initially inert detector, corrected active previous-point reset classifier, mixed fixed-pool results, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_context_reset_probe.py` | Development-only context-conditioned reset macro probe script for previous-point reset macro candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_context_reset_probe.json` | JSON results for the development-only context-reset probe; records failed no-op classifier screen, corrected screen, and full fixed-pool checks. | `python experiments/slimevolley/probes/g5_context_reset_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_rally_setup_probe.md` | Development-only rally-setup note for generation-5; records failed post-contact front-anchor structural/history probes and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_rally_setup_probe.py` | Development-only rally-setup probe script for post-own-contact front-anchor candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_rally_setup_probe.json` | JSON results for the development-only rally-setup probe; records fixed short-screen rows on `12000..12015`. | `python experiments/slimevolley/probes/g5_rally_setup_probe.py --phase screen` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_contact_timing_probe.md` | Development-only contact-timing note for generation-5; records low front-court trace diagnostics, no-op/tied jump override probes, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_contact_timing_probe.py` | Development-only contact-timing diagnostic/probe script for low front-court jump/contact candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_contact_timing_probe.json` | JSON results for the development-only contact-timing diagnostic and short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_contact_timing_probe.py --phase diagnose/screen` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_approach_quality_probe.md` | Development-only approach-quality note for generation-5; records pre-contact trace diagnostics, harmful early-jump probes, mixed/no-op approach probes, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_approach_quality_probe.py` | Development-only approach-quality diagnostic/probe script for pre-contact movement and early jump candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_approach_quality_probe.json` | JSON results for the development-only approach-quality diagnostic and short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_approach_quality_probe.py --phase diagnose/screen` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_contact_quality_probe.md` | Development-only contact-quality note for generation-5; records recent-contact/descent/brace probes, hard-tail nudges with built-in regressions, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_contact_quality_probe.py` | Development-only contact-quality probe script for short-history pressure gates and RNN-like brace action candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_contact_quality_probe.json` | JSON results for the development-only contact-quality short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_contact_quality_probe.py --phase screen` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_position_posture_probe.md` | Development-only position/posture scalar-config note for generation-5; records front-shifted home-anchor probes, archived-row tradeoffs, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_position_posture_probe.py` | Development-only front-posture scalar/config probe script around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_position_posture_probe.json` | JSON results for the development-only position/posture short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_position_posture_probe.py --phase screen` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_5_planner_takeover_probe.md` | Development-only planner-takeover structural note for generation-5; records harmful/inert transient planner delegation probes and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |",
        "| `probes/g5_planner_takeover_probe.py` | Development-only transient planner-takeover probe script around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_5_planner_takeover_probe.json` | JSON results for the development-only planner-takeover short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_planner_takeover_probe.py --phase screen` | reviewer inspection; development-seed evidence only |",
        "| `results/generation_4_trials.jsonl` | Append-only generation-4 ledger for development rows and final-only holdout rows. | generation-4 development and final holdout commands | reviewer inspection, `reports/generation_4_temporal_history_attempt.md`, and `results/holdout_g4_final.json` |",
        "| `results/generation_4_summary.csv` | CSV projection of the generation-4 ledger, including final-only holdout rows when present. | generation-4 ledger-producing commands | reviewer inspection |",
        "| `results/holdout_g4_final.json` | Generation-4 final-only holdout matrix over frozen policies, including `rally-serve` and `baseline-rnn`. | `make slimevolley-final-eval` after policy/config/opponent/test freeze | reviewer inspection and `make slimevolley-audit` seed/matrix/anti-tuning checks |",
        "| `reports/generation_4_temporal_history_attempt.md` | Development-only report for the stacked-history temporal candidate, including failed sub-hypotheses and paired controls. | maintained with generation-4 temporal evaluations | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_4_scalar_tuned_structural_attempt.md` | Development-only note for the `improved-tuned` scalar/config baseline and remaining neural comparator gap. | maintained with generation-4 scalar/config evidence | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_4_late_contact_attack_attempt.md` | Development-only note for the `attack` structural candidate, archived-opponent regressions, and remaining neural comparator gap. | maintained with generation-4 attack candidate evidence | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_4_joint_attack_scalar_search_attempt.md` | Development-only note for the failed/partial scalar search around `attack`; records the built-in-specific `-0.10` candidate and archived-opponent regressions. | maintained with generation-4 throwaway search evidence | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_4_low_receive_teacher_scalar_followup.md` | Development-only note for the failed teacher-action low-receive structural probes and bounded scalar/config follow-up search. | maintained with generation-4 dev-only follow-up evidence | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_4_rally_serve_candidate.md` | Development-only note for the rally-serve structural candidate that beat baseline-rnn on built-in development seeds before failing to beat it on final-only holdout. | maintained with generation-4 dev-only candidate evidence | reviewer inspection plus `results/holdout_g4_final.json` |",
        "| `notes/parallel/` | Development-only parallel worker notes for scalar search, grounded-low-receive probes, rear-wall probes, and robustness checks. | parallel worker runs on generation-4 dev seeds only | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/parallel_synthesis.md` | Synthesis report comparing parallel worker results and recording the no-promotion decision. | maintained after parallel worker completion | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_parallel_synthesis_rallyserve.md` | Dated synthesis of the rally-serve parallel worker pass; records that scalar/config, stacked low-receive, and rear-wall probes tied or regressed and no new candidate was promoted. | maintained after 2026-05-27 parallel worker completion | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_trace_rally_attack_rnn_worker.md` | Dated development-only trace comparison of `rally-serve`, `attack`, and `baseline-rnn` against the built-in opponent. | parallel trace diagnostics worker on generation-4 dev seeds | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_attack_scalar_subagent_v2.md` | Development-only v2 scalar/config probe around `rally-serve`; records tied built-in variants, incomplete/mixed fixed-pool rows, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/g4_attack_scalar_worker_a_20260527.md` | Development-only Worker A scalar/config search around `attack`/`net-pressure`; records mixed fixed-pool scalar results and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_grounded_low_receive_subagent_v2.md` | Development-only v2 stacked-frame grounded-low-receive probe; records a tie with `rally-serve` and rejects broad low-incoming modes. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/g4_grounded_low_receive_worker_b_screen.md` | Development-only Worker B grounded-low-receive short-screen note; records harmful/tied structural branch probes and no full-pool expansion. | no-ledger generation-4 short-screen diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_rear_wall_press_subagent_v2.md` | Development-only v2 rear-wall press probe; records harmful/tied wall-clear variants and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/g4_rear_wall_press_worker_c_20260527.md` | Development-only Worker C rear-wall press probe; records narrow built-in gain, fixed-pool regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_archived_robustness_subagent_v2.md` | Development-only v2 archived-opponent robustness note; records interrupted rerun and canonical fixed-pool regression versus `baseline-rnn`. | no-ledger generation-4 dev diagnostics plus existing summary rows | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_trace_attack_vs_rnn_subagent_v2.md` | Development-only v2 attack/rally-serve/RNN trace report on `9000..9015`. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/g4_trace_attack_vs_baseline_rnn_worker_d_20260527.md` | Development-only Worker D trace report comparing `attack`, `net-pressure`, and `baseline-rnn` on generation-4 dev seeds; records no promotion. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_parallel4_synthesis.md` | Development-only Worker A-E synthesis report for generation-4 parallel4 diagnostics; records no maintained edit and no promotion. | maintained after 2026-05-27 parallel4 worker completion | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel5_attack_scalar.md` | Development-only parallel5 attack scalar/config search; records a partial `attack` improvement that remained below `baseline-rnn` and `rally-serve`, with no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel5_grounded_low_receive.md` | Development-only parallel5 grounded-low-receive screen; records action-changing ties and one built-in regression, with no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `results/generation_4_parallel5_grounded_low_receive_screen.json` | JSON rows for the development-only parallel5 grounded-low-receive screen on seeds `9000..9015`. | no-ledger generation-4 dev screen | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel5_rear_wall_press.md` | Development-only parallel5 rear-wall press screen; records a narrow built-in tie, archived regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `results/generation_4_parallel5_rear_wall_press_probe.json` | JSON rows for the development-only parallel5 rear-wall press screen on seeds `9000..9015`. | no-ledger generation-4 dev screen | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_parallel5_trace_attack_rnn.md` | Development-only parallel5 trace diagnostic comparing `attack`, `rally-serve`, `post-contact`, and `baseline-rnn` on generation-4 dev seeds. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_parallel5_synthesis.md` | Development-only parallel5 synthesis for grounded-low-receive, rear-wall, and trace diagnostics; records no maintained edit. | maintained after 2026-05-27 parallel5 worker completion | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel6_attack_scalar.md` | Development-only parallel6 scalar/config search around `rally-serve`; records `low_x_0.52` as a fixed-pool-checked scalar candidate. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel6_grounded_low_receive.md` | Development-only parallel6 grounded-low-receive structural/history probe; records fixed-pool ties and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel6_rear_wall_press.md` | Development-only parallel6 rear-wall press probe; records small built-in gains, archived-opponent regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel6_archived_robustness.md` | Development-only parallel6 archived-opponent robustness note comparing `rally-serve`, `post-contact`, `net-pressure`, `rw_press_forcejump`, and `baseline-rnn`. | no-ledger generation-4 dev robustness review | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_parallel6_trace_attack_rnn.md` | Development-only parallel6 trace diagnostic comparing `attack`, `rally-serve`, and `baseline-rnn` on generation-4 dev seeds. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_parallel6_synthesis.md` | Development-only parallel6 synthesis; records the single supported edit as a named scalar/config candidate, not structural progress. | maintained after 2026-05-27 parallel6 worker completion | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_parallel_subagent_synthesis_v2.md` | Development-only v2 synthesis of scalar, structural, trace, and robustness subagent artifacts; records no promotion decision. | maintained after 2026-05-27 v2 parallel worker completion | reviewer inspection; development-seed evidence only |",
        "| `probes/g4_post_contact_gate_probe.py` | Development-only post-contact gate probe script for temporary structural/history candidates around `rally-serve`. | manual no-ledger generation-4 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_4_post_contact_gate_probe.json` | JSON results for the development-only post-contact gate probe; records screen and full fixed-pool rows with no promotion. | `python experiments/slimevolley/probes/g4_post_contact_gate_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_post_contact_gate_probe.md` | Development-only post-contact gate probe note; records short-screen and fixed-pool results plus the no-promotion decision. | maintained after 2026-05-27 post-contact probe completion | reviewer inspection; development-seed evidence only |",
        "| `probes/g4_stacked_low_receive_probe.py` | Development-only stacked low-receive probe script for temporary structural/history candidates around `post-contact`. | manual no-ledger generation-4 dev probe | reviewer inspection; development-seed evidence only |",
        "| `results/generation_4_stacked_low_receive_probe.json` | JSON results for the development-only stacked low-receive probe; records screen and full fixed-pool rows with no promotion. | `python experiments/slimevolley/probes/g4_stacked_low_receive_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_4_stacked_low_receive_probe.md` | Development-only stacked low-receive probe note; records short-screen hard-tail gains, full-pool built-in regression, and no-promotion decision. | maintained after 2026-05-27 stacked low-receive probe completion | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/g4_archived_opponent_robustness_post_contact_worker_e.md` | Development-only Worker E archived-opponent robustness note for `post-contact`; records fixed-pool rows and no final promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/generation_4_post_contact_front_conversion_attempt.md` | Development-only post-contact front-conversion note; records small archived-opponent gains, registered development-only candidate, and no final claim. | maintained after 2026-05-27 post-contact probe and code registration | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel3_attack_scalar.md` | Development-only parallel3 scalar/config search around `rally-serve`; records built-in-only ties/small same-W-L-D gains and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel3_grounded_low_receive.md` | Development-only parallel3 grounded-low-receive history probe; records action-changing ties, fixed-pool no-gain results, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel3_rear_wall_press.md` | Development-only parallel3 rear-wall structural probe; records narrow built-in gain, fixed-pool regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |",
        "| `reports/parallel/20260527_g4_parallel3_trace_attack_rnn.md` | Development-only parallel3 trace diagnostics comparing `attack`, `rally-serve`, `net-pressure`, and `baseline-rnn` on generation-4 dev seeds. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |",
        "| `results/generation_4_net_pressure_noledger_probe.json` | JSON rows for the development-only generation-4 `net-pressure` fixed-pool no-ledger probe. | no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_net_pressure_fixed_pool_noledger.md` | Development-only generation-4 `net-pressure` fixed-pool note; records built-in regression and no promotion. | maintained after no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |",
        "| `notes/parallel/20260527_g4_parallel3_archived_robustness.md` | Development-only parallel3 archived-opponent robustness note; compares `rally-serve`, `post-contact`, `net-pressure`, and `baseline-rnn` and records no promotion. | maintained after no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |",
        "| `reports/critic/` and `.omx/artifacts/` | Optional Claude Code CLI critic artifacts, each containing prompt, raw output, hashes, and advisory next-step suggestions. | `make slimevolley-critic ARGS=\"--allow-external-claude\"` or offline `--mock-output` runs | reviewer inspection; labeled external advisory context only |",
        "| `notes/generation_3_start.md` | Human-readable note for the first generation-3 dependency failure and corrected development diagnostic. | maintained with generation-3 setup changes | reviewer inspection |",
        "| `notes/generation_3_rear_wall_recovery_attempt.md` | Human-readable failure note for the rolled-back rear-wall recovery structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |",
        "| `notes/generation_3_delayed_low_receive_attempt.md` | Human-readable failure note for the rolled-back delayed low receive structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |",
        "| `notes/generation_3_rally_restart_serve_attempt.md` | Human-readable failure note for the rolled-back rally restart serve structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |",
        "| `notes/generation_3_rear_wall_press_attempt.md` | Human-readable note for the kept rear-wall press structural improvement. | maintained with generation-3 policy iterations | reviewer inspection |",
        "| `notes/generation_3_freeze_before_holdout.md` | Human-readable freeze note declaring the generation-3 policy/config/opponent/test state before final holdout. | maintained before generation-3 final holdout | reviewer inspection |",
        "| `reports/requirements_audit.md` | Requirement-by-requirement coverage matrix for reviewer traceability. | maintained with SlimeVolley experiment changes | `make slimevolley-audit` required-section/snippet/hash checks |",
    ]


def _artifact_integrity_lines(entries: list[dict[str, Any]]) -> list[str]:
    holdout_used = any(entry.get("seed_range", {}).get("split") == "holdout" for entry in entries)
    holdout_seeds = SEED_SPLITS["holdout"]
    audit_seeds = SEED_SPLITS["audit"]
    holdout_label = f"{holdout_seeds.start}..{holdout_seeds.stop - 1}"
    audit_label = f"{audit_seeds.start}..{audit_seeds.stop - 1}"
    lines = [
        "`make slimevolley-audit` is the canonical artifact-integrity gate for this custom environment.",
        "",
        "It checks:",
        "",
        "- ledger schema plus SlimeVolley-specific opponent, win/loss/draw, life-difference, action-frequency, numeric-cost, and failed-row failure-analysis fields,",
        "- `summary.csv` row count and field-by-field content against the append-only ledger,",
        "- `environment_diagnostics.json` package/API fields plus seed-reset and native step-API probes,",
        "- diagnostics availability remains consistent with successful development or holdout evidence,",
        "- scalar/config tuning rows never use reserved `holdout` or `audit` splits,",
        "- `search_best_dev.json` uses the development split and contains environment, config, opponent mean, selection-score, known-opponent, and one-based candidate-budget fields,",
        "- `round_robin_dev.json` uses the development split and contains a complete known-policy participant matrix, standings table, and win/loss/draw episode totals,",
        f"- holdout rows, when present, use exactly `{holdout_label}` and one episode per seed,",
        "- holdout ledger rows are marked as final SlimeVolley holdout matchups with an explicit anti-tuning next hypothesis,",
        "- ledger rows at or after `2026-05-25T00:00:00+00:00` include explicit `tests_pass_fail`; older generation-1 rows are covered by append-only metadata amendments that record `tests_pass_fail=not_recorded`,",
        "- the holdout artifact policy/opponent matrix matches the holdout ledger rows,",
        "- `configs/generation_2_protocol.json` predeclares fresh generation-2 development, holdout, and audit seeds that do not overlap generation-1 seeds,",
        "- `reports/generation_2_protocol.md` exposes the same guardrails and commands for reviewer inspection,",
        "- `reports/generation_2_diagnosis.md` exposes generation-2 trial-row status, failures, dependency state, costs, and the holdout lock,",
        "- generation-2 ledger rows use only predeclared generation-2 split seeds and are checked independently from generation-1 rows,",
        "- `search_best_g2_dev.json` and `round_robin_g2_dev.json` are cross-checked against the generation-2 ledger timestamps and cell contents,",
        "- `holdout_g2_final.json`, when present, is checked as final-only generation-2 holdout evidence with anti-tuning metadata,",
        "- `configs/generation_3_protocol.json` and `reports/generation_3_protocol.md` predeclare generation-3 development, holdout, and audit seeds,",
        "- `reports/generation_3_diagnosis.md` exposes generation-3 trial-row status, dependency failures, costs, and final-only holdout status,",
        "- `configs/generation_4_protocol.json` and `reports/generation_4_protocol.md` are the predeclared generation-4 protocol artifacts: development seeds `9000..9049`, holdout seeds `10000..10049`, and audit seeds `11000..11049` for any future SlimeVolley policy work,",
        "- the persisted audit snapshot records SHA256 hashes for checked artifacts and SlimeVolley source files.",
        "",
        f"Audit seeds `{audit_label}` remain reserved for future independent checks.",
    ]
    if holdout_used:
        lines.append(
            "Holdout rows are already present, so future policy edits must use a fresh predeclared experiment generation instead of reusing these final seeds."
        )
    else:
        lines.append("Holdout rows are absent, so reserved final seeds remain untouched in this ledger.")
    return lines


def _reproduction_command_lines() -> list[str]:
    return [
        "Run commands from `heuristic_learning/`. The holdout command is listed for reproduction/audit only; do not rerun it for policy tuning after holdout evidence exists.",
        "",
        "```bash",
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
        "make slimevolley-critic ARGS=\"--dry-run\"",
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
        "```",
        "",
        "For new ledger-producing SlimeVolley runs, include test provenance when it is known:",
        "",
        "```bash",
        "make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev ARGS=\"--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\"",
        "```",
        "",
        "Use `--tests-pass-fail not_recorded` only when test status is genuinely unavailable. Historical rows in this experiment predate explicit `tests_pass_fail`; `results/trial_amendments.jsonl` preserves append-only amendments keyed by row index and SHA256 hash instead of rewriting those trial rows.",
        "",
        'For machine-readable checks, use `make check-env ENV=SlimeVolley-v0 ARGS="--format json"`, `make check-promotion ENV=SlimeVolley-v0 ARGS="--format json"`, `make check-promotions ARGS="--format json"`, `make check-envs ARGS="--format json"`, `make custom-run ENV=SlimeVolley-v0 ARGS="--format json"`, `make slimevolley-audit ARGS="--format json"`, and `make slimevolley-summary ARGS="--format json"`. `make slimevolley-verify` also writes `results/audit_latest.json` with artifact/source SHA256 hashes, parsed `requirements_audit_rows`, `requirements_audit_status_counts`, `requirements_audit_partial_rows`, `requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, `requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications`.',
    ]


def _result_table(entries: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Timestamp | Policy | Opponent | Split | Episodes | Mean | Wins | Losses | Draws | Win rate | Steps | Status |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for entry in entries:
        wld = entry.get("win_loss_draw", {})
        lines.append(
            "| {timestamp} | {policy} | {opponent} | {split} | {episodes} | {mean} | {wins} | {losses} | {draws} | {win_rate} | {steps} | {status} |".format(
                timestamp=entry.get("timestamp", ""),
                policy=entry.get("policy_version", ""),
                opponent=entry.get("opponent_name", ""),
                split=entry.get("seed_range", {}).get("split", ""),
                episodes=entry.get("episodes", ""),
                mean=_stats(entry.get("score_stats", {}).get("mean")),
                wins=wld.get("wins", ""),
                losses=wld.get("losses", ""),
                draws=wld.get("draws", ""),
                win_rate=_stats(wld.get("win_rate")),
                steps=entry.get("environment_steps", ""),
                status=entry.get("pass_fail", ""),
            )
        )
    return lines


def _cost_accounting_lines(
    entries: list[dict[str, Any]],
    *,
    generation_entries: list[dict[str, Any]] | None = None,
    generation3_entries: list[dict[str, Any]] | None = None,
    generation4_entries: list[dict[str, Any]] | None = None,
    generation5_entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    generation_entries = generation_entries or []
    generation3_entries = generation3_entries or []
    generation4_entries = generation4_entries or []
    generation5_entries = generation5_entries or []
    all_entries = [*entries, *generation_entries, *generation3_entries, *generation4_entries, *generation5_entries]
    if not all_entries:
        return ["No SlimeVolley ledger rows exist yet."]

    by_status = Counter(str(entry.get("pass_fail", "")) for entry in all_entries)
    by_split = Counter(str(entry.get("seed_range", {}).get("split", "")) for entry in entries)
    generation_by_split = Counter(
        str(entry.get("seed_range", {}).get("split", "")) for entry in generation_entries
    )
    by_change_type = Counter(str(entry.get("change_type", "")) for entry in all_entries)
    tests_run = sorted(
        {
            test
            for entry in all_entries
            for test in entry.get("tests_run", [])
            if test
        }
    )
    tests_pass_fail_counts = Counter(
        str(entry.get("tests_pass_fail", "legacy_missing")) for entry in all_entries
    )
    llm_cost_sources = sorted(
        {
            str(entry.get("llm_cost", {}).get("source", "missing"))
            for entry in all_entries
        }
    )
    max_agent_iterations = max(
        (
            int(entry.get("agent_iterations", 0))
            for entry in all_entries
            if isinstance(entry.get("agent_iterations", 0), int)
        ),
        default=0,
    )
    total_code_edits = int(_sum_numeric(all_entries, "code_edits"))
    scalar_entries = [entry for entry in all_entries if entry.get("change_type") == "scalar/config tuning"]
    failed_entries = [entry for entry in all_entries if entry.get("pass_fail") != "pass"]
    lines = [
        "Environment-interaction cost is reported separately from research/agent maintenance cost. "
        "Episodes and environment steps measure sample use; ledger rows, code edits, agent iterations, tests, and wall time measure the surrounding coding-agent process. "
        "This table includes generation-2, generation-3, generation-4, and generation-5 rows when separate generation ledgers are present.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Generation-1 ledger rows / evaluation records | {len(entries)} |",
        f"| Generation-2 ledger rows / evaluation records | {len(generation_entries)} |",
        f"| Generation-3 ledger rows / evaluation records | {len(generation3_entries)} |",
        f"| Generation-4 ledger rows / evaluation records | {len(generation4_entries)} |",
        f"| Generation-5 ledger rows / evaluation records | {len(generation5_entries)} |",
        f"| Total ledger rows / evaluation records | {len(all_entries)} |",
        f"| Passing rows | {by_status.get('pass', 0)} |",
        f"| Failed or partial rows | {len(failed_entries)} |",
        f"| Episodes recorded | {int(_sum_numeric(all_entries, 'episodes'))} |",
        f"| Environment steps recorded | {int(_sum_numeric(all_entries, 'environment_steps'))} |",
        f"| Wall-clock seconds recorded | {_stats(_sum_numeric(all_entries, 'wall_clock_seconds'))} |",
        f"| Max recorded agent iterations | {max_agent_iterations} |",
        f"| Sum of recorded code-edit counts | {total_code_edits} |",
        f"| Scalar-search rows | {len(scalar_entries)} |",
        f"| Scalar-search episodes | {int(_sum_numeric(scalar_entries, 'episodes'))} |",
        f"| Scalar-search environment steps | {int(_sum_numeric(scalar_entries, 'environment_steps'))} |",
        "",
        "Sample cost by evidence split:",
        "",
        "| Ledger | Split | Rows | Episodes | Environment steps | Wall-clock seconds |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    generation3_by_split = Counter(
        str(entry.get("seed_range", {}).get("split", "")) for entry in generation3_entries
    )
    generation4_by_split = Counter(
        str(entry.get("seed_range", {}).get("split", "")) for entry in generation4_entries
    )
    generation5_by_split = Counter(
        str(entry.get("seed_range", {}).get("split", "")) for entry in generation5_entries
    )
    for ledger_label, ledger_entries, split_counter in [
        ("generation-1", entries, by_split),
        ("generation-2", generation_entries, generation_by_split),
        ("generation-3", generation3_entries, generation3_by_split),
        ("generation-4", generation4_entries, generation4_by_split),
        ("generation-5", generation5_entries, generation5_by_split),
    ]:
        for split, split_count in sorted(split_counter.items()):
            split_entries = [
                entry
                for entry in ledger_entries
                if str(entry.get("seed_range", {}).get("split", "")) == split
            ]
            lines.append(
                "| {ledger} | {split} | {rows} | {episodes} | {steps} | {wall} |".format(
                    ledger=ledger_label,
                    split=split or "(missing)",
                    rows=split_count,
                    episodes=int(_sum_numeric(split_entries, "episodes")),
                    steps=int(_sum_numeric(split_entries, "environment_steps")),
                    wall=_stats(_sum_numeric(split_entries, "wall_clock_seconds")),
                )
            )

    category_rows = [
        ("random baseline", lambda entry: entry.get("policy_version") == "random"),
        ("initial handwritten heuristic", lambda entry: entry.get("policy_version") == "initial"),
        (
            "agent-maintained structural heuristics",
            lambda entry: str(entry.get("policy_version", "")).startswith("improved")
            or entry.get("policy_version") in {"temporal", "attack", "rally-serve", "net-pressure", "planner", "teacher-assisted"},
        ),
        (
            "scalar/config search baseline",
            lambda entry: entry.get("policy_version") == "tuned"
            or entry.get("change_type") == "scalar/config tuning",
        ),
        ("packaged RNN comparator", lambda entry: entry.get("policy_version") == "baseline-rnn"),
    ]
    unmatched = list(all_entries)
    category_entries: list[tuple[str, list[dict[str, Any]]]] = []
    for label, predicate in category_rows:
        matched = [entry for entry in unmatched if predicate(entry)]
        category_entries.append((label, matched))
        matched_ids = {id(entry) for entry in matched}
        unmatched = [entry for entry in unmatched if id(entry) not in matched_ids]
    if unmatched:
        category_entries.append(("harness, diagnostics, and other rows", unmatched))

    lines.extend(
        [
            "",
            "Mutually exclusive cost by comparison group:",
            "",
            "| Group | Rows | Episodes | Environment steps | Wall-clock seconds | Code-edit count sum |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for label, group_entries in category_entries:
        lines.append(
            "| {label} | {rows} | {episodes} | {steps} | {wall} | {edits} |".format(
                label=label,
                rows=len(group_entries),
                episodes=int(_sum_numeric(group_entries, "episodes")),
                steps=int(_sum_numeric(group_entries, "environment_steps")),
                wall=_stats(_sum_numeric(group_entries, "wall_clock_seconds")),
                edits=int(_sum_numeric(group_entries, "code_edits")),
            )
        )

    lines.extend(
        [
            "",
            "The packaged RNN comparator is evaluated here, but its original training sample cost is external to this ledger and is therefore not comparable to the local heuristic-maintenance sample budget.",
            "",
            f"- Generation-1 rows by split: `{dict(sorted(by_split.items()))}`",
            f"- Generation-2 rows by split: `{dict(sorted(generation_by_split.items()))}`",
            f"- Generation-3 rows by split: `{dict(sorted(generation3_by_split.items()))}`",
            f"- Generation-4 rows by split: `{dict(sorted(generation4_by_split.items()))}`",
            f"- Generation-5 rows by split: `{dict(sorted(generation5_by_split.items()))}`",
            f"- Rows by change type across all ledgers: `{dict(sorted(by_change_type.items()))}`",
            f"- Tests recorded in ledger rows: `{', '.join(tests_run) if tests_run else 'none recorded'}`",
            f"- Explicit test pass/fail statuses: `{dict(sorted(tests_pass_fail_counts.items()))}`",
            f"- LLM token/call accounting: `{', '.join(llm_cost_sources)}`",
            "- Code-edit counts are recorded per ledger row and may overcount one shared edit evaluated across multiple opponents.",
            "- Hardware was not separately exposed by the local runtime; package and platform metadata are preserved in each ledger row.",
        ]
    )
    return lines


def _failure_lines(entries: list[dict[str, Any]]) -> list[str]:
    failures = [entry for entry in entries if entry.get("pass_fail") != "pass"]
    if not failures:
        return ["No failed SlimeVolley trials recorded yet."]
    lines: list[str] = []
    for entry in failures[-10:]:
        lines.append(
            f"- `{entry.get('timestamp', '')}` `{entry.get('policy_version', '')}` vs "
            f"`{entry.get('opponent_name', '')}`: {entry.get('failure_analysis', '')}"
        )
    return lines


def _dev_diagnosis_lines(entries: list[dict[str, Any]]) -> list[str]:
    dev_entries = [
        entry for entry in entries
        if entry.get("seed_range", {}).get("split") == "dev" and entry.get("pass_fail") == "pass"
    ]
    if not dev_entries:
        return ["No development-seed SlimeVolley matrix has been recorded yet."]
    lines: list[str] = []
    by_policy_opponent = {
        (entry.get("policy_version"), entry.get("opponent_name")): entry
        for entry in dev_entries
    }
    for policy in ["random", "initial", "improved"]:
        builtin = by_policy_opponent.get((policy, "builtin"))
        if builtin is None:
            continue
        mean = builtin.get("score_stats", {}).get("mean")
        wld = builtin.get("win_loss_draw", {})
        lines.append(
            f"- `{policy}` vs `builtin`: mean `{_stats(mean)}`, wins `{wld.get('wins', '')}`, losses `{wld.get('losses', '')}`."
        )
    initial_by_opp = {
        opponent: entry.get("score_stats", {}).get("mean")
        for (policy, opponent), entry in by_policy_opponent.items()
        if policy == "initial"
    }
    improved_by_opp = {
        opponent: entry.get("score_stats", {}).get("mean")
        for (policy, opponent), entry in by_policy_opponent.items()
        if policy == "improved"
    }
    for opponent in sorted(set(initial_by_opp) & set(improved_by_opp)):
        initial_mean = initial_by_opp[opponent]
        improved_mean = improved_by_opp[opponent]
        if initial_mean is None or improved_mean is None:
            continue
        if improved_mean < initial_mean:
            lines.append(
                f"- Structural `improved` regressed vs `initial` against `{opponent}` ({improved_mean:.6g} vs {initial_mean:.6g})."
            )
        elif improved_mean > initial_mean:
            lines.append(
                f"- Structural `improved` beat `initial` against `{opponent}` ({improved_mean:.6g} vs {initial_mean:.6g})."
            )
        else:
            lines.append(
                f"- Structural `improved` tied `initial` against `{opponent}` ({improved_mean:.6g})."
            )
    lines.append(
        "- Diagnosis: low-ball rescue improves the non-built-in opponent pool, but the current structural modes still do not solve the built-in opponent."
    )
    return lines


def _evidence_verdict_lines(
    entries: list[dict[str, Any]],
    *,
    generation_entries: list[dict[str, Any]] | None = None,
    generation3_entries: list[dict[str, Any]] | None = None,
    generation4_entries: list[dict[str, Any]] | None = None,
    generation5_entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    generation_entries = generation_entries or []
    generation3_entries = generation3_entries or []
    generation4_entries = generation4_entries or []
    generation5_entries = generation5_entries or []
    has_generation4_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation4_entries
    )
    has_generation3_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation3_entries
    )
    has_generation_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation_entries
    )
    if has_generation4_holdout:
        evidence_entries = generation4_entries
        evidence_source = "generation-4 holdout"
    elif has_generation3_holdout:
        evidence_entries = generation3_entries
        evidence_source = "generation-3 holdout"
    elif has_generation_holdout:
        evidence_entries = generation_entries
        evidence_source = "generation-2 holdout"
    else:
        evidence_entries = entries
        evidence_source = "generation-1"
    split = "holdout" if any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in evidence_entries
    ) else "dev"
    by_policy_opponent = _latest_entry_map(evidence_entries, split)
    if not by_policy_opponent:
        return ["No successful development or holdout evidence exists yet."]

    evidence_label = f"{evidence_source} {split}" if evidence_source == "generation-1" else evidence_source
    lines = [
        f"Primary evidence source for this verdict: `{evidence_label}`"
        + (" (final-only; not available for further tuning)." if split == "holdout" else "."),
    ]
    initial_means = {
        opponent: _score_mean(entry)
        for (policy, opponent), entry in by_policy_opponent.items()
        if policy == "initial"
    }
    improved_means = {
        opponent: _score_mean(entry)
        for (policy, opponent), entry in by_policy_opponent.items()
        if policy == "improved"
    }
    tuned_means = {
        opponent: _score_mean(entry)
        for (policy, opponent), entry in by_policy_opponent.items()
        if policy == "tuned"
    }
    baseline_means = {
        opponent: _score_mean(entry)
        for (policy, opponent), entry in by_policy_opponent.items()
        if policy == "baseline-rnn"
    }
    rally_means = {
        opponent: _score_mean(entry)
        for (policy, opponent), entry in by_policy_opponent.items()
        if policy == "rally-serve"
    }
    common_initial = {
        opponent: improved_means[opponent] - initial_means[opponent]
        for opponent in set(improved_means) & set(initial_means)
        if improved_means[opponent] is not None and initial_means[opponent] is not None
    }
    non_builtin_initial = {
        opponent: delta for opponent, delta in common_initial.items()
        if opponent != "builtin"
    }
    if common_initial:
        better = sum(1 for value in common_initial.values() if value > 0)
        worse = sum(1 for value in common_initial.values() if value < 0)
        tied = len(common_initial) - better - worse
        avg_delta = _mean(list(common_initial.values()))
        lines.append(
            f"- `improved` versus `initial` across common `{evidence_label}` opponents: "
            f"{better} better, {worse} worse, {tied} tied; mean score delta `{_stats(avg_delta)}`."
        )
    if non_builtin_initial:
        better = sum(1 for value in non_builtin_initial.values() if value > 0)
        lines.append(
            f"- Excluding the built-in opponent, `improved` beat `initial` on "
            f"{better}/{len(non_builtin_initial)} common `{evidence_label}` opponents."
        )
    builtin_initial = initial_means.get("builtin")
    builtin_improved = improved_means.get("builtin")
    builtin_rnn = baseline_means.get("builtin")
    if builtin_initial is not None and builtin_improved is not None:
        lines.append(
            f"- Built-in opponent remains unsolved: `initial` mean `{_stats(builtin_initial)}`, "
            f"`improved` mean `{_stats(builtin_improved)}`."
        )
    if builtin_rnn is not None and builtin_improved is not None:
        lines.append(
            f"- Neural comparator gap on built-in opponent: `baseline-rnn` mean `{_stats(builtin_rnn)}` "
            f"versus `improved` mean `{_stats(builtin_improved)}`."
        )
    rally_builtin = rally_means.get("builtin")
    if builtin_rnn is not None and rally_builtin is not None:
        rally_delta = rally_builtin - builtin_rnn
        lines.append(
            f"- Current generation-4 candidate gap on built-in opponent: `rally-serve` mean `{_stats(rally_builtin)}` "
            f"versus `baseline-rnn` mean `{_stats(builtin_rnn)}`; delta `{_stats(rally_delta)}`."
        )
    common_tuned = {
        opponent: improved_means[opponent] - tuned_means[opponent]
        for opponent in set(improved_means) & set(tuned_means)
        if improved_means[opponent] is not None and tuned_means[opponent] is not None
    }
    if common_tuned:
        better = sum(1 for value in common_tuned.values() if value > 0)
        avg_delta = _mean(list(common_tuned.values()))
        lines.append(
            f"- Structural `improved` versus scalar-search `tuned`: "
            f"{better}/{len(common_tuned)} common `{evidence_label}` opponents better; mean delta `{_stats(avg_delta)}`."
        )
    lines.extend(
        [
            "- Supports the hypothesis: the agent-maintained heuristic produced interpretable structural archives and improved robustness against random, initial, and archived heuristic opponents.",
            "- Weakens the hypothesis: the maintained heuristic failed to beat the packaged RNN on the built-in final holdout, development gains did not generalize cleanly, and some late structural changes tied their predecessors.",
            "- Overall verdict for this SlimeVolley run: weak or mixed support, not a deep-RL-comparable result.",
        ]
    )
    return lines


def _anti_cheating_and_limitations_lines(
    entries: list[dict[str, Any]],
    status: str,
    *,
    generation_entries: list[dict[str, Any]] | None = None,
    generation3_entries: list[dict[str, Any]] | None = None,
    generation4_entries: list[dict[str, Any]] | None = None,
    generation5_entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    generation_entries = generation_entries or []
    generation3_entries = generation3_entries or []
    generation4_entries = generation4_entries or []
    generation5_entries = generation5_entries or []
    all_entries = [*entries, *generation_entries, *generation3_entries, *generation4_entries, *generation5_entries]
    change_types = Counter(str(entry.get("change_type", "")) for entry in all_entries)
    noncanonical = sorted(change_type for change_type in change_types if change_type not in CANONICAL_CHANGE_TYPES)
    holdout_used = any(entry.get("seed_range", {}).get("split") == "holdout" for entry in entries)
    generation_holdout_used = any(
        entry.get("seed_range", {}).get("split") == "holdout" for entry in generation_entries
    )
    generation3_holdout_used = any(
        entry.get("seed_range", {}).get("split") == "holdout" for entry in generation3_entries
    )
    generation4_holdout_used = any(
        entry.get("seed_range", {}).get("split") == "holdout" for entry in generation4_entries
    )
    generation5_holdout_used = any(
        entry.get("seed_range", {}).get("split") == "holdout" for entry in generation5_entries
    )
    lines = [
        "- The ledger is append-only; failed and partial rows remain visible rather than being deleted.",
        "- Scalar/config search is labeled separately from structural policy edits.",
        "- Archived heuristic opponents are preserved as `improved-v0`, `improved-v1`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`.",
        "- Duplicate development rows appear because diagnostics and paired comparisons were intentionally logged; the ledger is an audit trail, not a set of independent benchmark replicas.",
        "- LLM call and token counts were unavailable from the local runtime and are explicitly recorded that way.",
        "- The neural comparator is the packaged SlimeVolley RNN baseline, not a locally trained deep RL agent.",
    ]
    consumed_ranges = []
    if holdout_used:
        consumed_ranges.append("holdout seeds `1000..1049`")
    if generation_holdout_used:
        consumed_ranges.append("generation-2 holdout seeds `4000..4049`")
    if generation3_holdout_used:
        consumed_ranges.append("generation-3 holdout seeds `7000..7049`")
    if generation4_holdout_used:
        consumed_ranges.append("generation-4 holdout seeds `10000..10049`")
    if generation5_holdout_used:
        consumed_ranges.append("generation-5 holdout seeds `13000..13049`")
    if consumed_ranges:
        lines.append(
            "- " + ", ".join(consumed_ranges) + " have been evaluated once. This report can interpret those results, but policy tuning on any consumed range would invalidate the evidence."
        )
    else:
        lines.append("- Holdout seeds are not present in the ledger yet.")
    if generation4_holdout_used:
        lines.append(
            "- Generation-4 audit seeds `11000..11049` remain reserved; because generation-4 holdout is consumed, further policy research should predeclare a fresh generation instead of tuning from generation-4 final evidence."
        )
    if status != "available":
        lines.append("- Environment setup is unavailable, so performance claims should not be made.")
    if noncanonical:
        lines.append(
            f"- Noncanonical legacy change_type values are still present append-only: `{', '.join(noncanonical)}`."
        )
    return lines


def _scalar_search_lines(entries: list[dict[str, Any]], best_path: Path | None) -> list[str]:
    search_entries = [
        entry for entry in entries
        if entry.get("change_type") == "scalar/config tuning" and entry.get("pass_fail") == "pass"
    ]
    if not search_entries:
        return ["No SlimeVolley scalar-search baseline has been recorded yet."]
    lines = [f"Recorded scalar-search evaluation rows: {len(search_entries)}"]
    best_payload = _read_json(best_path) if best_path is not None else None
    if best_payload:
        lines.append(f"- Best config artifact: `{best_path}`")
        lines.append(f"- Selection score: `{_stats(best_payload.get('selection_score'))}`")
        lines.append(f"- Opponents: `{', '.join(best_payload.get('opponents', []))}`")
        lines.append(f"- Config: `{json.dumps(best_payload.get('config', {}), sort_keys=True)}`")
        means = best_payload.get("opponent_means", {})
        if means:
            rendered = ", ".join(f"{name}={_stats(value)}" for name, value in sorted(means.items()))
            lines.append(f"- Opponent means: `{rendered}`")
    else:
        lines.append("- Best config artifact has not been generated yet.")
    return lines


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _diagnostic_coverage_lines(entries: list[dict[str, Any]]) -> list[str]:
    passing_entries = [entry for entry in entries if entry.get("pass_fail") == "pass"]
    if not passing_entries:
        return ["No successful SlimeVolley rows exist yet, so diagnostic coverage cannot be summarized."]

    per_episode_rows = [
        entry for entry in passing_entries
        if isinstance(entry.get("per_episode"), list) and entry.get("per_episode")
    ]
    episodes = [
        episode
        for entry in per_episode_rows
        for episode in entry.get("per_episode", [])
        if isinstance(episode, dict)
    ]
    complete_episode_records = [
        episode for episode in episodes
        if {"seed", "score", "steps", "outcome", "action_counts"}.issubset(episode)
    ]
    point_events = [
        event
        for episode in episodes
        for event in episode.get("point_events", [])
        if isinstance(event, dict)
    ]
    traced_events = [event for event in point_events if event.get("pre_event_trace")]
    event_outcomes = Counter(str(event.get("outcome", "")) for event in point_events)
    action_frequency_rows = [entry for entry in passing_entries if entry.get("action_frequencies")]
    opponent_action_frequency_rows = [entry for entry in passing_entries if entry.get("opponent_action_frequencies")]
    opponent_metadata_rows = [
        entry for entry in passing_entries
        if entry.get("opponent_name") and entry.get("opponent_kind") and entry.get("opponent_version")
    ]

    return [
        f"- Passing rows with per-episode diagnostics: `{len(per_episode_rows)}/{len(passing_entries)}`.",
        f"- Per-episode records: `{len(episodes)}`; records with seed, score, steps, outcome, and action counts: `{len(complete_episode_records)}`.",
        "- Point events recorded: `{total}` total, `{won}` won, `{lost}` lost; events with compact pre-event traces: `{traced}`.".format(
            total=len(point_events),
            won=event_outcomes.get("point_won", 0),
            lost=event_outcomes.get("point_lost", 0),
            traced=len(traced_events),
        ),
        f"- Rows with agent action frequencies: `{len(action_frequency_rows)}/{len(passing_entries)}`; rows with opponent action frequencies: `{len(opponent_action_frequency_rows)}/{len(passing_entries)}`.",
        f"- Rows with explicit opponent name, kind, and version: `{len(opponent_metadata_rows)}/{len(passing_entries)}`.",
        "- Minimum logged fields covered: per-episode score, timesteps, life-loss/life-win point events, final outcome, opponent type/name, seed, policy version, and action frequencies.",
        "- Optional replay artifacts are compact JSON traces around selected point events rather than rendered video files.",
    ]


def _trace_diagnostic_lines(entries: list[dict[str, Any]]) -> list[str]:
    traced_entries = [
        entry for entry in entries
        if entry.get("policy_version") == "improved"
        and entry.get("opponent_name") == "builtin"
        and entry.get("pass_fail") == "pass"
        and entry.get("seed_range", {}).get("split") == "dev"
        and entry.get("config", {}).get("trace_window", 0)
    ]
    if not traced_entries:
        return ["No traced `improved` vs `builtin` development-seed diagnostic row has been recorded yet."]

    entry = traced_entries[-1]
    events = [
        event
        for episode in entry.get("per_episode", [])
        for event in episode.get("point_events", [])
        if event.get("outcome") == "point_lost" and event.get("pre_event_trace")
    ]
    if not events:
        return [f"Latest traced row `{entry.get('timestamp', '')}` contains no lost point traces."]

    event_actions = Counter(str(event.get("action")) for event in events)
    first_actions = Counter(str(event["pre_event_trace"][0].get("action")) for event in events)
    last_actions = Counter(str(event["pre_event_trace"][-1].get("action")) for event in events)
    start_dx: list[float] = []
    final_dx: list[float] = []
    abs_distance_delta: list[float] = []
    final_agent_y: list[float] = []
    final_ball_y: list[float] = []
    final_ball_vy: list[float] = []
    for event in events:
        trace = event["pre_event_trace"]
        first = trace[0].get("state", {})
        last = trace[-1].get("state", {})
        if {"agent_x", "ball_x"}.issubset(first) and {"agent_x", "ball_x"}.issubset(last):
            first_dx = float(first["ball_x"]) - float(first["agent_x"])
            last_dx = float(last["ball_x"]) - float(last["agent_x"])
            start_dx.append(first_dx)
            final_dx.append(last_dx)
            abs_distance_delta.append(abs(first_dx) - abs(last_dx))
        if {"agent_y", "ball_y", "ball_vy"}.issubset(last):
            final_agent_y.append(float(last["agent_y"]))
            final_ball_y.append(float(last["ball_y"]))
            final_ball_vy.append(float(last["ball_vy"]))

    lines = [
        f"- Latest traced row: `{entry.get('timestamp', '')}` with trace window `{entry.get('config', {}).get('trace_window')}`.",
        f"- Lost point traces: `{len(events)}`; score mean `{_stats(entry.get('score_stats', {}).get('mean'))}`.",
        "- Contact/return diagnostic artifacts: `results/contact_diagnostics_g3_dev.json` and `reports/contact_diagnostics_g3_dev.md` summarize inferred contact candidates from the same development traces.",
        f"- Scoring-step actions: `{dict(event_actions.most_common())}`.",
        f"- First trace-frame actions: `{dict(first_actions.most_common())}`; last trace-frame actions: `{dict(last_actions.most_common())}`.",
    ]
    if start_dx and final_dx:
        lines.append(
            f"- Mean ball-minus-agent x moved from `{_stats(_mean(start_dx))}` to `{_stats(_mean(final_dx))}`; "
            f"mean absolute x-distance improvement was `{_stats(_mean(abs_distance_delta))}`."
        )
    if final_agent_y and final_ball_y:
        lines.append(
            f"- Mean final traced agent y `{_stats(_mean(final_agent_y))}` versus ball y `{_stats(_mean(final_ball_y))}`, "
            f"with mean ball vy `{_stats(_mean(final_ball_vy))}`."
        )
    lines.append(
        "- Trace diagnosis: losses are usually not pure x-position misses; the agent is near the ball horizontally but remains above a fast-descending low ball. This motivated `grounded_low_receive`; paired evidence below shows jump suppression alone tied its predecessor, so the next structural hypothesis should move earlier into receive positioning or contact timing."
    )
    return lines


def _comparison_line(
    *,
    mode: str,
    candidate: str,
    predecessor: str,
    by_policy_opponent: dict[tuple[Any, Any], dict[str, Any]],
) -> list[str]:
    lines: list[str] = []
    candidate_builtin = by_policy_opponent.get((candidate, "builtin"))
    predecessor_builtin = by_policy_opponent.get((predecessor, "builtin"))
    if candidate_builtin is not None and predecessor_builtin is not None:
        candidate_mean = candidate_builtin.get("score_stats", {}).get("mean")
        predecessor_mean = predecessor_builtin.get("score_stats", {}).get("mean")
        if candidate_mean == predecessor_mean:
            lines.append(
                f"- `{mode}`: tied frozen `{predecessor}` against `builtin` "
                f"(both mean `{_stats(candidate_mean)}`), so it did not solve the built-in failure."
            )
        elif candidate_mean is not None and predecessor_mean is not None and candidate_mean < predecessor_mean:
            lines.append(
                f"- `{mode}`: regressed against `builtin` versus frozen `{predecessor}` "
                f"(`{_stats(candidate_mean)}` vs `{_stats(predecessor_mean)}`)."
            )
        elif candidate_mean is not None and predecessor_mean is not None:
            lines.append(
                f"- `{mode}`: improved against `builtin` versus frozen `{predecessor}` "
                f"(`{_stats(candidate_mean)}` vs `{_stats(predecessor_mean)}`)."
            )

    candidate_previous = by_policy_opponent.get((candidate, predecessor))
    previous_candidate = by_policy_opponent.get((predecessor, candidate))
    if candidate_previous is not None and previous_candidate is not None:
        candidate_mean = candidate_previous.get("score_stats", {}).get("mean")
        predecessor_mean = previous_candidate.get("score_stats", {}).get("mean")
        if candidate_mean == predecessor_mean:
            lines.append(
                f"- `{candidate}` and frozen `{predecessor}` tied each other in round-robin cross-play "
                f"(means `{_stats(candidate_mean)}` and `{_stats(predecessor_mean)}`)."
            )
    return lines


def _failed_or_partial_direction_lines(entries: list[dict[str, Any]]) -> list[str]:
    dev_entries = [
        entry for entry in entries
        if entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "dev"
    ]
    by_policy_opponent = {
        (entry.get("policy_version"), entry.get("opponent_name")): entry
        for entry in dev_entries
    }
    lines: list[str] = []
    lines.extend(
        _comparison_line(
            mode="late_low_ball_guard",
            candidate="improved-v2",
            predecessor="improved-v1",
            by_policy_opponent=by_policy_opponent,
        )
    )
    lines.extend(
        _comparison_line(
            mode="grounded_low_receive",
            candidate="improved",
            predecessor="improved-v2",
            by_policy_opponent=by_policy_opponent,
        )
    )

    if not lines:
        return ["No failed or partial structural direction has enough paired evidence yet."]
    return lines


def _holdout_lines(entries: list[dict[str, Any]], holdout_path: Path | None) -> list[str]:
    holdout_entries = [
        entry for entry in entries
        if entry.get("pass_fail") == "pass"
        and entry.get("seed_range", {}).get("split") == "holdout"
    ]
    if not holdout_entries:
        return ["No SlimeVolley holdout rows recorded yet; reserved seeds remain untouched."]

    lines = [
        "Holdout rows are final evidence and must not be used for further policy tuning.",
        f"- Recorded holdout rows: `{len(holdout_entries)}`",
    ]
    if holdout_path is not None and holdout_path.exists():
        payload = _read_json(holdout_path)
        if payload:
            lines.extend(
                [
                    f"- Artifact: `{holdout_path}`",
                    f"- Policies: `{', '.join(payload.get('policies', []))}`",
                    f"- Opponents: `{', '.join(payload.get('opponents', []))}`",
                    f"- Matchups: `{payload.get('matchup_count', '')}`",
                    f"- Episodes per matchup: `{payload.get('episodes_per_matchup', '')}`",
                ]
            )
    lines.extend(
        [
            "",
            "| Policy | Opponent | Episodes | Mean | Wins | Losses | Draws | Win rate | Steps |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for entry in sorted(holdout_entries, key=lambda item: (item.get("policy_version", ""), item.get("opponent_name", ""))):
        wld = entry.get("win_loss_draw", {})
        lines.append(
            "| {policy} | {opponent} | {episodes} | {mean} | {wins} | {losses} | {draws} | {win_rate} | {steps} |".format(
                policy=entry.get("policy_version", ""),
                opponent=entry.get("opponent_name", ""),
                episodes=entry.get("episodes", ""),
                mean=_stats(entry.get("score_stats", {}).get("mean")),
                wins=wld.get("wins", ""),
                losses=wld.get("losses", ""),
                draws=wld.get("draws", ""),
                win_rate=_stats(wld.get("win_rate")),
                steps=entry.get("environment_steps", ""),
            )
        )
    return lines


def _generation_2_evidence_lines(ledger_path: Path) -> list[str]:
    """Summarize the fresh generation-2 SlimeVolley artifacts beside the ledger."""

    results_dir = ledger_path.parent
    generation_ledger = results_dir / "generation_2_trials.jsonl"
    generation_summary = results_dir / "generation_2_summary.csv"
    search_best = results_dir / "search_best_g2_dev.json"
    tournament = results_dir / "round_robin_g2_dev.json"
    holdout = results_dir / "holdout_g2_final.json"

    if not generation_ledger.exists():
        return [
            "No generation-2 ledger is present beside this SlimeVolley ledger.",
            "If more policy work is planned after a consumed holdout, predeclare a fresh generation before tuning.",
        ]

    entries = read_entries(generation_ledger)
    split_counts = Counter(str(entry.get("seed_range", {}).get("split", "unknown")) for entry in entries)
    lines = [
        "Generation-2 evidence uses fresh predeclared seeds and a separate ledger from the original SlimeVolley run.",
        "Generation-2 holdout rows are final-only evidence and must not be used for further policy, scalar-config, or opponent-pool tuning.",
        f"- Generation-2 ledger: `{generation_ledger}`",
        f"- Generation-2 summary: `{generation_summary}`",
        f"- Generation-2 ledger rows: `{len(entries)}`",
        f"- Generation-2 split counts: `{dict(sorted(split_counts.items()))}`",
        f"- Generation-2 scalar-search artifact: `{search_best}`",
        f"- Generation-2 round-robin artifact: `{tournament}`",
    ]

    if not holdout.exists():
        lines.extend(
            [
                f"- Generation-2 holdout artifact: `{holdout}` is not present yet.",
                "Do not inspect generation-2 holdout seeds until the generation-2 policy, scalar config, opponent pool, and tests are frozen.",
            ]
        )
        return lines

    payload = _read_json(holdout)
    if not payload:
        lines.append(f"- Generation-2 holdout artifact `{holdout}` could not be read.")
        return lines

    lines.extend(
        [
            f"- Generation-2 holdout artifact: `{holdout}`",
            f"- Generation-2 holdout seeds: `{payload.get('seed_start', '')}..{int(payload.get('seed_start', 0)) + int(payload.get('episodes_per_matchup', 0)) - 1}`",
            f"- Matchups: `{payload.get('matchup_count', '')}`",
            f"- Episodes per matchup: `{payload.get('episodes_per_matchup', '')}`",
            f"- Policies: `{', '.join(payload.get('policies', []))}`",
            f"- Opponents: `{', '.join(payload.get('opponents', []))}`",
            "",
            "| Policy | Opponent | Episodes | Mean | Wins | Losses | Draws | Win rate | Steps |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    cells = payload.get("cells", [])
    if isinstance(cells, list):
        for cell in sorted(cells, key=lambda item: (str(item.get("policy", "")), str(item.get("opponent", "")))):
            lines.append(
                "| {policy} | {opponent} | {episodes} | {mean} | {wins} | {losses} | {draws} | {win_rate} | {steps} |".format(
                    policy=cell.get("policy", ""),
                    opponent=cell.get("opponent", ""),
                    episodes=cell.get("episodes", ""),
                    mean=_stats(cell.get("mean")),
                    wins=cell.get("wins", ""),
                    losses=cell.get("losses", ""),
                    draws=cell.get("draws", ""),
                    win_rate=_stats(cell.get("win_rate")),
                    steps=cell.get("environment_steps", ""),
                )
            )
    lines.extend(
        [
            "",
            "Generation-2 headline: the current structural heuristic improved over the initial and scalar-tuned heuristic on the non-built-in opponent pool, but it still failed to solve the built-in opponent and remained far behind `baseline-rnn`.",
            "Any additional SlimeVolley policy work now requires following the predeclared generation-4 protocol with development seeds `9000..9049`, sealed holdout seeds `10000..10049`, and reserved audit seeds `11000..11049`.",
        ]
    )
    return lines




def _generation_3_evidence_lines(ledger_path: Path) -> list[str]:
    """Summarize generation-3 development and final-only holdout evidence."""

    results_dir = ledger_path.parent
    generation_ledger = results_dir / "generation_3_trials.jsonl"
    generation_summary = results_dir / "generation_3_summary.csv"
    diagnosis = results_dir.parent / "reports" / "generation_3_diagnosis.md"
    protocol = results_dir.parent / "configs" / "generation_3_protocol.json"
    protocol_report = results_dir.parent / "reports" / "generation_3_protocol.md"
    holdout = results_dir / "holdout_g3_final.json"

    if not generation_ledger.exists():
        return [
            "No generation-3 ledger is present yet.",
            "Generation-3 is reserved for future SlimeVolley policy work after generation-2 holdout consumption.",
        ]

    entries = read_entries(generation_ledger)
    split_counts = Counter(str(entry.get("seed_range", {}).get("split", "unknown")) for entry in entries)
    status_counts = Counter(str(entry.get("pass_fail", "")) for entry in entries)
    holdout_present = holdout.exists()
    if holdout_present:
        status_line = "Generation-3 now includes final-only holdout evidence after the frozen policy/config/opponent/test state was evaluated. It must not be used for subsequent tuning."
    else:
        status_line = "Generation-3 is development-only evidence so far. It predeclares fresh seeds after the generation-2 holdout was consumed, but it has not opened generation-3 holdout."
    lines = [
        status_line,
        f"- Generation-3 protocol JSON: `{protocol}`",
        f"- Generation-3 protocol report: `{protocol_report}`",
        f"- Generation-3 diagnosis report: `{diagnosis}`",
        f"- Generation-3 ledger: `{generation_ledger}`",
        f"- Generation-3 summary: `{generation_summary}`",
        f"- Generation-3 ledger rows: `{len(entries)}`",
        f"- Generation-3 split counts: `{dict(sorted(split_counts.items()))}`",
        f"- Generation-3 pass/fail counts: `{dict(sorted(status_counts.items()))}`",
    ]
    if holdout.exists():
        lines.append(f"- Generation-3 holdout artifact: `{holdout}` is present and must be treated as final-only evidence.")
    else:
        lines.append(f"- Generation-3 holdout artifact: `{holdout}` is not present; holdout seeds `7000..7049` remain unopened.")

    latest_pass = next(
        (
            entry for entry in reversed(entries)
            if entry.get("pass_fail") == "pass"
            and entry.get("policy_version") == "improved"
            and entry.get("opponent_name") == "builtin"
            and entry.get("seed_range", {}).get("split") == "dev"
        ),
        None,
    )
    if latest_pass is not None:
        wld = latest_pass.get("win_loss_draw", {})
        seed_range = latest_pass.get("seed_range", {})
        start = seed_range.get("start")
        stop = seed_range.get("stop_exclusive")
        seed_label = f"{start}..{int(stop) - 1}" if isinstance(start, int) and isinstance(stop, int) else "unknown"
        lines.extend(
            [
                "",
                "Latest generation-3 development diagnostic:",
                "",
                "| Policy | Opponent | Seeds | Episodes | Mean | Wins | Losses | Draws | Steps |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
                "| {policy} | {opponent} | `{seeds}` | {episodes} | {mean} | {wins} | {losses} | {draws} | {steps} |".format(
                    policy=latest_pass.get("policy_version", ""),
                    opponent=latest_pass.get("opponent_name", ""),
                    seeds=seed_label,
                    episodes=latest_pass.get("episodes", ""),
                    mean=_stats(latest_pass.get("score_stats", {}).get("mean")),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                    steps=latest_pass.get("environment_steps", ""),
                ),
            ]
        )
    holdout_builtin = next(
        (
            entry for entry in reversed(entries)
            if entry.get("pass_fail") == "pass"
            and entry.get("policy_version") == "improved"
            and entry.get("opponent_name") == "builtin"
            and entry.get("seed_range", {}).get("split") == "holdout"
        ),
        None,
    )
    if holdout_builtin is not None:
        wld = holdout_builtin.get("win_loss_draw", {})
        seed_range = holdout_builtin.get("seed_range", {})
        start = seed_range.get("start")
        stop = seed_range.get("stop_exclusive")
        seed_label = f"{start}..{int(stop) - 1}" if isinstance(start, int) and isinstance(stop, int) else "unknown"
        lines.extend(
            [
                "",
                "Generation-3 final holdout built-in row:",
                "",
                "| Policy | Opponent | Seeds | Episodes | Mean | Wins | Losses | Draws | Steps |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
                "| {policy} | {opponent} | `{seeds}` | {episodes} | {mean} | {wins} | {losses} | {draws} | {steps} |".format(
                    policy=holdout_builtin.get("policy_version", ""),
                    opponent=holdout_builtin.get("opponent_name", ""),
                    seeds=seed_label,
                    episodes=holdout_builtin.get("episodes", ""),
                    mean=_stats(holdout_builtin.get("score_stats", {}).get("mean")),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                    steps=holdout_builtin.get("environment_steps", ""),
                ),
            ]
        )

    failed_entries = [entry for entry in entries if entry.get("pass_fail") != "pass"]
    if failed_entries:
        lines.extend(
            [
                "",
                "Generation-3 failed rows remain visible:",
            ]
        )
        for entry in failed_entries[-3:]:
            lines.append(
                f"- `{entry.get('timestamp', '')}` `{entry.get('policy_version', '')}` vs `{entry.get('opponent_name', '')}`: {entry.get('failure_analysis', '')}"
            )
    if holdout_present:
        lines.append(
            "Generation-3 holdout evidence confirms the built-in opponent gap remains and is final-only; further tuning requires fresh seeds."
        )
    else:
        lines.append(
            "Generation-3 development evidence confirms the built-in opponent gap remains; it should guide future diagnosis, not serve as final holdout evidence."
        )
    return lines


def _generation_4_development_lines(ledger_path: Path) -> list[str]:
    """Summarize generation-4 development and final-only holdout evidence."""

    results_dir = ledger_path.parent
    reports_dir = results_dir.parent / "reports"
    generation_ledger = results_dir / "generation_4_trials.jsonl"
    generation_summary = results_dir / "generation_4_summary.csv"
    protocol = results_dir.parent / "configs" / "generation_4_protocol.json"
    protocol_report = reports_dir / "generation_4_protocol.md"
    temporal_report = reports_dir / "generation_4_temporal_history_attempt.md"
    front_hit_note = results_dir.parent / "notes" / "generation_4_front_hit_suppression_attempt.md"
    rear_wall_note = results_dir.parent / "notes" / "generation_4_rear_wall_low_jump_attempt.md"
    front_net_note = results_dir.parent / "notes" / "generation_4_front_net_low_scoop_attempt.md"
    scalar_tuned_note = results_dir.parent / "notes" / "generation_4_scalar_tuned_structural_attempt.md"
    attack_note = results_dir.parent / "notes" / "generation_4_late_contact_attack_attempt.md"
    joint_attack_search_note = results_dir.parent / "notes" / "generation_4_joint_attack_scalar_search_attempt.md"
    low_receive_followup_note = results_dir.parent / "notes" / "generation_4_low_receive_teacher_scalar_followup.md"
    rally_serve_note = results_dir.parent / "notes" / "generation_4_rally_serve_candidate.md"
    parallel_scalar_note = results_dir.parent / "notes" / "parallel" / "20260527_scalar_rally_attack_worker.md"
    parallel_grounded_note = results_dir.parent / "notes" / "parallel" / "20260527_grounded_low_receive_stacked_worker.md"
    parallel_rear_wall_note = results_dir.parent / "notes" / "parallel" / "20260527_rear_wall_stacked_worker.md"
    parallel_robustness_note = results_dir.parent / "notes" / "parallel" / "20260527_robustness_rallyserve_worker.md"
    parallel_trace_report = reports_dir / "parallel" / "20260527_trace_rally_attack_rnn_worker.md"
    parallel_synthesis_report = reports_dir / "parallel" / "20260527_parallel_synthesis_rallyserve.md"
    parallel_g4_attack_scalar_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_attack_scalar_subagent.md"
    parallel_g4_grounded_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_grounded_low_receive_subagent.md"
    parallel_g4_rear_wall_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_rear_wall_press_subagent.md"
    parallel_g4_robustness_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_archived_robustness_subagent.md"
    parallel_g4_trace_report = reports_dir / "parallel" / "20260527_g4_trace_attack_vs_rnn_subagent.md"
    parallel_g4_synthesis_report = reports_dir / "parallel" / "20260527_g4_parallel_subagent_synthesis.md"
    parallel_g4_attack_scalar_v2_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_attack_scalar_subagent_v2.md"
    parallel_g4_worker_a_attack_scalar_note = results_dir.parent / "notes" / "parallel" / "g4_attack_scalar_worker_a_20260527.md"
    parallel_g4_grounded_v2_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_grounded_low_receive_subagent_v2.md"
    parallel_g4_worker_b_grounded_note = results_dir.parent / "notes" / "parallel" / "g4_grounded_low_receive_worker_b_screen.md"
    parallel_g4_rear_wall_v2_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_rear_wall_press_subagent_v2.md"
    parallel_g4_worker_c_rear_wall_note = results_dir.parent / "notes" / "parallel" / "g4_rear_wall_press_worker_c_20260527.md"
    parallel_g4_robustness_v2_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_archived_robustness_subagent_v2.md"
    parallel_g4_trace_v2_report = reports_dir / "parallel" / "20260527_g4_trace_attack_vs_rnn_subagent_v2.md"
    parallel_g4_worker_d_trace_report = reports_dir / "parallel" / "g4_trace_attack_vs_baseline_rnn_worker_d_20260527.md"
    parallel_g4_parallel4_synthesis_report = reports_dir / "parallel" / "20260527_g4_parallel4_synthesis.md"
    parallel_g4_parallel5_attack_scalar_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel5_attack_scalar.md"
    parallel_g4_parallel5_grounded_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel5_grounded_low_receive.md"
    parallel_g4_parallel5_grounded_result = results_dir / "generation_4_parallel5_grounded_low_receive_screen.json"
    parallel_g4_parallel5_rear_wall_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel5_rear_wall_press.md"
    parallel_g4_parallel5_rear_wall_result = results_dir / "generation_4_parallel5_rear_wall_press_probe.json"
    parallel_g4_parallel5_trace_report = reports_dir / "parallel" / "20260527_g4_parallel5_trace_attack_rnn.md"
    parallel_g4_parallel5_synthesis_report = reports_dir / "parallel" / "20260527_g4_parallel5_synthesis.md"
    parallel_g4_parallel6_attack_scalar_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel6_attack_scalar.md"
    parallel_g4_parallel6_grounded_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel6_grounded_low_receive.md"
    parallel_g4_parallel6_rear_wall_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel6_rear_wall_press.md"
    parallel_g4_parallel6_archived_robustness_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel6_archived_robustness.md"
    parallel_g4_parallel6_trace_report = reports_dir / "parallel" / "20260527_g4_parallel6_trace_attack_rnn.md"
    parallel_g4_parallel6_synthesis_report = reports_dir / "parallel" / "20260527_g4_parallel6_synthesis.md"
    parallel_g4_synthesis_v2_report = reports_dir / "parallel" / "20260527_g4_parallel_subagent_synthesis_v2.md"
    post_contact_candidate_note = results_dir.parent / "notes" / "generation_4_post_contact_front_conversion_attempt.md"
    post_contact_worker_e_note = results_dir.parent / "notes" / "parallel" / "g4_archived_opponent_robustness_post_contact_worker_e.md"
    post_contact_probe_script = results_dir.parent / "probes" / "g4_post_contact_gate_probe.py"
    post_contact_probe_result = results_dir / "generation_4_post_contact_gate_probe.json"
    stacked_low_receive_note = results_dir.parent / "notes" / "generation_4_stacked_low_receive_probe.md"
    stacked_low_receive_probe_script = results_dir.parent / "probes" / "g4_stacked_low_receive_probe.py"
    stacked_low_receive_probe_result = results_dir / "generation_4_stacked_low_receive_probe.json"
    parallel_g4_parallel3_attack_scalar_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel3_attack_scalar.md"
    parallel_g4_parallel3_grounded_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel3_grounded_low_receive.md"
    parallel_g4_parallel3_rear_wall_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel3_rear_wall_press.md"
    parallel_g4_parallel3_trace_report = reports_dir / "parallel" / "20260527_g4_parallel3_trace_attack_rnn.md"
    net_pressure_noledger_result = results_dir / "generation_4_net_pressure_noledger_probe.json"
    parallel_g4_net_pressure_fixed_pool_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_net_pressure_fixed_pool_noledger.md"
    parallel_g4_parallel3_archived_robustness_note = results_dir.parent / "notes" / "parallel" / "20260527_g4_parallel3_archived_robustness.md"
    holdout_artifact = results_dir / "holdout_g4_final.json"

    if not generation_ledger.exists():
        return [
            "No generation-4 development ledger is present yet.",
            "Generation-4 holdout seeds `10000..10049` and audit seeds `11000..11049` remain sealed.",
        ]

    entries = read_entries(generation_ledger)
    split_counts = Counter(str(entry.get("seed_range", {}).get("split", "unknown")) for entry in entries)
    status_counts = Counter(str(entry.get("pass_fail", "")) for entry in entries)
    holdout_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") == "holdout"]
    status_line = (
        "Generation-4 now includes final-only holdout evidence. It records temporal/planner candidates, kept structural edits through rear_wall_low_jump, a separate scalar/config-tuned improved-tuned baseline, the partial late-contact attack structural candidate, failed/partial scalar and structural probes, the rally-serve candidate, a post-contact front-conversion development candidate, and a final-only holdout comparison against `baseline-rnn`."
        if holdout_entries
        else "Generation-4 is currently development-only evidence. It records temporal/planner candidates, kept structural edits through rear_wall_low_jump, a separate scalar/config-tuned improved-tuned baseline, the partial late-contact attack structural candidate, a failed/partial joint scalar search around that attack rule, and the rolled-back front_net_low_scoop attempt without opening generation-4 holdout or audit seeds."
    )
    lines = [
        status_line,
        f"- Generation-4 protocol JSON: `{protocol}`",
        f"- Generation-4 protocol report: `{protocol_report}`",
        f"- Generation-4 temporal attempt report: `{temporal_report}`",
        f"- Generation-4 front-hit suppression note: `{front_hit_note}`",
        f"- Generation-4 rear-wall low-jump note: `{rear_wall_note}`",
        f"- Generation-4 front-net low-scoop rollback note: `{front_net_note}`",
        f"- Generation-4 scalar-tuned baseline note: `{scalar_tuned_note}`",
        f"- Generation-4 late-contact attack note: `{attack_note}`",
        f"- Generation-4 joint attack scalar-search note: `{joint_attack_search_note}`",
        f"- Generation-4 low-receive teacher/scalar follow-up note: `{low_receive_followup_note}`",
        f"- Generation-4 rally-serve candidate note: `{rally_serve_note}`",
        f"- Generation-4 parallel scalar rally/attack worker note: `{parallel_scalar_note}`",
        f"- Generation-4 parallel grounded-low-receive stacked worker note: `{parallel_grounded_note}`",
        f"- Generation-4 parallel rear-wall stacked worker note: `{parallel_rear_wall_note}`",
        f"- Generation-4 parallel rally-serve robustness worker note: `{parallel_robustness_note}`",
        f"- Generation-4 parallel rally/attack/RNN trace report: `{parallel_trace_report}`",
        f"- Generation-4 parallel rally-serve synthesis report: `{parallel_synthesis_report}`",
        f"- Generation-4 subagent attack scalar note: `{parallel_g4_attack_scalar_note}`",
        f"- Generation-4 subagent grounded-low-receive note: `{parallel_g4_grounded_note}`",
        f"- Generation-4 subagent rear-wall press note: `{parallel_g4_rear_wall_note}`",
        f"- Generation-4 subagent archived-opponent robustness note: `{parallel_g4_robustness_note}`",
        f"- Generation-4 subagent attack/RNN trace report: `{parallel_g4_trace_report}`",
        f"- Generation-4 subagent synthesis report: `{parallel_g4_synthesis_report}`",
        f"- Generation-4 subagent scalar/config v2 note: `{parallel_g4_attack_scalar_v2_note}`",
        f"- Generation-4 Worker A attack/net-pressure scalar note: `{parallel_g4_worker_a_attack_scalar_note}`",
        f"- Generation-4 subagent grounded-low-receive v2 note: `{parallel_g4_grounded_v2_note}`",
        f"- Generation-4 Worker B grounded-low-receive screen note: `{parallel_g4_worker_b_grounded_note}`",
        f"- Generation-4 subagent rear-wall press v2 note: `{parallel_g4_rear_wall_v2_note}`",
        f"- Generation-4 Worker C rear-wall press note: `{parallel_g4_worker_c_rear_wall_note}`",
        f"- Generation-4 subagent archived-opponent robustness v2 note: `{parallel_g4_robustness_v2_note}`",
        f"- Generation-4 subagent attack/rally-serve/RNN trace v2 report: `{parallel_g4_trace_v2_report}`",
        f"- Generation-4 Worker D attack/net-pressure/RNN trace report: `{parallel_g4_worker_d_trace_report}`",
        f"- Generation-4 parallel4 synthesis report: `{parallel_g4_parallel4_synthesis_report}`",
        f"- Generation-4 parallel6 scalar/config note: `{parallel_g4_parallel6_attack_scalar_note}`",
        f"- Generation-4 parallel6 grounded-low-receive note: `{parallel_g4_parallel6_grounded_note}`",
        f"- Generation-4 parallel6 rear-wall press note: `{parallel_g4_parallel6_rear_wall_note}`",
        f"- Generation-4 parallel6 archived-opponent robustness note: `{parallel_g4_parallel6_archived_robustness_note}`",
        f"- Generation-4 parallel6 attack/rally-serve/RNN trace report: `{parallel_g4_parallel6_trace_report}`",
        f"- Generation-4 parallel6 synthesis report: `{parallel_g4_parallel6_synthesis_report}`",
        f"- Generation-4 subagent synthesis v2 report: `{parallel_g4_synthesis_v2_report}`",
        f"- Generation-4 post-contact front-conversion candidate note: `{post_contact_candidate_note}`",
        f"- Generation-4 post-contact Worker E archived-opponent robustness note: `{post_contact_worker_e_note}`",
        f"- Generation-4 post-contact gate probe script: `{post_contact_probe_script}`",
        f"- Generation-4 post-contact gate probe results: `{post_contact_probe_result}`",
        f"- Generation-4 stacked low-receive probe note: `{stacked_low_receive_note}`",
        f"- Generation-4 stacked low-receive probe script: `{stacked_low_receive_probe_script}`",
        f"- Generation-4 stacked low-receive probe results: `{stacked_low_receive_probe_result}`",
        f"- Generation-4 parallel3 scalar/config note: `{parallel_g4_parallel3_attack_scalar_note}`",
        f"- Generation-4 parallel3 grounded-low-receive history note: `{parallel_g4_parallel3_grounded_note}`",
        f"- Generation-4 parallel3 rear-wall press note: `{parallel_g4_parallel3_rear_wall_note}`",
        f"- Generation-4 parallel3 attack/rally-serve/net-pressure/RNN trace report: `{parallel_g4_parallel3_trace_report}`",
        f"- Generation-4 net-pressure fixed-pool no-ledger results: `{net_pressure_noledger_result}`",
        f"- Generation-4 net-pressure fixed-pool no-ledger note: `{parallel_g4_net_pressure_fixed_pool_note}`",
        f"- Generation-4 parallel3 archived-opponent robustness note: `{parallel_g4_parallel3_archived_robustness_note}`",
        f"- Generation-4 ledger: `{generation_ledger}`",
        f"- Generation-4 summary: `{generation_summary}`",
        f"- Generation-4 final holdout artifact: `{holdout_artifact}`"
        + (" is present and is final-only evidence." if holdout_artifact.exists() else " is not present."),
        f"- Generation-4 ledger rows: `{len(entries)}`",
        f"- Generation-4 split counts: `{dict(sorted(split_counts.items()))}`",
        f"- Generation-4 pass/fail counts: `{dict(sorted(status_counts.items()))}`",
    ]
    if holdout_entries:
        lines.append("- Warning: generation-4 holdout rows are present. Treat them as final-only evidence and do not tune against them.")
        holdout_map = _latest_entry_map(holdout_entries, "holdout")
        holdout_pairs = [
            ("random", "builtin"),
            ("initial", "builtin"),
            ("improved", "builtin"),
            ("improved-tuned", "builtin"),
            ("attack", "builtin"),
            ("rally-serve", "builtin"),
            ("baseline-rnn", "builtin"),
            ("rally-serve", "improved-v5"),
            ("baseline-rnn", "improved-v5"),
            ("rally-serve", "improved-v6"),
            ("baseline-rnn", "improved-v6"),
        ]
        lines.extend(
            [
                "",
                "Generation-4 final-only holdout summary (`10000..10049`):",
                "",
                "| Policy | Opponent | Mean | W/L/D | Steps |",
                "| --- | --- | ---: | --- | ---: |",
            ]
        )
        for policy, opponent in holdout_pairs:
            entry = holdout_map.get((policy, opponent))
            if entry is None:
                continue
            wld = entry.get("win_loss_draw", {})
            lines.append(
                "| {policy} | {opponent} | {mean} | {wins}/{losses}/{draws} | {steps} |".format(
                    policy=policy,
                    opponent=opponent,
                    mean=_stats(_score_mean(entry)),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                    steps=entry.get("environment_steps", ""),
                )
            )
        rally_holdout = holdout_map.get(("rally-serve", "builtin"))
        rnn_holdout = holdout_map.get(("baseline-rnn", "builtin"))
        if rally_holdout is not None and rnn_holdout is not None:
            rally_mean = _score_mean(rally_holdout)
            rnn_mean = _score_mean(rnn_holdout)
            delta = None if rally_mean is None or rnn_mean is None else rally_mean - rnn_mean
            lines.append(
                f"- Final-only built-in holdout result: `rally-serve` mean `{_stats(rally_mean)}` versus `baseline-rnn` mean `{_stats(rnn_mean)}`; holdout delta `{_stats(delta)}`."
            )
        for archived in ("improved-v5", "improved-v6"):
            rally_archived = holdout_map.get(("rally-serve", archived))
            rnn_archived = holdout_map.get(("baseline-rnn", archived))
            if rally_archived is None or rnn_archived is None:
                continue
            rally_mean = _score_mean(rally_archived)
            rnn_mean = _score_mean(rnn_archived)
            delta = None if rally_mean is None or rnn_mean is None else rally_mean - rnn_mean
            lines.append(
                f"- Final-only archived-opponent result versus `{archived}`: `rally-serve` mean `{_stats(rally_mean)}` versus `baseline-rnn` mean `{_stats(rnn_mean)}`; delta `{_stats(delta)}`."
            )
        lines.append(
            "- Generation-4 holdout conclusion: `rally-serve` did not beat `baseline-rnn` on sealed built-in holdout; no generation-4 heuristic policy is promoted from this final evidence."
        )
    else:
        lines.append("- Generation-4 holdout rows are absent; holdout seeds `10000..10049` remain sealed.")

    latest_full: dict[tuple[Any, Any], dict[str, Any]] = {}
    for entry in entries:
        seed_range = entry.get("seed_range", {})
        if (
            entry.get("pass_fail") == "pass"
            and seed_range.get("split") == "dev"
            and seed_range.get("start") == 9000
            and entry.get("episodes") == 50
            and entry.get("policy_version") in {"improved", "improved-tuned", "attack", "rally-serve", "temporal", "baseline-rnn"}
        ):
            latest_full[(entry.get("policy_version"), entry.get("opponent_name"))] = entry

    opponents = ["builtin", "random", "initial", "improved-v0", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6"]
    if latest_full:
        lines.extend(
            [
                "",
                "Latest 50-seed development comparison (`9000..9049`):",
                "",
                "| Opponent | Improved mean | Temporal mean | Delta | Improved W/L/D | Temporal W/L/D |",
                "| --- | ---: | ---: | ---: | --- | --- |",
            ]
        )
        temporal_better = 0
        temporal_worse = 0
        temporal_tied = 0
        for opponent in opponents:
            improved = latest_full.get(("improved", opponent))
            temporal = latest_full.get(("temporal", opponent))
            if improved is None or temporal is None:
                continue
            improved_mean = _score_mean(improved)
            temporal_mean = _score_mean(temporal)
            if improved_mean is None or temporal_mean is None:
                continue
            delta = temporal_mean - improved_mean
            if delta > 0:
                temporal_better += 1
            elif delta < 0:
                temporal_worse += 1
            else:
                temporal_tied += 1
            iw = improved.get("win_loss_draw", {})
            tw = temporal.get("win_loss_draw", {})
            lines.append(
                "| {opponent} | {improved_mean} | {temporal_mean} | {delta} | {iwins}/{ilosses}/{idraws} | {twins}/{tlosses}/{tdraws} |".format(
                    opponent=opponent,
                    improved_mean=_stats(improved_mean),
                    temporal_mean=_stats(temporal_mean),
                    delta=f"{delta:+.6g}",
                    iwins=iw.get("wins", ""),
                    ilosses=iw.get("losses", ""),
                    idraws=iw.get("draws", ""),
                    twins=tw.get("wins", ""),
                    tlosses=tw.get("losses", ""),
                    tdraws=tw.get("draws", ""),
                )
            )
        lines.extend(
            [
                "",
                f"Temporal score deltas across paired development opponents: `{temporal_better}` better, `{temporal_worse}` worse, `{temporal_tied}` tied.",
                "Decision: keep `temporal` as an auditable generation-4 candidate and opponent, but do not promote it over `improved` because the full development evidence is mixed and built-in performance is slightly worse.",
            ]
        )
    else:
        lines.append("No paired 50-seed `improved` versus `temporal` development comparison is present yet.")

    tuned_rows = [
        (opponent, latest_full.get(("improved", opponent)), latest_full.get(("improved-tuned", opponent)))
        for opponent in opponents
        if latest_full.get(("improved", opponent)) is not None and latest_full.get(("improved-tuned", opponent)) is not None
    ]
    if tuned_rows:
        lines.extend([
            "",
            "Latest scalar/config tuned baseline versus current `improved` (`9000..9049`):",
            "",
            "| Opponent | Improved mean | Improved-tuned mean | Delta | Improved W/L/D | Tuned W/L/D |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ])
        tuned_better = 0
        tuned_worse = 0
        tuned_tied = 0
        for opponent, improved, tuned in tuned_rows:
            if improved is None or tuned is None:
                continue
            improved_mean = _score_mean(improved)
            tuned_mean = _score_mean(tuned)
            if improved_mean is None or tuned_mean is None:
                continue
            delta = tuned_mean - improved_mean
            if delta > 0:
                tuned_better += 1
            elif delta < 0:
                tuned_worse += 1
            else:
                tuned_tied += 1
            iw = improved.get("win_loss_draw", {})
            tw = tuned.get("win_loss_draw", {})
            lines.append(
                "| {opponent} | {improved_mean} | {tuned_mean} | {delta} | {iwins}/{ilosses}/{idraws} | {twins}/{tlosses}/{tdraws} |".format(
                    opponent=opponent,
                    improved_mean=_stats(improved_mean),
                    tuned_mean=_stats(tuned_mean),
                    delta=f"{delta:+.6g}",
                    iwins=iw.get("wins", ""),
                    ilosses=iw.get("losses", ""),
                    idraws=iw.get("draws", ""),
                    twins=tw.get("wins", ""),
                    tlosses=tw.get("losses", ""),
                    tdraws=tw.get("draws", ""),
                )
            )
        lines.extend([
            "",
            f"Scalar-tuned deltas across paired development opponents: `{tuned_better}` better, `{tuned_worse}` worse, `{tuned_tied}` tied.",
            "Decision: keep `improved-tuned` as a scalar/config baseline only. It is not counted as a structural policy improvement and future structural edits must beat it before holdout.",
        ])

    attack_rows = [
        (opponent, latest_full.get(("improved-tuned", opponent)), latest_full.get(("attack", opponent)))
        for opponent in opponents
        if latest_full.get(("improved-tuned", opponent)) is not None and latest_full.get(("attack", opponent)) is not None
    ]
    if attack_rows:
        lines.extend([
            "",
            "Latest structural attack candidate versus scalar/config baseline (`9000..9049`):",
            "",
            "| Opponent | Improved-tuned mean | Attack mean | Delta | Tuned W/L/D | Attack W/L/D |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ])
        attack_better = 0
        attack_worse = 0
        attack_tied = 0
        for opponent, tuned, attack in attack_rows:
            if tuned is None or attack is None:
                continue
            tuned_mean = _score_mean(tuned)
            attack_mean = _score_mean(attack)
            if tuned_mean is None or attack_mean is None:
                continue
            delta = attack_mean - tuned_mean
            if delta > 0:
                attack_better += 1
            elif delta < 0:
                attack_worse += 1
            else:
                attack_tied += 1
            tw = tuned.get("win_loss_draw", {})
            aw = attack.get("win_loss_draw", {})
            lines.append(
                "| {opponent} | {tuned_mean} | {attack_mean} | {delta} | {twins}/{tlosses}/{tdraws} | {awins}/{alosses}/{adraws} |".format(
                    opponent=opponent,
                    tuned_mean=_stats(tuned_mean),
                    attack_mean=_stats(attack_mean),
                    delta=f"{delta:+.6g}",
                    twins=tw.get("wins", ""),
                    tlosses=tw.get("losses", ""),
                    tdraws=tw.get("draws", ""),
                    awins=aw.get("wins", ""),
                    alosses=aw.get("losses", ""),
                    adraws=aw.get("draws", ""),
                )
            )
        lines.extend([
            "",
            f"Attack candidate deltas across paired development opponents: `{attack_better}` better, `{attack_worse}` worse, `{attack_tied}` tied.",
            "Decision: keep `attack` as a partial structural candidate only. It is not promoted over `improved-tuned` because it remains below `baseline-rnn` on built-in development seeds and regresses nearest archived opponents.",
            "",
            "Joint attack scalar search (`9000..9049`, development only): a follow-up threshold/gain search found a built-in-specific candidate at mean `-0.10` with W/L/D `11/13/26`, narrowing the same-seed `baseline-rnn` gap to `0.22`, but the no-ledger opponent-pool check was worse or tied against every non-built-in opponent. It is documented as a failed/partial scalar search and is not promoted.",
            "",
            "Low-receive teacher/scalar follow-up (`9000..9049`, development only): a teacher-action diagnostic found many low own-side and near-net loss windows where the RNN would jump, but targeted `LowDriveFinish` and `NetVerticalBlock` structural probes tied or worsened the fixed short screen. A bounded 98-config scalar follow-up again topped out at mean `-0.02`, W/L/D `9/12/29`, leaving a `0.14` built-in gap to `baseline-rnn`; no candidate was promoted.",
        ])

    rally_serve_rows = [
        (opponent, latest_full.get(("rally-serve", opponent)))
        for opponent in opponents
        if latest_full.get(("rally-serve", opponent)) is not None
    ]
    if rally_serve_rows:
        lines.extend([
            "",
            "Latest rally-serve candidate development matrix (`9000..9049`):",
            "",
            "| Opponent | Rally-serve mean | W/L/D | Steps |",
            "| --- | ---: | --- | ---: |",
        ])
        for opponent, entry in rally_serve_rows:
            if entry is None:
                continue
            wld = entry.get("win_loss_draw", {})
            lines.append(
                "| {opponent} | {mean} | {wins}/{losses}/{draws} | {steps} |".format(
                    opponent=opponent,
                    mean=_stats(_score_mean(entry)),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                    steps=entry.get("environment_steps", ""),
                )
            )
        rally_builtin = latest_full.get(("rally-serve", "builtin"))
        baseline = latest_full.get(("baseline-rnn", "builtin"))
        tuned_v5 = latest_full.get(("improved-tuned", "improved-v5"))
        rally_v5 = latest_full.get(("rally-serve", "improved-v5"))
        if rally_builtin is not None and baseline is not None:
            rally_mean = _score_mean(rally_builtin)
            baseline_mean = _score_mean(baseline)
            delta = None if rally_mean is None or baseline_mean is None else rally_mean - baseline_mean
            lines.append(
                f"- Same-seed built-in comparator result: `rally-serve` mean `{_stats(rally_mean)}` versus `baseline-rnn` mean `{_stats(baseline_mean)}`; development delta `{_stats(delta)}`."
            )
        if tuned_v5 is not None and rally_v5 is not None:
            tuned_mean = _score_mean(tuned_v5)
            rally_mean = _score_mean(rally_v5)
            delta = None if rally_mean is None or tuned_mean is None else rally_mean - tuned_mean
            lines.append(
                f"- Recorded archive-pool caveat: `rally-serve` versus `improved-v5` mean `{_stats(rally_mean)}` compared with `improved-tuned` versus `improved-v5` mean `{_stats(tuned_mean)}`; delta `{_stats(delta)}`."
            )
        if holdout_entries:
            lines.append(
                "Final-only holdout decision: `rally-serve` remains an archived structural-plus-scalar candidate, but it is not promoted because it failed to beat `baseline-rnn` on generation-4 built-in holdout."
            )
        else:
            lines.append(
                "Decision: freeze `rally-serve` as the current generation-4 development candidate. It beats the packaged RNN on built-in development seeds, but holdout and audit remain sealed, so this is not final generalization evidence."
            )
        lines.extend(
            [
                "",
                "Latest parallel rally-serve development pass (`9000..9049`, no holdout/audit):",
                "- Scalar/config search around `rally-serve` screened 53 candidates on `9000..9015` and full-checked the reference plus top candidates on `9000..9049`; no candidate beat the current `0.14` built-in mean, and tied variants added losses.",
                "- Stacked-history `grounded_low_receive` probes tied the current built-in result at best; the branch remained sparse and outcome-neutral.",
                "- Stacked rear-wall probes tied or regressed; broad post-bounce/hold modes were harmful, and exact `rear_wall_low_jump` action swaps were neutral.",
                "- Trace diagnostics show `rally-serve` cuts `attack` point losses from `32` to `18`, but it still wins fewer built-in matches than `baseline-rnn` (`13` versus `18`) and relies more on draws (`29` versus `20`).",
                "- Pre-holdout robustness evidence supported freezing `rally-serve`, with the recorded caveat that it regressed versus `improved-tuned` on `improved-v5` by `-0.06` mean.",
                "- Decision from the parallel pass: no new policy/config/test promotion; keep `rally-serve` frozen and do not tune on holdout or audit seeds.",
                "- Minimum known new development-only cost from that pass: `6,540,000` environment steps, excluding unreported LLM token cost.",
            ]
        )
        if holdout_entries:
            lines.append(
                "- Final-only holdout now supersedes the pre-holdout freeze recommendation: `rally-serve` failed to beat `baseline-rnn` on built-in holdout, so no generation-4 policy is promoted."
            )
        if stacked_low_receive_note.exists():
            lines.append(
                "- Additional stacked low-receive probe: `stacked_low_101_wide` improved `improved-v5/v6` by `+0.04` on full generation-4 development seeds, but regressed built-in from `0.14` to `0.04` and fell below `baseline-rnn` (`0.12`), so no policy edit was promoted."
            )
        if parallel_g4_parallel5_synthesis_report.exists():
            lines.append(
                "- Additional parallel5 diagnostics on generation-4 development seeds: scalar/config tuning improved `attack` to `-0.06` built-in full-dev mean but stayed below `baseline-rnn` and `rally-serve`; grounded-low-receive variants tied at best, the rear-wall low-close jump tied built-in while regressing `improved-v5/v6`, and the trace pass again pointed to low own-side/rear-wall recovery as the gap. No maintained edit was promoted."
            )
        if (
            parallel_g4_parallel6_attack_scalar_note.exists()
            or parallel_g4_parallel6_grounded_note.exists()
            or parallel_g4_parallel6_rear_wall_note.exists()
            or parallel_g4_parallel6_archived_robustness_note.exists()
            or parallel_g4_parallel6_trace_report.exists()
            or parallel_g4_parallel6_synthesis_report.exists()
        ):
            lines.append(
                "- Additional parallel6 diagnostics on generation-4 development seeds: scalar/config tuning found `low_x_0.52` as a fixed-pool-checked `rally-serve` variant with built-in mean `0.18`; it is now exposed as `rally-serve-low-x52` for auditability, but it is scalar/config evidence rather than structural progress. Grounded-low-receive history probes tied the fixed pool without closing the hard-opponent RNN gap; rear-wall press probes repeated the small built-in-gain plus archived-regression pattern; the robustness note kept the fixed-pool gap to `baseline-rnn` explicit, and trace diagnostics again showed `rally-serve` improving `attack` mostly through loss-to-draw conversion. No holdout or audit seeds were opened."
            )

    improved_rows = [
        (opponent, latest_full.get(("improved", opponent)))
        for opponent in opponents
        if latest_full.get(("improved", opponent)) is not None
    ]
    if improved_rows:
        lines.extend([
            "",
            "Latest current `improved` development matrix after rear_wall_low_jump:",
            "",
            "| Opponent | Mean | W/L/D | Steps |",
            "| --- | ---: | --- | ---: |",
        ])
        for opponent, entry in improved_rows:
            if entry is None:
                continue
            wld = entry.get("win_loss_draw", {})
            lines.append(
                "| {opponent} | {mean} | {wins}/{losses}/{draws} | {steps} |".format(
                    opponent=opponent,
                    mean=_stats(_score_mean(entry)),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                    steps=entry.get("environment_steps", ""),
                )
            )
        previous = latest_full.get(("improved", "improved-v4"))
        builtin = latest_full.get(("improved", "builtin"))
        tuned_builtin = latest_full.get(("improved-tuned", "builtin"))
        baseline = latest_full.get(("baseline-rnn", "builtin"))
        if builtin is not None and baseline is not None:
            baseline_mean = _score_mean(baseline)
            builtin_mean = _score_mean(builtin)
            gap = None if baseline_mean is None or builtin_mean is None else baseline_mean - builtin_mean
            lines.append(
                f"- Same-seed built-in neural gap after rear_wall_low_jump: `baseline-rnn` mean `{_stats(baseline_mean)}` versus `improved` mean `{_stats(builtin_mean)}`; remaining gap `{_stats(gap)}`."
            )
            if tuned_builtin is not None:
                tuned_mean = _score_mean(tuned_builtin)
                tuned_gap = None if baseline_mean is None or tuned_mean is None else baseline_mean - tuned_mean
                lines.append(
                    f"- Same-seed scalar-tuned built-in gap: `baseline-rnn` mean `{_stats(baseline_mean)}` versus `improved-tuned` mean `{_stats(tuned_mean)}`; remaining gap `{_stats(tuned_gap)}`."
                )
        if previous is not None:
            lines.append(
                f"- Archive regression check: current `improved` versus frozen `improved-v4` mean `{_stats(_score_mean(previous))}` on development seeds; this preserves the pre-edit policy as an opponent."
            )


    latest_candidates: dict[str, dict[str, Any]] = {}
    for entry in entries:
        seed_range = entry.get("seed_range", {})
        if (
            entry.get("pass_fail") == "pass"
            and seed_range.get("split") == "dev"
            and seed_range.get("start") == 9000
            and entry.get("episodes") == 50
            and entry.get("opponent_name") == "builtin"
            and entry.get("policy_version") in {"planner", "teacher-assisted"}
        ):
            latest_candidates[str(entry.get("policy_version"))] = entry
    if latest_candidates:
        lines.extend(
            [
                "",
                "Planner and teacher-assisted built-in development checks (`9000..9049`):",
                "",
                "| Policy | Mean | W/L/D | Steps | Decision |",
                "| --- | ---: | --- | ---: | --- |",
            ]
        )
        improved_builtin = latest_full.get(("improved", "builtin"))
        improved_mean = _score_mean(improved_builtin) if improved_builtin is not None else None
        for policy in ["planner", "teacher-assisted"]:
            entry = latest_candidates.get(policy)
            if entry is None:
                continue
            mean = _score_mean(entry)
            wld = entry.get("win_loss_draw", {})
            if improved_mean is not None and mean is not None and mean < improved_mean:
                decision = "do not promote; below paired improved baseline"
            else:
                decision = "requires full opponent-pool comparison before promotion"
            lines.append(
                "| {policy} | {mean} | {wins}/{losses}/{draws} | {steps} | {decision} |".format(
                    policy=policy,
                    mean=_stats(mean),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                    steps=entry.get("environment_steps", ""),
                    decision=decision,
                )
            )
    return lines



def _generation_5_development_lines(ledger_path: Path) -> list[str]:
    """Summarize generation-5 post-holdout development-only evidence."""

    results_dir = ledger_path.parent
    reports_dir = results_dir.parent / "reports"
    generation_ledger = results_dir / "generation_5_trials.jsonl"
    generation_summary = results_dir / "generation_5_summary.csv"
    protocol = results_dir.parent / "configs" / "generation_5_protocol.json"
    protocol_report = reports_dir / "generation_5_protocol.md"
    net_pressure_note = results_dir.parent / "notes" / "generation_5_net_pressure_attempt.md"
    fixed_pool_note = results_dir.parent / "notes" / "generation_5_fixed_pool_comparator.md"
    hard_opponent_note = results_dir.parent / "notes" / "generation_5_hard_opponent_trace_and_probe.md"
    post_contact_note = results_dir.parent / "notes" / "generation_5_post_contact_comparison.md"
    aggressive_pressure_note = results_dir.parent / "notes" / "generation_5_aggressive_pressure_and_brace_probe.md"
    stacked_followthrough_note = results_dir.parent / "notes" / "generation_5_stacked_followthrough_and_posture_probe.md"
    phase_pressure_note = results_dir.parent / "notes" / "generation_5_phase_pressure_probe.md"
    teacher_serve_note = results_dir.parent / "notes" / "generation_5_teacher_serve_probe.md"
    teacher_serve_probe_script = results_dir.parent / "probes" / "g5_teacher_serve_probe.py"
    teacher_serve_probe_result = results_dir / "generation_5_teacher_serve_probe.json"
    context_reset_note = results_dir.parent / "notes" / "generation_5_context_reset_probe.md"
    context_reset_probe_script = results_dir.parent / "probes" / "g5_context_reset_probe.py"
    context_reset_probe_result = results_dir / "generation_5_context_reset_probe.json"
    rally_setup_note = results_dir.parent / "notes" / "generation_5_rally_setup_probe.md"
    rally_setup_probe_script = results_dir.parent / "probes" / "g5_rally_setup_probe.py"
    rally_setup_probe_result = results_dir / "generation_5_rally_setup_probe.json"
    contact_timing_note = results_dir.parent / "notes" / "generation_5_contact_timing_probe.md"
    contact_timing_probe_script = results_dir.parent / "probes" / "g5_contact_timing_probe.py"
    contact_timing_probe_result = results_dir / "generation_5_contact_timing_probe.json"
    approach_quality_note = results_dir.parent / "notes" / "generation_5_approach_quality_probe.md"
    approach_quality_probe_script = results_dir.parent / "probes" / "g5_approach_quality_probe.py"
    approach_quality_probe_result = results_dir / "generation_5_approach_quality_probe.json"
    contact_quality_note = results_dir.parent / "notes" / "generation_5_contact_quality_probe.md"
    contact_quality_probe_script = results_dir.parent / "probes" / "g5_contact_quality_probe.py"
    contact_quality_probe_result = results_dir / "generation_5_contact_quality_probe.json"
    position_posture_note = results_dir.parent / "notes" / "generation_5_position_posture_probe.md"
    position_posture_probe_script = results_dir.parent / "probes" / "g5_position_posture_probe.py"
    position_posture_probe_result = results_dir / "generation_5_position_posture_probe.json"
    planner_takeover_note = results_dir.parent / "notes" / "generation_5_planner_takeover_probe.md"
    planner_takeover_probe_script = results_dir.parent / "probes" / "g5_planner_takeover_probe.py"
    planner_takeover_probe_result = results_dir / "generation_5_planner_takeover_probe.json"
    holdout_artifact = results_dir / "holdout_g5_final.json"

    if not generation_ledger.exists():
        return [
            f"Generation-5 protocol JSON: `{protocol}`",
            f"Generation-5 protocol report: `{protocol_report}`",
            "No generation-5 development ledger is present yet.",
            "Generation-5 holdout seeds `13000..13049` and audit seeds `14000..14049` remain sealed.",
        ]

    entries = read_entries(generation_ledger)
    split_counts = Counter(str(entry.get("seed_range", {}).get("split", "unknown")) for entry in entries)
    status_counts = Counter(str(entry.get("pass_fail", "")) for entry in entries)
    holdout_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") == "holdout"]
    lines = [
        "Generation-5 is fresh post-generation-4 development evidence only. It predeclares new development, holdout, and audit seeds after the generation-4 holdout failure and starts with the `net-pressure` structural probe.",
        f"- Generation-5 protocol JSON: `{protocol}`",
        f"- Generation-5 protocol report: `{protocol_report}`",
        f"- Generation-5 net-pressure note: `{net_pressure_note}`",
        f"- Generation-5 fixed-pool comparator note: `{fixed_pool_note}`",
        f"- Generation-5 hard-opponent trace/probe note: `{hard_opponent_note}`",
        f"- Generation-5 post-contact comparison note: `{post_contact_note}`",
        f"- Generation-5 aggressive pressure and brace probe note: `{aggressive_pressure_note}`",
        f"- Generation-5 stacked followthrough and posture probe note: `{stacked_followthrough_note}`",
        f"- Generation-5 phase-pressure probe note: `{phase_pressure_note}`",
        f"- Generation-5 teacher-serve probe note: `{teacher_serve_note}`",
        f"- Generation-5 context-reset probe note: `{context_reset_note}`",
        f"- Generation-5 rally-setup probe note: `{rally_setup_note}`",
        f"- Generation-5 contact-timing probe note: `{contact_timing_note}`",
        f"- Generation-5 approach-quality probe note: `{approach_quality_note}`",
        f"- Generation-5 contact-quality probe note: `{contact_quality_note}`",
        f"- Generation-5 position/posture probe note: `{position_posture_note}`",
        f"- Generation-5 planner-takeover probe note: `{planner_takeover_note}`",
        f"- Generation-5 ledger: `{generation_ledger}`",
        f"- Generation-5 summary: `{generation_summary}`",
        f"- Generation-5 final holdout artifact: `{holdout_artifact}`" + (" is present and is final-only evidence." if holdout_artifact.exists() else " is not present."),
        f"- Generation-5 ledger rows: `{len(entries)}`",
        f"- Generation-5 split counts: `{dict(sorted(split_counts.items()))}`",
        f"- Generation-5 pass/fail counts: `{dict(sorted(status_counts.items()))}`",
    ]
    if holdout_entries:
        lines.append("- Warning: generation-5 holdout rows are present. Treat them as final-only evidence and do not tune against them.")
    else:
        lines.append("- Generation-5 holdout rows are absent; holdout seeds `13000..13049` remain sealed, and audit seeds `14000..14049` remain unused.")

    latest_dev = _latest_entry_map(entries, "dev")
    builtin_policies = ["improved-tuned", "attack", "rally-serve", "post-contact", "baseline-rnn", "net-pressure"]
    lines.extend([
        "",
        "Generation-5 built-in development comparison (`12000..12049` unless noted):",
        "",
        "| Policy | Episodes | Mean | W/L/D | Steps |",
        "| --- | ---: | ---: | --- | ---: |",
    ])
    for policy in builtin_policies:
        entry = latest_dev.get((policy, "builtin"))
        if entry is None:
            continue
        wld = entry.get("win_loss_draw", {})
        lines.append(
            "| {policy} | {episodes} | {mean} | {wins}/{losses}/{draws} | {steps} |".format(
                policy=policy,
                episodes=entry.get("episodes", ""),
                mean=_stats(_score_mean(entry)),
                wins=wld.get("wins", ""),
                losses=wld.get("losses", ""),
                draws=wld.get("draws", ""),
                steps=entry.get("environment_steps", ""),
            )
        )
    net_pressure = latest_dev.get(("net-pressure", "builtin"))
    baseline = latest_dev.get(("baseline-rnn", "builtin"))
    rally = latest_dev.get(("rally-serve", "builtin"))
    if net_pressure is not None and baseline is not None:
        net_mean = _score_mean(net_pressure)
        baseline_mean = _score_mean(baseline)
        delta = None if net_mean is None or baseline_mean is None else net_mean - baseline_mean
        lines.append(
            f"- Built-in development comparator result: `net-pressure` mean `{_stats(net_mean)}` versus `baseline-rnn` mean `{_stats(baseline_mean)}`; development delta `{_stats(delta)}`."
        )
    if net_pressure is not None and rally is not None:
        net_mean = _score_mean(net_pressure)
        rally_mean = _score_mean(rally)
        delta = None if net_mean is None or rally_mean is None else net_mean - rally_mean
        lines.append(
            f"- Built-in development heuristic delta: `net-pressure` mean `{_stats(net_mean)}` versus `rally-serve` mean `{_stats(rally_mean)}`; development delta `{_stats(delta)}`."
        )

    if teacher_serve_note.exists():
        lines.append(
            "- Additional teacher-serve macro probe on generation-5 development seeds: `serve_110_10` improved several hard archived short-screen rows, but the full `12000..12049` fixed-pool check regressed built-in from `-0.06` to `-0.12`, regressed `improved-v2/v3`, and remained far below `baseline-rnn` on hard archived opponents. No maintained edit was promoted and holdout/audit stayed sealed."
        )

    if context_reset_note.exists():
        lines.append(
            "- Additional context-reset macro probe on generation-5 development seeds: after fixing an initially inert single-frame context detector, `ctx_any_low_110_10` reached the best built-in development mean so far (`-0.02`) but regressed most fixed-pool archived opponents versus `net-pressure` and remained far below `baseline-rnn` on hard rows. No maintained edit was promoted and holdout/audit stayed sealed."
        )

    if rally_setup_note.exists():
        lines.append(
            "- Additional rally-setup structural/history probe on generation-5 development seeds: post-own-contact front-anchor phases fired on the fixed short screen, but preserved only the built-in row, regressed `improved-v3/v4`, left `improved-v5/v6` unchanged, and remained far below `baseline-rnn`. No maintained edit was promoted and holdout/audit stayed sealed."
        )

    if contact_timing_note.exists():
        lines.append(
            "- Additional contact-timing diagnostic/probe on generation-5 development seeds: low front-court traces showed `net-pressure` already jumps on most terminal low-contact frames, while narrow `001`/back-jump/base-jump overrides fired only four frames and tied the reference table. No maintained edit was promoted and holdout/audit stayed sealed."
        )

    if approach_quality_note.exists():
        lines.append(
            "- Additional approach-quality diagnostic/probe on generation-5 development seeds: eight-frame pre-contact traces showed `net-pressure` farther behind the ball than `baseline-rnn`, but early-jump copies collapsed performance, broad no-jump approach rules were mixed or harmful, and a far-behind follow-up only nudged `improved-v5/v6` while regressing built-in and `improved-v3/v4`. No maintained edit was promoted and holdout/audit stayed sealed."
        )

    if contact_quality_note.exists():
        lines.append(
            "- Additional contact-quality structural/history probe on generation-5 development seeds: recent-contact gates and `110`/`111` brace substitutions were active, but hard-tail nudges came with built-in or `improved-v3/v4` regressions and remained far below `baseline-rnn`. No full-pool expansion, maintained edit, holdout, or audit run was promoted."
        )

    if position_posture_note.exists():
        lines.append(
            "- Additional position/posture scalar-config probe on generation-5 development seeds: front-shifted home anchors preserved or nudged some early archived rows, but the harder-tail gains came with built-in or `improved-v3/v4` regressions and remained far below `baseline-rnn`. No full-pool expansion, maintained config, holdout, or audit run was promoted."
        )

    if planner_takeover_note.exists():
        lines.append(
            "- Additional planner-takeover structural probe on generation-5 development seeds: safe/grounded/wide transient planner delegation fired on the short screen but sharply regressed built-in and hard archived rows, while strict/net-clear variants were inert ties. No full-pool expansion, maintained edit, holdout, or audit run was promoted."
        )

    pool_opponents = ["builtin", "random", "initial", "improved-v0", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6"]
    pool_rows = [
        (
            opponent,
            latest_dev.get(("net-pressure", opponent)),
            latest_dev.get(("baseline-rnn", opponent)),
            latest_dev.get(("rally-serve", opponent)),
            latest_dev.get(("post-contact", opponent)),
        )
        for opponent in pool_opponents
    ]
    if any(any(entry is not None for entry in entries) for _opponent, *entries in pool_rows):
        lines.extend([
            "",
            "Generation-5 fixed development opponent-pool comparison:",
            "",
            "| Opponent | net-pressure | baseline-rnn | rally-serve | post-contact | net-pressure minus baseline-rnn | net-pressure minus rally-serve | post-contact minus baseline-rnn |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        net_minus_baseline: list[float] = []
        net_minus_rally: list[float] = []
        post_minus_baseline: list[float] = []
        for opponent, net_entry, baseline_entry, rally_entry, post_entry in pool_rows:
            def cell(entry: dict[str, Any] | None) -> str:
                if entry is None:
                    return ""
                wld = entry.get("win_loss_draw", {})
                return "{mean} {wins}/{losses}/{draws} {steps}".format(
                    mean=_stats(_score_mean(entry)),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                    steps=entry.get("environment_steps", ""),
                )

            net_mean = _score_mean(net_entry) if net_entry is not None else None
            baseline_mean = _score_mean(baseline_entry) if baseline_entry is not None else None
            rally_mean = _score_mean(rally_entry) if rally_entry is not None else None
            post_mean = _score_mean(post_entry) if post_entry is not None else None
            baseline_delta = None if net_mean is None or baseline_mean is None else net_mean - baseline_mean
            rally_delta = None if net_mean is None or rally_mean is None else net_mean - rally_mean
            post_baseline_delta = None if post_mean is None or baseline_mean is None else post_mean - baseline_mean
            if baseline_delta is not None:
                net_minus_baseline.append(baseline_delta)
            if rally_delta is not None:
                net_minus_rally.append(rally_delta)
            if post_baseline_delta is not None:
                post_minus_baseline.append(post_baseline_delta)
            lines.append(
                "| {opponent} | {net} | {baseline} | {rally} | {post} | {baseline_delta} | {rally_delta} | {post_baseline_delta} |".format(
                    opponent=opponent,
                    net=cell(net_entry),
                    baseline=cell(baseline_entry),
                    rally=cell(rally_entry),
                    post=cell(post_entry),
                    baseline_delta=_stats(baseline_delta),
                    rally_delta=_stats(rally_delta),
                    post_baseline_delta=_stats(post_baseline_delta),
                )
            )
        if net_minus_baseline:
            better = sum(1 for delta in net_minus_baseline if delta > 0)
            tied = sum(1 for delta in net_minus_baseline if delta == 0)
            worse = sum(1 for delta in net_minus_baseline if delta < 0)
            lines.append(
                f"- Fixed-pool neural comparison: `net-pressure` is better than `baseline-rnn` on `{better}` opponents, tied on `{tied}`, and worse on `{worse}` across the recorded fixed pool."
            )
        if net_minus_rally:
            better = sum(1 for delta in net_minus_rally if delta > 0)
            tied = sum(1 for delta in net_minus_rally if delta == 0)
            worse = sum(1 for delta in net_minus_rally if delta < 0)
            lines.append(
                f"- Fixed-pool heuristic comparison: `net-pressure` is better than `rally-serve` on `{better}` opponents, tied on `{tied}`, and worse on `{worse}` across the recorded fixed pool."
            )
        if post_minus_baseline:
            better = sum(1 for delta in post_minus_baseline if delta > 0)
            tied = sum(1 for delta in post_minus_baseline if delta == 0)
            worse = sum(1 for delta in post_minus_baseline if delta < 0)
            lines.append(
                f"- Fixed-pool post-contact neural comparison: `post-contact` is better than `baseline-rnn` on `{better}` opponents, tied on `{tied}`, and worse on `{worse}` across the recorded fixed pool."
            )
        lines.append(
            "- Promotion recommendation: do not open generation-5 holdout. The fixed-pool comparator rows are now present, and neither `net-pressure` nor `post-contact` beats the neural comparator across the harder archived opponents."
        )
    if aggressive_pressure_note.exists():
        lines.append(
            "- Additional generation-5 failed direction: aggressive low-contact jump/brace rules and brace-serve macros were screened on `12000..12015`; broad pressure collapsed, brace variants either regressed built-in or became no-ops, and no candidate justified a maintained policy edit."
        )
    if stacked_followthrough_note.exists():
        lines.append(
            "- Additional generation-5 mixed/failed direction: front-low recovery, stacked followthrough, and opponent-posture gated low-pressure probes were screened on development seeds; the best full-dev posture gate only nudged `improved-v5/v6` while regressing other fixed-pool rows, so no maintained policy edit was promoted."
        )
    if phase_pressure_note.exists():
        lines.append(
            "- Additional generation-5 mixed direction: phase-gated opponent-side low pressure improved some hard archived rows, with `phase_two_frame` moving built-in by `+0.04` and `improved-v5/v6` by `+0.10/+0.12`, but it regressed `improved-v2/v3` and stayed far below `baseline-rnn`; no maintained policy edit was promoted."
        )
    return lines


def _critic_artifact_lines(critic_dir: Path = DEFAULT_CRITIC_REPORT_DIR) -> list[str]:
    lines = [
        "Claude Code CLI critic artifacts are external advisory context. They can propose next directions, but they are not benchmark evidence and do not change promotion status unless followed by ledgered code/config/test edits.",
        f"The critic also writes a reusable OMX copy under `{DEFAULT_OMX_ARTIFACT_DIR}` unless `--no-omx-artifact` is supplied.",
        "",
    ]
    if not critic_dir.exists():
        return [
            *lines,
            f"No Claude critic artifacts recorded yet in `{critic_dir}`.",
            "Use `make slimevolley-critic ARGS=\"--dry-run\"` to preview the prompt without sending data externally.",
            "Use `make slimevolley-critic ARGS=\"--allow-external-claude\"` only when external Claude review is intentional.",
        ]
    artifacts = sorted(
        [path for path in critic_dir.glob(f"{CRITIC_FILENAME_PREFIX}-*.md") if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not artifacts:
        return [*lines, f"No Claude critic artifacts recorded yet in `{critic_dir}`."]
    lines.extend(
        [
            f"Critic artifact directory: `{critic_dir}`",
            "",
            "| Artifact | Size bytes | Advisory note |",
            "| --- | ---: | --- |",
        ]
    )
    for artifact in artifacts[:5]:
        text = artifact.read_text(encoding="utf-8")
        note = "external advisory critique"
        for marker in ("## Concise Summary", "## Action Items / Next Steps"):
            marker_index = text.find(marker)
            if marker_index >= 0:
                after = text[marker_index + len(marker):].strip().splitlines()
                note = next((line.strip() for line in after if line.strip() and not line.startswith("##")), note)
                break
        lines.append(f"| `{artifact}` | {artifact.stat().st_size} | {note[:160]} |")
    return lines


def _tournament_lines(tournament_path: Path | None) -> list[str]:
    if tournament_path is None or not tournament_path.exists():
        return ["No SlimeVolley round-robin artifact recorded yet."]
    payload = _read_json(tournament_path)
    if not payload:
        return [f"Tournament artifact `{tournament_path}` could not be read."]

    lines = [
        f"- Artifact: `{tournament_path}`",
        f"- Split: `{payload.get('split', '')}`",
        f"- Participants: `{', '.join(payload.get('participants', []))}`",
        f"- Matchups: `{payload.get('matchup_count', '')}`",
        f"- Status: `{payload.get('pass_fail', '')}`",
        "",
        "| Rank | Policy | Mean score across opponents | Win rate | Wins | Losses | Draws | Steps |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(payload.get("standings", []), start=1):
        lines.append(
            "| {rank} | {policy} | {mean} | {win_rate} | {wins} | {losses} | {draws} | {steps} |".format(
                rank=rank,
                policy=row.get("policy", ""),
                mean=_stats(row.get("mean_score_across_opponents")),
                win_rate=_stats(row.get("win_rate")),
                wins=row.get("wins", ""),
                losses=row.get("losses", ""),
                draws=row.get("draws", ""),
                steps=row.get("environment_steps", ""),
            )
        )
    return lines


def _neural_comparator_lines(entries: list[dict[str, Any]]) -> list[str]:
    comparator_entries = [
        entry for entry in entries
        if entry.get("policy_version") == "baseline-rnn"
        and entry.get("pass_fail") == "pass"
        and entry.get("seed_range", {}).get("split") == "dev"
    ]
    if not comparator_entries:
        return ["No neural/RL comparator has been recorded yet."]

    lines = [
        "The `baseline-rnn` policy is slimevolleygym's shipped 120-parameter RNN policy. "
        "It is included as a labeled neural comparator, not as an interpretable heuristic improvement."
    ]
    for entry in sorted(comparator_entries, key=lambda item: item.get("opponent_name", "")):
        wld = entry.get("win_loss_draw", {})
        lines.append(
            f"- `baseline-rnn` vs `{entry.get('opponent_name', '')}`: "
            f"mean `{_stats(entry.get('score_stats', {}).get('mean'))}`, "
            f"wins `{wld.get('wins', '')}`, losses `{wld.get('losses', '')}`, "
            f"draws `{wld.get('draws', '')}`, steps `{entry.get('environment_steps', '')}`."
        )

    by_policy_opponent = {
        (entry.get("policy_version"), entry.get("opponent_name")): entry
        for entry in entries
        if entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "dev"
    }
    heuristic = by_policy_opponent.get(("improved", "builtin"))
    comparator = by_policy_opponent.get(("baseline-rnn", "builtin"))
    if heuristic is not None and comparator is not None:
        heuristic_mean = heuristic.get("score_stats", {}).get("mean")
        comparator_mean = comparator.get("score_stats", {}).get("mean")
        if heuristic_mean is not None and comparator_mean is not None:
            lines.append(
                f"- Built-in-opponent gap on dev seeds: `baseline-rnn` mean `{_stats(comparator_mean)}` "
                f"versus structural heuristic mean `{_stats(heuristic_mean)}`."
            )
    return lines


def _conclusion(
    entries: list[dict[str, Any]],
    status: str,
    *,
    generation_entries: list[dict[str, Any]] | None = None,
    generation3_entries: list[dict[str, Any]] | None = None,
    generation4_entries: list[dict[str, Any]] | None = None,
    generation5_entries: list[dict[str, Any]] | None = None,
) -> str:
    generation_entries = generation_entries or []
    generation3_entries = generation3_entries or []
    generation4_entries = generation4_entries or []
    generation5_entries = generation5_entries or []
    has_generation4_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation4_entries
    )
    has_generation3_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation3_entries
    )
    has_generation_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation_entries
    )
    has_pass = any(entry.get("pass_fail") == "pass" for entry in entries)
    has_dev = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "dev"
        for entry in entries
    )
    has_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in entries
    )
    if status != "available":
        return "The current evidence is a setup failure, not a policy-performance result: the optional legacy Gym/SlimeVolley dependencies are unavailable locally."
    if has_generation4_holdout:
        by_policy_opponent = _latest_entry_map(generation4_entries, "holdout")
        rally = by_policy_opponent.get(("rally-serve", "builtin"))
        comparator = by_policy_opponent.get(("baseline-rnn", "builtin"))
        built_in_sentence = ""
        if rally is not None and comparator is not None:
            rally_mean = _score_mean(rally)
            comparator_mean = _score_mean(comparator)
            delta = None if rally_mean is None or comparator_mean is None else rally_mean - comparator_mean
            built_in_sentence = f" On built-in holdout, `rally-serve` mean `{_stats(rally_mean)}` versus `baseline-rnn` mean `{_stats(comparator_mean)}`, delta `{_stats(delta)}`."
        gen5_dev = _latest_entry_map(generation5_entries, "dev")
        net_pressure = gen5_dev.get(("net-pressure", "builtin"))
        gen5_sentence = ""
        if net_pressure is not None:
            net_mean = _score_mean(net_pressure)
            gen5_sentence = f" A later generation-5 development-only structural probe, `net-pressure`, reached built-in mean `{_stats(net_mean)}`; this is not holdout evidence and must stay on fresh development protocol rails."
        return "Generation-4 holdout evidence exists and is final-only: do not use seeds `1000..1049`, `4000..4049`, `7000..7049`, or `10000..10049` for further policy tuning, and keep generation-4 audit seeds `11000..11049` reserved. The rally-serve candidate beat the packaged RNN on built-in development seeds but failed to beat it on sealed built-in holdout." + built_in_sentence + gen5_sentence + " This SlimeVolley run therefore weakens the final generalization claim, though generation-5 has reopened a clean development path toward a better heuristic."
    if has_generation3_holdout:
        return "Generation-3 holdout evidence exists and is final-only: do not use seeds `1000..1049`, `4000..4049`, or `7000..7049` for further policy tuning. The maintained heuristic improved strongly over the initial and scalar-tuned heuristics against random, initial, and archived heuristic opponents, with archived development checkpoints now extending through `improved-v6`, but it still failed to solve the built-in opponent and remained far behind the packaged RNN comparator. This SlimeVolley run therefore provides weak or mixed support for heuristic learning, and it weakens any claim that the current heuristic performs similarly to a deep/RNN baseline."
    if has_generation_holdout:
        return "Generation-2 holdout evidence exists and is final-only: do not use seeds `1000..1049` or `4000..4049` for further policy tuning. The maintained heuristic improved over the initial and scalar-tuned heuristics against non-built-in opponents, but it remained far from the packaged RNN comparator and did not solve the built-in opponent. This SlimeVolley run therefore provides weak or mixed support for heuristic learning, and it weakens any claim that the current heuristic performs similarly to a deep/RNN baseline."
    if has_holdout:
        return "Holdout evidence exists and is final-only: do not use it for further policy tuning. The maintained heuristic improved over the initial heuristic against non-built-in opponents, but it remained far from the packaged RNN comparator and did not solve the built-in opponent. This SlimeVolley run therefore provides weak or mixed support for heuristic learning, and it weakens any claim that the current heuristic performs similarly to a deep/RNN baseline."
    has_rnn_comparator = any(
        entry.get("pass_fail") == "pass"
        and entry.get("policy_version") == "baseline-rnn"
        and entry.get("seed_range", {}).get("split") == "dev"
        for entry in entries
    )
    if has_dev and has_rnn_comparator:
        return "Development-seed evidence exists: structural low-ball rescue improves the non-built-in opponent pool, but current heuristics remain noncompetitive with the built-in baseline. The later late_low_ball_guard and grounded_low_receive edits are preserved as audited partial directions, but paired dev evidence shows both tied their frozen predecessors rather than improving aggregate scores. The labeled pretrained RNN comparator is substantially stronger across the opponent pool, so the heuristic-learning evidence is currently mixed and incomplete. Holdout remains intentionally untouched."
    if has_dev:
        return "Development-seed evidence exists: structural low-ball rescue improves the non-built-in opponent pool, but current heuristics remain noncompetitive with the built-in baseline. Holdout remains intentionally untouched."
    if has_pass:
        return "Smoke evidence exists, but development-seed and holdout conclusions are not justified yet."
    return "No successful SlimeVolley evaluation exists yet."


def _next_steps(
    entries: list[dict[str, Any]],
    status: str,
    *,
    generation_entries: list[dict[str, Any]] | None = None,
    generation3_entries: list[dict[str, Any]] | None = None,
    generation4_entries: list[dict[str, Any]] | None = None,
    generation5_entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    generation_entries = generation_entries or []
    generation3_entries = generation3_entries or []
    generation4_entries = generation4_entries or []
    generation5_entries = generation5_entries or []
    has_generation4_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation4_entries
    )
    has_generation3_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation3_entries
    )
    has_generation_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in generation_entries
    )
    has_dev = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "dev"
        for entry in entries
    )
    has_holdout = any(
        entry.get("pass_fail") == "pass" and entry.get("seed_range", {}).get("split") == "holdout"
        for entry in entries
    )
    has_scalar_search = any(
        entry.get("pass_fail") == "pass" and entry.get("change_type") == "scalar/config tuning"
        for entry in entries
    )
    if status != "available":
        return [
            "1. Install the legacy SlimeVolley dependency stack exactly as documented.",
            "2. Rerun `make slimevolley-doctor` and commit the resulting diagnostics.",
            "3. Repeat the smoke evaluation before development-seed runs.",
            "4. Keep failure rows append-only and avoid holdout evaluations until the policy/opponent protocol is frozen.",
        ]
    if has_generation4_holdout:
        gen5_dev = _latest_entry_map(generation5_entries, "dev")
        if gen5_dev.get(("net-pressure", "builtin")) is not None:
            gen5_fixed_pool = ["builtin", "random", "initial", "improved-v0", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6"]
            gen5_fixed_pool_complete = all(
                gen5_dev.get((policy, opponent)) is not None
                for policy in ("net-pressure", "baseline-rnn", "rally-serve")
                for opponent in gen5_fixed_pool
            )
            if gen5_fixed_pool_complete:
                return [
                    "1. Treat consumed holdout seeds `1000..1049`, `4000..4049`, `7000..7049`, and `10000..10049` as frozen final evidence; do not tune against any consumed holdout range.",
                    "2. Continue generation-5 only on development seeds `12000..12049`; keep generation-5 holdout `13000..13049` and audit `14000..14049` unopened.",
                    "3. Do not promote `net-pressure`: the fixed development pool shows it beats `baseline-rnn` on built-in mean but trails the neural comparator on the harder archived opponents.",
                    "4. Hard-opponent trace/probe diagnostics are now recorded; the tested front-net, brace-action, and contact-quality rules were mixed or harmful. The next generation-5 development edit should require a more specific multi-frame contact-quality detector before rerunning the fixed development pool.",
                ]
            return [
                "1. Treat consumed holdout seeds `1000..1049`, `4000..4049`, `7000..7049`, and `10000..10049` as frozen final evidence; do not tune against any consumed holdout range.",
                "2. Continue generation-5 only on development seeds `12000..12049`; keep generation-5 holdout `13000..13049` and audit `14000..14049` unopened.",
                "3. Regenerate same-seed generation-5 development comparator rows for `baseline-rnn` and `rally-serve` against the fixed opponent pool before any promotion claim.",
                "4. Inspect `net-pressure` draw traces where `baseline-rnn` wins, then make at most one structural edit before re-running the fixed development pool.",
            ]
        return [
            "1. Treat SlimeVolley policy evidence as frozen for consumed holdout seeds `1000..1049`, `4000..4049`, `7000..7049`, and `10000..10049`; do not tune against any consumed holdout range.",
            "2. Keep generation-4 audit seeds `11000..11049` reserved unless a separate independent audit is explicitly predeclared; do not use them for tuning.",
            "3. If continuing SlimeVolley policy research, predeclare a generation-5 protocol with fresh development, holdout, and audit seed ranges before making new policy-selection claims.",
            "4. Preserve `rally-serve` and all archived opponent checks so future changes cannot hide the generation-4 holdout regression against `baseline-rnn`.",
        ]
    if has_generation3_holdout:
        return [
            "1. Treat SlimeVolley policy evidence as frozen for consumed seeds `1000..1049`, `4000..4049`, and `7000..7049`; do not tune against any of those holdout ranges.",
            "2. If continuing SlimeVolley policy research, follow the predeclared generation-4 protocol: develop only on seeds `9000..9049`, keep holdout seeds `10000..10049` sealed until freeze, and reserve audit seeds `11000..11049`.",
            "3. Keep the current work focused on documentation, tests, audit tooling, or adding new environment adapters.",
            "4. Preserve archived policies and opponent-pool checks so future changes cannot silently erase regressions.",
        ]
    if has_generation_holdout:
        return [
            "1. Treat SlimeVolley policy evidence as frozen for consumed seeds `1000..1049` and `4000..4049`; do not tune against either holdout range.",
            "2. If continuing SlimeVolley policy research, predeclare a fresh later-generation protocol with new development, holdout, and audit seed ranges before making policy-selection claims.",
            "3. Keep the current work focused on documentation, tests, audit tooling, or adding new environment adapters.",
            "4. Preserve archived policies and opponent-pool checks so future changes cannot silently erase regressions.",
        ]
    if has_holdout:
        return [
            "1. Treat the current SlimeVolley policy/evidence set as frozen for seeds `1000..1049`; do not tune against these holdout rows.",
            "2. If continuing SlimeVolley policy research, predeclare a fresh experiment generation with new development and holdout seed ranges.",
            "3. Keep the current work focused on documentation, tests, audit tooling, or adding new environment adapters.",
            "4. Preserve archived policies and opponent-pool checks so future changes cannot silently erase regressions.",
        ]
    if not has_dev:
        return [
            "1. Run fixed development-seed evaluations against `builtin`, `random`, `initial`, and archived heuristic opponents.",
            "2. Generate scalar-search baselines only on development seeds.",
            "3. Inspect failures before changing heuristic structure.",
            "4. Keep holdout untouched until the policy/opponent protocol is frozen.",
        ]
    if has_scalar_search:
        return [
            "1. Add a targeted structural policy change for the built-in-opponent serve/return failure mode.",
            "2. Re-run the fixed development opponent matrix and compare against initial, frozen archive, and scalar-search baselines.",
            "3. If a candidate is selected, freeze its opponent archive before any holdout run.",
            "4. Keep holdout untouched until the next structural and scalar baselines are frozen.",
        ]
    return [
        "1. Add a targeted structural policy change for the built-in-opponent failure mode.",
        "2. Run scalar/config search as a separately labeled baseline on development seeds only.",
        "3. Re-run the fixed development opponent matrix and compare against the archived policies.",
        "4. Keep holdout untouched until after the policy and scalar-search baselines are frozen.",
    ]


def render_slimevolley_report(
    *,
    ledger_path: Path = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    summary_path: Path = env_summary_path(SLIMEVOLLEY_ENV_ID),
    report_path: Path = env_report_path(SLIMEVOLLEY_ENV_ID),
    diagnostics_path: Path | None = None,
    search_best_path: Path | None = None,
    tournament_path: Path | None = None,
    holdout_path: Path | None = None,
    critic_dir: Path = DEFAULT_CRITIC_REPORT_DIR,
) -> str:
    """Render and write the SlimeVolley experiment report."""

    amendments_path = default_amendments_path(ledger_path)
    raw_entries = read_entries(ledger_path)
    amendments = read_ledger_amendments(amendments_path)
    entries, amendment_issues, _amendment_counts = apply_ledger_amendments(
        raw_entries,
        amendments,
        target_ledger=ledger_path.name,
    )
    if amendment_issues:
        raise ValueError("invalid SlimeVolley ledger amendments: " + "; ".join(amendment_issues[:5]))
    if ledger_path.exists():
        write_summary_csv(ledger_path, summary_path, entries=entries)
    generation_ledger_path = ledger_path.with_name("generation_2_trials.jsonl")
    generation_entries = read_entries(generation_ledger_path) if generation_ledger_path.exists() else []
    generation3_ledger_path = ledger_path.with_name("generation_3_trials.jsonl")
    generation3_entries = read_entries(generation3_ledger_path) if generation3_ledger_path.exists() else []
    generation4_ledger_path = ledger_path.with_name("generation_4_trials.jsonl")
    generation4_entries = read_entries(generation4_ledger_path) if generation4_ledger_path.exists() else []
    generation5_ledger_path = ledger_path.with_name("generation_5_trials.jsonl")
    generation5_entries = read_entries(generation5_ledger_path) if generation5_ledger_path.exists() else []
    diagnostics = _read_json(diagnostics_path) if diagnostics_path is not None else None
    if search_best_path is None:
        search_best_path = ledger_path.with_name("search_best_dev.json")
    if tournament_path is None:
        tournament_path = ledger_path.with_name("round_robin_dev.json")
    if holdout_path is None:
        holdout_path = ledger_path.with_name("holdout_final.json")
    generator_package_versions = dependency_versions()
    runtime_metadata = _latest_runtime_metadata(entries)
    package_versions = _package_versions_for_report(
        diagnostics=diagnostics,
        runtime_metadata=runtime_metadata,
        generator_package_versions=generator_package_versions,
    )
    status = diagnostics.get("status") if diagnostics else "not recorded"
    registration = registration_for(SLIMEVOLLEY_ENV_ID)

    lines = [
        "# SlimeVolley Heuristic Learning Report",
        "",
        "## Status",
        "",
        f"- Environment id: `{SLIMEVOLLEY_ENV_ID}`",
        f"- Environment availability: `{status}`",
        f"- Ledger: `{ledger_path}`",
        f"- Summary CSV: `{summary_path}`",
        f"- Registration status: `{registration.status}`; custom SlimeVolley commands are active, while aggregate `eval-all` remains limited to generic Gymnasium-style environments.",
        f"- Custom module root: `{registration.custom_module_root}`; this bridge delegates to `hl_benchmark.slimevolley` for implementation compatibility.",
        "",
        "## Dependency Versions",
        "",
        "Versions prefer the latest ledger `runtime_metadata.packages` snapshot, with `environment_diagnostics.json` overriding the SlimeVolley-specific package probes when available. This avoids rewriting the recorded environment stack when the report is regenerated with a different Python interpreter.",
        "",
    ]
    for package_name, version in sorted(package_versions.items()):
        lines.append(f"- {package_name}: `{version}`")
    lines.extend(["", "## Runtime Metadata", "", *_runtime_metadata_lines(runtime_metadata)])
    if diagnostics:
        lines.extend(
            [
                "",
                "## Environment Diagnostics",
                "",
                f"- Message: {diagnostics.get('message', '')}",
                f"- Observation space: `{diagnostics.get('observation_space', diagnostics.get('expected_observation_space', 'unknown'))}`",
                f"- Action space: `{diagnostics.get('action_space', diagnostics.get('expected_action_space', 'unknown'))}`",
                f"- Step API: `{diagnostics.get('expected_step_api', 'unknown')}`",
                f"- Observed step API: `{diagnostics.get('observed_step_api', 'unknown')}`",
                f"- Observed multi-agent step API: `{diagnostics.get('multiagent_step_api_observed', 'unknown')}`",
                f"- Seed API behavior: {diagnostics.get('seed_api_behavior', 'unknown')}",
                f"- Same-seed reset observation match: `{diagnostics.get('same_seed_reset_observation_equal', 'unknown')}`",
                f"- Reward semantics: {diagnostics.get('reward_semantics', 'unknown')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Reproduction Commands",
            "",
            *_reproduction_command_lines(),
            "",
            "## Artifact Integrity Checks",
            "",
            *_artifact_integrity_lines(entries),
            "",
            "## Artifact Manifest",
            "",
            *_artifact_manifest_lines(),
            "",
            "## Opponent Protocol",
            "",
            "| Name | Version | Kind | Description |",
            "| --- | --- | --- | --- |",
        ]
    )
    for spec in OPPONENT_POOL.values():
        lines.append(f"| {spec.name} | {spec.version} | {spec.kind} | {spec.description} |")
    lines.extend(
        [
            "",
            "## Ledger Summary",
            "",
            f"Recorded SlimeVolley trials: {len(entries)}",
            "",
            *_result_table(entries),
            "",
            "## Failure Notes",
            "",
            *_failure_lines(entries),
            "",
            "## Seed Ranges",
            "",
            *_seed_range_lines(entries),
            "",
            "## Policy Evolution Timeline",
            "",
            *_policy_evolution_lines(entries + generation_entries + generation3_entries + generation4_entries + generation5_entries),
            "",
            "## Development Diagnosis",
            "",
            *_dev_diagnosis_lines(entries),
            "",
            "## Diagnostic Coverage",
            "",
            *_diagnostic_coverage_lines(entries),
            "",
            "## Trace Diagnostics",
            "",
            *_trace_diagnostic_lines(entries),
            "",
            "## Failed Or Partial Directions",
            "",
            *_failed_or_partial_direction_lines(entries),
            "",
            "## Round-Robin Tournament",
            "",
            *_tournament_lines(tournament_path),
            "",
            "## Holdout Evaluation",
            "",
            *_holdout_lines(entries, holdout_path),
            "",
            "## Generation-2 Evidence",
            "",
            *_generation_2_evidence_lines(ledger_path),
            "",
            "## Generation-3 Evidence",
            "",
            *_generation_3_evidence_lines(ledger_path),
            "",
            "## Generation-4 Development Attempt",
            "",
            *_generation_4_development_lines(ledger_path),
            "",
            "## Generation-5 Development Attempt",
            "",
            *_generation_5_development_lines(ledger_path),
            "",
            "## External Critic",
            "",
            *_critic_artifact_lines(critic_dir),
            "",
            "## Scalar Search Baseline",
            "",
            *_scalar_search_lines(entries, search_best_path),
            "",
            "## Neural/RL Comparator",
            "",
            *_neural_comparator_lines(entries + generation_entries + generation3_entries + generation4_entries + generation5_entries),
            "",
            "## Cost Accounting",
            "",
            *_cost_accounting_lines(
                entries,
                generation_entries=generation_entries,
                generation3_entries=generation3_entries,
                generation4_entries=generation4_entries,
                generation5_entries=generation5_entries,
            ),
            "",
            "## Hypothesis Evidence Verdict",
            "",
            *_evidence_verdict_lines(entries, generation_entries=generation_entries, generation3_entries=generation3_entries, generation4_entries=generation4_entries, generation5_entries=generation5_entries),
            "",
            "## Anti-Cheating And Limitations",
            "",
            *_anti_cheating_and_limitations_lines(entries, str(status), generation_entries=generation_entries, generation3_entries=generation3_entries, generation4_entries=generation4_entries, generation5_entries=generation5_entries),
            "",
            "## Current Conclusion",
            "",
            _conclusion(entries, str(status), generation_entries=generation_entries, generation3_entries=generation3_entries, generation4_entries=generation4_entries, generation5_entries=generation5_entries),
            "",
            "## Next Steps",
            "",
            *_next_steps(entries, str(status), generation_entries=generation_entries, generation3_entries=generation3_entries, generation4_entries=generation4_entries, generation5_entries=generation5_entries),
        ]
    )
    report = "\n".join(lines) + "\n"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--summary", type=Path, default=env_summary_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument("--output", type=Path, default=env_report_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument(
        "--diagnostics",
        type=Path,
        default=env_ledger_path(SLIMEVOLLEY_ENV_ID).with_name("environment_diagnostics.json"),
    )
    parser.add_argument(
        "--search-best",
        type=Path,
        default=env_ledger_path(SLIMEVOLLEY_ENV_ID).with_name("search_best_dev.json"),
    )
    parser.add_argument(
        "--tournament",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_dev.json",
    )
    parser.add_argument(
        "--holdout",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json",
    )
    parser.add_argument(
        "--critic-dir",
        type=Path,
        default=DEFAULT_CRITIC_REPORT_DIR,
    )
    args = parser.parse_args()
    render_slimevolley_report(
        ledger_path=args.ledger,
        summary_path=args.summary,
        report_path=args.output,
        diagnostics_path=args.diagnostics,
        search_best_path=args.search_best,
        tournament_path=args.tournament,
        holdout_path=args.holdout,
        critic_dir=args.critic_dir,
    )
    print(args.output)


if __name__ == "__main__":
    main()
