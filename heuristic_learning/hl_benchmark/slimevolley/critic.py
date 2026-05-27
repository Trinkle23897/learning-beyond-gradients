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
DEFAULT_FINAL_REPORT = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "final_report.md"
DEFAULT_CRITIC_REPORT_DIR = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "critic"
DEFAULT_OMX_ARTIFACT_DIR = PROJECT_ROOT / ".omx" / "artifacts"
DEFAULT_JOINT_ATTACK_SEARCH_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_4_joint_attack_scalar_search_attempt.md"
DEFAULT_LOW_RECEIVE_FOLLOWUP_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_4_low_receive_teacher_scalar_followup.md"
DEFAULT_RALLY_SERVE_NOTE = env_results_dir(SLIMEVOLLEY_ENV_ID).parent / "notes" / "generation_4_rally_serve_candidate.md"
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
        ("improved", "builtin"),
        ("improved-tuned", "builtin"),
        ("attack", "builtin"),
        ("rally-serve", "builtin"),
        ("temporal", "builtin"),
        ("planner", "builtin"),
        ("teacher-assisted", "builtin"),
        ("baseline-rnn", "builtin"),
        ("improved", "random"),
        ("improved", "initial"),
        ("improved", "improved-v3"),
        ("improved", "improved-v4"),
        ("improved", "improved-v5"),
        ("improved", "improved-v6"),
        ("improved-tuned", "improved-v5"),
        ("improved-tuned", "improved-v6"),
        ("attack", "improved-v5"),
        ("attack", "improved-v6"),
        ("rally-serve", "improved-v5"),
        ("rally-serve", "improved-v6"),
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
    headings = ["## Generation-4 Development Attempt", "## Neural/RL Comparator", "## Current Conclusion", "## Next Steps"]
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
    ledger_path: Path = DEFAULT_GENERATION4_LEDGER,
    summary_path: Path = DEFAULT_GENERATION4_SUMMARY,
    report_path: Path = DEFAULT_FINAL_REPORT,
    context: str = "sanitized",
    task: str = DEFAULT_TASK,
) -> str:
    """Build the prompt sent to Claude without using holdout rows as tuning context."""

    entries = read_entries(ledger_path) if ledger_path.exists() else []
    dev_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") == "dev"]
    sealed_entries = [entry for entry in entries if entry.get("seed_range", {}).get("split") in {"holdout", "audit"}]
    lines = [
        "You are an external critic for a transparent SlimeVolley heuristic-learning experiment.",
        "Your job is to critique current development performance and propose auditable next directions.",
        "Do not ask to tune on holdout or audit seeds. Do not propose hidden neural runtime policies as the maintained heuristic.",
        "Separate structural heuristic ideas from scalar/config tuning and from teacher-assisted rule discovery.",
        "",
        f"Task: {task}",
        "",
        "Current generation-4 guardrails:",
        "- Development seeds: 9000..9049.",
        "- Holdout seeds: 10000..10049; consumed for final-only evaluation and unavailable for tuning.",
        "- Audit seeds: 11000..11049; reserved for independent checks and not available for tuning.",
        f"- Selected ledger path: {ledger_path}",
        f"- Selected summary path: {summary_path}",
        f"- Sealed holdout/audit rows in this selected ledger (consumed final holdout or reserved audit): {len(sealed_entries)}; these rows are excluded from next-direction development context.",
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
        "- The current maintained `improved` heuristic remains stronger than `planner` and `teacher-assisted` against the built-in opponent on development seeds.",
        "- `improved-tuned` is a scalar/config baseline: it improves built-in development score but remains below `baseline-rnn` and is not structural improvement evidence.",
        "- The `attack` candidate is a structural partial: it improves built-in development score but remains below `baseline-rnn` and regresses nearest archived opponents, so it is not promoted.",
        "- A follow-up scalar search around `attack` found a built-in-only development candidate at mean `-0.10`, still below `baseline-rnn` mean `0.12` and worse or tied against all non-built-in opponents; it is not promoted.",
        "- A later parallel scalar/config search found a stronger built-in-only candidate at mean `-0.02` with `low_ball_rescue_x_window=0.48`; it still trails `baseline-rnn` mean `0.12`, is scalar-only, and is not promoted.",
        "- A low-receive teacher-action follow-up found RNN jump signals in low own-side loss windows, but targeted `LowDriveFinish` and `NetVerticalBlock` structural probes tied or worsened the short screen; a bounded 98-config scalar follow-up again topped out at mean `-0.02` and is not promoted.",
        "- The `rally-serve` candidate adds a point-reset serve detector plus scalar fields; it beat `baseline-rnn` on built-in development seeds (`0.14` vs `0.12`) but failed to beat it on final-only built-in holdout (`-0.22` vs `-0.12`). Do not propose tuning from this holdout outcome; any new policy-selection work needs a fresh predeclared generation.",
        "- The latest parallel rally-serve pass found no new promotion: scalar/config variants, stacked grounded-low-receive probes, and stacked rear-wall probes only tied or regressed versus current `rally-serve`; minimum recorded new dev cost was `6,540,000` environment steps.",
        "- Trace diagnostics show `rally-serve` improves over `attack` by reducing point losses from `32` to `18`, but it wins fewer built-in matches than `baseline-rnn` (`13` versus `18`) and relies more on draws (`29` versus `20`).",
        f"- Joint scalar-search note, if present: `{DEFAULT_JOINT_ATTACK_SEARCH_NOTE}`.",
        f"- Low-receive teacher/scalar follow-up note, if present: `{DEFAULT_LOW_RECEIVE_FOLLOWUP_NOTE}`.",
        f"- Rally-serve candidate note, if present: `{DEFAULT_RALLY_SERVE_NOTE}`.",
        f"- Parallel synthesis report, if present: `{DEFAULT_PARALLEL_SYNTHESIS_REPORT}`.",
        f"- Parallel trace report, if present: `{DEFAULT_PARALLEL_TRACE_REPORT}`.",
        "- The planner variants should not be promoted without new evidence; their failed rows remain append-only evidence.",
        "- The packaged `baseline-rnn` is a comparator/possible teacher for dev-only rule discovery, not a runtime maintained heuristic.",
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
    ledger_path: Path = DEFAULT_GENERATION4_LEDGER,
    summary_path: Path = DEFAULT_GENERATION4_SUMMARY,
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
    parser.add_argument("--ledger", type=Path, default=DEFAULT_GENERATION4_LEDGER)
    parser.add_argument("--summary", type=Path, default=DEFAULT_GENERATION4_SUMMARY)
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
