"""Claude Code CLI critic for SlimeVolley performance evidence.

The critic is an external advisory tool. It summarizes already-recorded
SlimeVolley development evidence, asks the local Claude CLI for critique and
next directions, and saves the prompt/response as an auditable artifact. It does
not edit policies, run evaluations, or select holdout candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from hl_benchmark.artifacts import PROJECT_ROOT, env_reports_dir, env_results_dir
from hl_benchmark.ledger import read_entries
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID


DEFAULT_GENERATION4_LEDGER = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_trials.jsonl"
DEFAULT_GENERATION4_SUMMARY = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_summary.csv"
DEFAULT_GENERATION5_LEDGER = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_5_trials.jsonl"
DEFAULT_GENERATION5_SUMMARY = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_5_summary.csv"
DEFAULT_CRITIC_LEDGER = DEFAULT_GENERATION5_LEDGER if DEFAULT_GENERATION5_LEDGER.exists() else DEFAULT_GENERATION4_LEDGER
DEFAULT_CRITIC_SUMMARY = DEFAULT_GENERATION5_SUMMARY if DEFAULT_GENERATION5_LEDGER.exists() else DEFAULT_GENERATION4_SUMMARY
DEFAULT_FINAL_REPORT = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "final_report.md"
DEFAULT_CRITIC_REPORT_DIR = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "critic"
DEFAULT_OMX_ARTIFACT_DIR = PROJECT_ROOT / ".omx" / "artifacts"
DEFAULT_JOINT_ATTACK_SEARCH_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_4_joint_attack_scalar_search_attempt.md"
DEFAULT_LOW_RECEIVE_FOLLOWUP_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_4_low_receive_teacher_scalar_followup.md"
DEFAULT_RALLY_SERVE_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_4_rally_serve_candidate.md"
DEFAULT_GENERATION5_NET_PRESSURE_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_net_pressure_attempt.md"
DEFAULT_GENERATION5_FIXED_POOL_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_fixed_pool_comparator.md"
DEFAULT_GENERATION5_AGGRESSIVE_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_aggressive_pressure_and_brace_probe.md"
DEFAULT_GENERATION5_STACKED_POSTURE_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_stacked_followthrough_and_posture_probe.md"
DEFAULT_GENERATION5_RALLY_SETUP_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_rally_setup_probe.md"
DEFAULT_GENERATION5_CONTACT_TIMING_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_contact_timing_probe.md"
DEFAULT_GENERATION5_APPROACH_QUALITY_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_approach_quality_probe.md"
DEFAULT_GENERATION5_CONTACT_QUALITY_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_contact_quality_probe.md"
DEFAULT_GENERATION5_POSITION_POSTURE_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_position_posture_probe.md"
DEFAULT_GENERATION5_PLANNER_TAKEOVER_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_5_planner_takeover_probe.md"
DEFAULT_PARALLEL_SYNTHESIS_REPORT = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "parallel" / "20260527_parallel_synthesis_rallyserve.md"
DEFAULT_PARALLEL_TRACE_REPORT = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "parallel" / "20260527_trace_rally_attack_rnn_worker.md"
DEFAULT_TASK = "Critique the current SlimeVolley heuristic-learning performance and propose the next improvement direction."
CRITIC_FILENAME_PREFIX = "claude-slimevolley-critic"

Runner = Callable[[list[str]], str]


@dataclass(frozen=True)
class ClaudeCriticResult:
    """Paths and payload from one critic run."""

    prompt: str
    claude_output: str
    report_artifact_path: Path | None
    omx_artifact_path: Path | None
    metadata: dict[str, Any]


def _sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _score_mean(entry: dict[str, Any]) -> float | None:
    value = entry.get("score_stats", {}).get("mean")
    return float(value) if isinstance(value, (int, float)) else None


def _wld(entry: dict[str, Any]) -> str:
    values = entry.get("win_loss_draw", {})
    return "{}/{}/{}".format(values.get("wins", ""), values.get("losses", ""), values.get("draws", ""))


def _seed_label(entry: dict[str, Any]) -> str:
    seed_range = entry.get("seed_range", {})
    start = seed_range.get("start")
    stop_exclusive = seed_range.get("stop_exclusive")
    if isinstance(start, int) and isinstance(stop_exclusive, int):
        return f"{start}..{stop_exclusive - 1}"
    return "unknown"


@dataclass(frozen=True)
class CriticGenerationContext:
    """Human-readable seed and interpretation context for one selected ledger."""

    label: str
    dev_seeds: str
    holdout_seeds: str
    audit_seeds: str
    holdout_note: str
    audit_note: str


def _critic_generation_context(ledger_path: Path) -> CriticGenerationContext:
    name = ledger_path.name
    if "generation_5" in name:
        return CriticGenerationContext(
            label="generation-5",
            dev_seeds="12000..12049",
            holdout_seeds="13000..13049",
            holdout_note="sealed and unavailable for tuning",
            audit_seeds="14000..14049",
            audit_note="reserved for independent checks and unavailable for tuning",
        )
    if "generation_4" in name:
        return CriticGenerationContext(
            label="generation-4",
            dev_seeds="9000..9049",
            holdout_seeds="10000..10049",
            holdout_note="consumed for final-only evaluation and unavailable for tuning",
            audit_seeds="11000..11049",
            audit_note="reserved for independent checks and unavailable for tuning",
        )
    return CriticGenerationContext(
        label="selected generation",
        dev_seeds="the selected ledger's development split",
        holdout_seeds="the selected ledger's holdout split",
        holdout_note="excluded from next-direction development context",
        audit_seeds="the selected ledger's audit split",
        audit_note="excluded from next-direction development context",
    )


def _known_interpretation_lines(generation: CriticGenerationContext) -> list[str]:
    if generation.label == "generation-5":
        return [
            "- Generation-5 is fresh post-generation-4 development context; generation-5 holdout and audit seeds remain sealed and must not be used for tuning.",
            "- `net-pressure` is the current best generation-5 structural probe: it beats `baseline-rnn` on built-in development mean but remains behind on hard archived opponents.",
            "- `post-contact` did not transfer into a fixed-pool improvement over `net-pressure` and is not promoted.",
            "- Broad aggressive low-contact, brace-serve, front-low recovery, stacked followthrough, and opponent-posture low-pressure probes produced mixed or negative development evidence and should not be promoted without stronger fixed-pool rows.",
            "- The remaining gap is not a single terminal-frame action problem. A post-own-contact front-anchor rally-setup phase was tried and rejected because it preserved only built-in, regressed `improved-v3/v4`, and left `improved-v5/v6` unchanged.",
            "- A contact-timing diagnostic then showed `net-pressure` already jumps on most low front-court terminal frames; narrow vertical/back/base jump overrides tied the reference and were not promoted.",
            "- A pre-contact approach diagnostic found `net-pressure` farther behind the ball than `baseline-rnn` eight frames before low terminal windows, but early-jump copies collapsed performance; broad and far-behind no-jump approach variants were mixed or harmful and were not promoted.",
            "- A contact-quality probe tried recent-contact gates, stricter descent gates, and `110`/`111` brace substitutions; hard-tail nudges came with built-in or `improved-v3/v4` regressions and no candidate was promoted.",
            "- A front-posture scalar/config probe tried front-shifted home anchors; minor archived-row nudges were offset by built-in or hard-tail regressions, so no candidate was promoted.",
            "- A planner-takeover structural probe tried short transparent-planner delegation; active gates sharply regressed built-in and hard archived rows, while narrow gates were inert.",
            "- The next credible direction should avoid copying single RNN actions; it should model a longer phase controller or explicitly test draw-reduction goals separately from hard archived-opponent robustness.",
            f"- Generation-5 net-pressure note, if present: `{DEFAULT_GENERATION5_NET_PRESSURE_NOTE}`.",
            f"- Generation-5 fixed-pool comparator note, if present: `{DEFAULT_GENERATION5_FIXED_POOL_NOTE}`.",
            f"- Generation-5 aggressive pressure/brace note, if present: `{DEFAULT_GENERATION5_AGGRESSIVE_NOTE}`.",
            f"- Generation-5 stacked followthrough/posture note, if present: `{DEFAULT_GENERATION5_STACKED_POSTURE_NOTE}`.",
            f"- Generation-5 rally-setup note, if present: `{DEFAULT_GENERATION5_RALLY_SETUP_NOTE}`.",
            f"- Generation-5 contact-timing note, if present: `{DEFAULT_GENERATION5_CONTACT_TIMING_NOTE}`.",
            f"- Generation-5 approach-quality note, if present: `{DEFAULT_GENERATION5_APPROACH_QUALITY_NOTE}`.",
            f"- Generation-5 contact-quality note, if present: `{DEFAULT_GENERATION5_CONTACT_QUALITY_NOTE}`.",
            f"- Generation-5 position/posture note, if present: `{DEFAULT_GENERATION5_POSITION_POSTURE_NOTE}`.",
            f"- Generation-5 planner-takeover note, if present: `{DEFAULT_GENERATION5_PLANNER_TAKEOVER_NOTE}`.",
            "- The packaged `baseline-rnn` is a comparator/possible teacher for dev-only rule discovery, not a runtime maintained heuristic.",
        ]
    return [
        "- The current maintained `improved` heuristic remains stronger than `planner` and `teacher-assisted` against the built-in opponent on development seeds.",
        "- `improved-tuned` is a scalar/config baseline: it improves built-in development score but remains below `baseline-rnn` and is not structural improvement evidence.",
        "- The `attack` candidate is a structural partial: it improves built-in development score but remains below `baseline-rnn` and regresses nearest archived opponents, so it is not promoted.",
        "- A follow-up scalar search around `attack` found a built-in-only development candidate at mean `-0.10`, still below `baseline-rnn` mean `0.12` and worse or tied against all non-built-in opponents; it is not promoted.",
        "- A later parallel scalar/config search found a stronger built-in-only candidate at mean `-0.02` with `low_ball_rescue_x_window=0.48`; it still trails `baseline-rnn` mean `0.12`, is scalar-only, and is not promoted.",
        "- A low-receive teacher-action follow-up found RNN jump signals in low own-side loss windows, but targeted `LowDriveFinish` and `NetVerticalBlock` structural probes tied or worsened the short screen; a bounded 98-config scalar follow-up again topped out at mean `-0.02` and is not promoted.",
        "- The `rally-serve` candidate adds a point-reset serve detector plus scalar fields; it beat `baseline-rnn` on built-in development seeds (`0.14` vs `0.12`) but failed to beat it on final-only built-in holdout (`-0.22` vs `-0.12`). Do not propose tuning from this holdout outcome; any new policy-selection work needs a fresh predeclared generation.",
        "- The latest parallel6 rally-serve pass found one scalar/config candidate, `rally-serve-low-x52`, after fixed development opponent-pool checks: built-in mean `0.18` versus current `rally-serve` `0.14` and `baseline-rnn` `0.12`. It is scalar-only development evidence, not structural progress, and holdout/audit seeds remain closed.",
        "- Trace diagnostics show `rally-serve` improves over `attack` by reducing point losses from `32` to `18`, but it wins fewer built-in matches than `baseline-rnn` (`13` versus `18`) and relies more on draws (`29` versus `20`).",
        f"- Joint scalar-search note, if present: `{DEFAULT_JOINT_ATTACK_SEARCH_NOTE}`.",
        f"- Low-receive teacher/scalar follow-up note, if present: `{DEFAULT_LOW_RECEIVE_FOLLOWUP_NOTE}`.",
        f"- Rally-serve candidate note, if present: `{DEFAULT_RALLY_SERVE_NOTE}`.",
        f"- Parallel synthesis report, if present: `{DEFAULT_PARALLEL_SYNTHESIS_REPORT}`.",
        f"- Parallel trace report, if present: `{DEFAULT_PARALLEL_TRACE_REPORT}`.",
        "- The planner variants should not be promoted without new evidence; their failed rows remain append-only evidence.",
        "- The packaged `baseline-rnn` is a comparator/possible teacher for dev-only rule discovery, not a runtime maintained heuristic.",
    ]


def _latest_dev_entries(entries: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in entries:
        seed_range = entry.get("seed_range", {})
        if entry.get("pass_fail") != "pass" or seed_range.get("split") != "dev":
            continue
        policy = entry.get("policy_version")
        opponent = entry.get("opponent_name")
        if isinstance(policy, str) and isinstance(opponent, str):
            latest[(policy, opponent)] = entry
    return latest


def _mode_counts(entry: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for episode in entry.get("per_episode", []):
        for event in episode.get("point_events", []):
            diagnostics = event.get("policy_diagnostics", {})
            mode = diagnostics.get("mode") if isinstance(diagnostics, dict) else None
            if isinstance(mode, str):
                counts[mode] = counts.get(mode, 0) + 1
            for frame in event.get("pre_event_trace", []):
                frame_diagnostics = frame.get("policy_diagnostics", {})
                frame_mode = frame_diagnostics.get("mode") if isinstance(frame_diagnostics, dict) else None
                if isinstance(frame_mode, str):
                    key = f"trace:{frame_mode}"
                    counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:12])


def _failure_note(entry: dict[str, Any]) -> str:
    return str(entry.get("failure_analysis", "")).replace("\n", " ")[:160]


def _performance_table(entries: list[dict[str, Any]]) -> list[str]:
    latest = _latest_dev_entries(entries)
    rows = [
        "| Policy | Opponent | Seeds | Episodes | Mean | W/L/D | Steps | Notes |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | --- |",
    ]
    interesting = [
        ("baseline-rnn", "builtin"),
        ("net-pressure", "builtin"),
        ("rally-serve", "builtin"),
        ("post-contact", "builtin"),
        ("attack", "builtin"),
        ("improved-tuned", "builtin"),
        ("temporal", "builtin"),
        ("planner", "builtin"),
        ("teacher-assisted", "builtin"),
        ("net-pressure", "random"),
        ("baseline-rnn", "random"),
        ("net-pressure", "initial"),
        ("baseline-rnn", "initial"),
        ("net-pressure", "improved-v0"),
        ("baseline-rnn", "improved-v0"),
        ("net-pressure", "improved-v2"),
        ("baseline-rnn", "improved-v2"),
        ("net-pressure", "improved-v3"),
        ("baseline-rnn", "improved-v3"),
        ("net-pressure", "improved-v4"),
        ("baseline-rnn", "improved-v4"),
        ("net-pressure", "improved-v5"),
        ("baseline-rnn", "improved-v5"),
        ("net-pressure", "improved-v6"),
        ("baseline-rnn", "improved-v6"),
        ("rally-serve", "improved-v5"),
        ("rally-serve", "improved-v6"),
        ("post-contact", "improved-v5"),
        ("post-contact", "improved-v6"),
        ("improved", "builtin"),
        ("improved", "improved-v5"),
        ("improved", "improved-v6"),
    ]
    seen: set[tuple[str, str]] = set()
    for key in interesting:
        entry = latest.get(key)
        if entry is None:
            continue
        seen.add(key)
        rows.append(
            "| {policy} | {opponent} | `{seeds}` | {episodes} | {mean} | {wld} | {steps} | {notes} |".format(
                policy=key[0],
                opponent=key[1],
                seeds=_seed_label(entry),
                episodes=entry.get("episodes", ""),
                mean=_score_mean(entry),
                wld=_wld(entry),
                steps=entry.get("environment_steps", ""),
                notes=_failure_note(entry),
            )
        )
    for key, entry in sorted(latest.items()):
        if key in seen or key[1] != "builtin" or key[0] not in {"planner", "teacher-assisted", "temporal", "attack", "rally-serve"}:
            continue
        rows.append(
            "| {policy} | {opponent} | `{seeds}` | {episodes} | {mean} | {wld} | {steps} | {notes} |".format(
                policy=key[0],
                opponent=key[1],
                seeds=_seed_label(entry),
                episodes=entry.get("episodes", ""),
                mean=_score_mean(entry),
                wld=_wld(entry),
                steps=entry.get("environment_steps", ""),
                notes=_failure_note(entry),
            )
        )
    return rows


def _diagnostic_lines(entries: list[dict[str, Any]]) -> list[str]:
    latest = _latest_dev_entries(entries)
    lines: list[str] = []
    for key in [("planner", "builtin"), ("teacher-assisted", "builtin")]:
        entry = latest.get(key)
        if entry is None:
            continue
        modes = _mode_counts(entry)
        if modes:
            lines.append(f"- {key[0]} vs {key[1]} mode counts: `{modes}`")
    if not lines:
        lines.append("- No planner policy diagnostics were found in the selected development rows.")
    return lines


def _report_excerpt(report_path: Path, *, context: str) -> str:
    if context != "full" or not report_path.exists():
        return ""
    text = report_path.read_text(encoding="utf-8")
    headings = [
        "## Generation-5 Development Attempt",
        "## Generation-4 Development Attempt",
        "## Neural/RL Comparator",
        "## Current Conclusion",
        "## Next Steps",
    ]
    chunks: list[str] = []
    for heading in headings:
        start = text.find(heading)
        if start < 0:
            continue
        next_start = text.find("\n## ", start + len(heading))
        chunks.append(text[start: next_start if next_start >= 0 else len(text)].strip())
    return "\n\n".join(chunks)


def build_critic_prompt(
    *,
    ledger_path: Path = DEFAULT_CRITIC_LEDGER,
    summary_path: Path = DEFAULT_CRITIC_SUMMARY,
    report_path: Path = DEFAULT_FINAL_REPORT,
    context: str = "sanitized",
    task: str = DEFAULT_TASK,
) -> str:
    """Build the prompt sent to Claude without using holdout rows as tuning context."""

    entries = read_entries(ledger_path) if ledger_path.exists() else []
    dev_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") == "dev"]
    sealed_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") in {"holdout", "audit"}]
    generation = _critic_generation_context(ledger_path)
    lines = [
        "You are an external critic for a transparent SlimeVolley heuristic-learning experiment.",
        "Your job is to critique current development performance and propose auditable next directions.",
        "Do not ask to tune on holdout or audit seeds. Do not propose hidden neural runtime policies as the maintained heuristic.",
        "Separate structural heuristic ideas from scalar/config tuning and from teacher-assisted rule discovery.",
        "",
        f"Task: {task}",
        "",
        f"Current {generation.label} guardrails:",
        f"- Development seeds: {generation.dev_seeds}.",
        f"- Holdout seeds: {generation.holdout_seeds}; {generation.holdout_note}.",
        f"- Audit seeds: {generation.audit_seeds}; {generation.audit_note}.",
        f"- Selected ledger path: {ledger_path}",
        f"- Selected summary path: {summary_path}",
        f"- Sealed holdout/audit rows in this selected ledger: {len(sealed_entries)}; these rows are excluded from next-direction development context.",
        "",
        f"Development rows available: {len(dev_entries)}",
        "",
        "Latest development performance table:",
        *_performance_table(dev_entries),
        "",
        "Planner/teacher diagnostic summary:",
        *_diagnostic_lines(dev_entries),
        "",
        "Known interpretation before critic review:",
        *_known_interpretation_lines(generation),
        "",
        "Please return:",
        "1. A blunt performance critique.",
        "2. The most likely reason the planner variants failed.",
        "3. A ranked next-direction plan, with structural ideas first.",
        "4. What diagnostics or traces to collect before the next code edit.",
        "5. Which ideas risk overfitting or violating the audit protocol.",
    ]
    excerpt = _report_excerpt(report_path, context=context)
    if excerpt:
        lines.extend(["", "Full-context report excerpt:", excerpt])
    return "\n".join(lines).strip() + "\n"


def _default_runner(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout


def _command_output(command: list[str], *, runner: Runner | None = None) -> str:
    active_runner = runner or _default_runner
    return active_runner(command).strip()


def claude_version(*, cli: str = "claude", runner: Runner | None = None) -> str:
    """Return the Claude CLI version or a not-found marker."""

    if shutil.which(cli) is None and runner is None:
        return "not_found"
    try:
        return _command_output([cli, "--version"], runner=runner)
    except Exception as exc:  # pragma: no cover - defensive around local CLI variants
        return f"unavailable: {type(exc).__name__}: {exc}"


def invoke_claude(
    prompt: str,
    *,
    allow_external_claude: bool = False,
    cli: str = "claude",
    runner: Runner | None = None,
) -> str:
    """Invoke Claude only after an explicit external-send gate."""

    if not allow_external_claude:
        raise ValueError("refusing to send SlimeVolley evidence to Claude without --allow-external-claude")
    if shutil.which(cli) is None and runner is None:
        raise FileNotFoundError(f"Claude CLI not found: {cli}; install/configure it and verify with `claude --version`")
    return _command_output([cli, "-p", prompt], runner=runner)


def _summary_from_output(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return "\n".join(lines[:6]) if lines else "No Claude output captured."


def _action_items_from_output(output: str) -> str:
    selected = []
    for line in output.splitlines():
        lowered = line.lower()
        if any(keyword in lowered for keyword in ("next", "implement", "collect", "diagnostic", "try", "avoid")):
            selected.append(line.strip())
        if len(selected) >= 8:
            break
    return "\n".join(selected) if selected else "Review the raw Claude output and decide whether any recommendation merits a ledgered code/config/test change."


def render_critic_artifact(
    *,
    task: str,
    prompt: str,
    claude_output: str,
    metadata: dict[str, Any],
) -> str:
    """Render the reusable Claude critic artifact."""

    return "\n".join(
        [
            "# Claude SlimeVolley Critic",
            "",
            "## Original User Task",
            "",
            task,
            "",
            "## Metadata",
            "",
            "```json",
            json.dumps(metadata, indent=2, sort_keys=True),
            "```",
            "",
            "## Final Prompt Sent To Claude CLI",
            "",
            "```text",
            prompt.rstrip(),
            "```",
            "",
            "## Claude Output Raw",
            "",
            claude_output.rstrip() or "No Claude output captured.",
            "",
            "## Concise Summary",
            "",
            _summary_from_output(claude_output),
            "",
            "## Action Items / Next Steps",
            "",
            _action_items_from_output(claude_output),
            "",
            "## Audit Note",
            "",
            "This is an external advisory artifact. It is not policy evidence by itself; any subsequent code/config/test change must be ledgered separately.",
            "",
        ]
    )


def run_claude_critic(
    *,
    ledger_path: Path = DEFAULT_CRITIC_LEDGER,
    summary_path: Path = DEFAULT_CRITIC_SUMMARY,
    report_path: Path = DEFAULT_FINAL_REPORT,
    context: str = "sanitized",
    task: str = DEFAULT_TASK,
    allow_external_claude: bool = False,
    dry_run: bool = False,
    mock_output: str | None = None,
    cli: str = "claude",
    report_artifact_dir: Path = DEFAULT_CRITIC_REPORT_DIR,
    omx_artifact_dir: Path = DEFAULT_OMX_ARTIFACT_DIR,
    write_omx_artifact: bool = True,
    runner: Runner | None = None,
    timestamp: datetime | None = None,
) -> ClaudeCriticResult:
    """Build the prompt, optionally call Claude, and persist critic artifacts."""

    prompt = build_critic_prompt(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        context=context,
        task=task,
    )
    now = timestamp or datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    metadata = {
        "timestamp": now.isoformat(),
        "environment": SLIMEVOLLEY_ENV_ID,
        "context": context,
        "ledger_path": str(ledger_path),
        "summary_path": str(summary_path),
        "report_path": str(report_path),
        "critic_generation": _critic_generation_context(ledger_path).label,
        "ledger_sha256": _sha256_file(ledger_path),
        "summary_sha256": _sha256_file(summary_path),
        "report_sha256": _sha256_file(report_path),
        "claude_cli": cli,
        "claude_version": claude_version(cli=cli, runner=runner),
        "allow_external_claude": allow_external_claude,
        "dry_run": dry_run,
        "mock_output_used": mock_output is not None,
        "advisory_only": True,
    }
    if dry_run:
        return ClaudeCriticResult(
            prompt=prompt,
            claude_output="",
            report_artifact_path=None,
            omx_artifact_path=None,
            metadata=metadata,
        )
    claude_output = mock_output if mock_output is not None else invoke_claude(
        prompt,
        allow_external_claude=allow_external_claude,
        cli=cli,
        runner=runner,
    )
    artifact = render_critic_artifact(
        task=task,
        prompt=prompt,
        claude_output=claude_output,
        metadata=metadata,
    )
    filename = f"{CRITIC_FILENAME_PREFIX}-{stamp}.md"
    report_artifact_dir.mkdir(parents=True, exist_ok=True)
    report_path_out = report_artifact_dir / filename
    report_path_out.write_text(artifact, encoding="utf-8")
    omx_path_out: Path | None = None
    if write_omx_artifact:
        omx_artifact_dir.mkdir(parents=True, exist_ok=True)
        omx_path_out = omx_artifact_dir / filename
        omx_path_out.write_text(artifact, encoding="utf-8")
    return ClaudeCriticResult(
        prompt=prompt,
        claude_output=claude_output,
        report_artifact_path=report_path_out,
        omx_artifact_path=omx_path_out,
        metadata=metadata,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_CRITIC_LEDGER)
    parser.add_argument("--summary", type=Path, default=DEFAULT_CRITIC_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_FINAL_REPORT)
    parser.add_argument("--context", choices=["sanitized", "full"], default="sanitized")
    parser.add_argument("--task", default=DEFAULT_TASK)
    parser.add_argument("--allow-external-claude", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print the prompt and do not write artifacts or call Claude.")
    parser.add_argument("--mock-output", default=None, help="Use supplied text as Claude output; intended for tests and offline demos.")
    parser.add_argument("--cli", default="claude")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_CRITIC_REPORT_DIR)
    parser.add_argument("--omx-artifact-dir", type=Path, default=DEFAULT_OMX_ARTIFACT_DIR)
    parser.add_argument("--no-omx-artifact", action="store_true")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    result = run_claude_critic(
        ledger_path=args.ledger,
        summary_path=args.summary,
        report_path=args.report,
        context=args.context,
        task=args.task,
        allow_external_claude=args.allow_external_claude,
        dry_run=args.dry_run,
        mock_output=args.mock_output,
        cli=args.cli,
        report_artifact_dir=args.output_dir,
        omx_artifact_dir=args.omx_artifact_dir,
        write_omx_artifact=not args.no_omx_artifact,
    )
    if args.format == "json":
        print(json.dumps({
            "prompt": result.prompt if args.dry_run else None,
            "report_artifact_path": str(result.report_artifact_path) if result.report_artifact_path else None,
            "omx_artifact_path": str(result.omx_artifact_path) if result.omx_artifact_path else None,
            "metadata": result.metadata,
        }, indent=2, sort_keys=True))
        return
    if args.dry_run:
        print(result.prompt, end="")
    else:
        print(f"Claude critic artifact: {result.report_artifact_path}")
        if result.omx_artifact_path:
            print(f"OMX artifact copy: {result.omx_artifact_path}")


if __name__ == "__main__":
    main()
