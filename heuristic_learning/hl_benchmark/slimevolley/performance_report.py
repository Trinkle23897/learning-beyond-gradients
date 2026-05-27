"""Generate a SlimeVolley performance deep-dive from persisted artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_ledger_path, env_reports_dir, env_results_dir
from hl_benchmark.ledger import read_entries
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID


DEFAULT_PERFORMANCE_REPORT_PATH = (
    env_reports_dir(SLIMEVOLLEY_ENV_ID) / "performance_deepdive.md"
)

PERFORMANCE_REPORT_SECTIONS = (
    "## Status",
    "## Evidence Sources",
    "## Holdout Matrix",
    "## Generation-2 Final Evidence",
    "## Generation-3 Evidence",
    "## Headline Comparisons",
    "## Built-In Opponent Gap",
    "## Opponent-Pool Robustness",
    "## Development Round-Robin",
    "## Scalar Search Context",
    "## Cost Context",
    "## Interpretation",
    "## Next Performance Step",
)

POLICY_ORDER = {
    "random": 0,
    "initial": 1,
    "tuned": 2,
    "improved-v0": 3,
    "improved-v1": 4,
    "improved-v2": 5,
    "improved-v3": 6,
    "improved": 7,
    "baseline-rnn": 8,
}
OPPONENT_ORDER = {
    "builtin": 0,
    "random": 1,
    "initial": 2,
    "improved-v0": 3,
    "improved-v1": 4,
    "improved-v2": 5,
    "improved-v3": 6,
    "improved": 7,
}


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


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _sum_numeric(entries: list[dict[str, Any]], key: str) -> float:
    total = 0.0
    for entry in entries:
        value = entry.get(key)
        if isinstance(value, (int, float)):
            total += float(value)
    return total


def _cell_mean(cell: dict[str, Any] | None) -> float | None:
    if cell is None:
        return None
    value = cell.get("mean")
    return float(value) if isinstance(value, (int, float)) else None


def _cell_key(cell: dict[str, Any]) -> tuple[int, str, int, str]:
    policy = str(cell.get("policy", ""))
    opponent = str(cell.get("opponent", ""))
    return (
        POLICY_ORDER.get(policy, 1000),
        policy,
        OPPONENT_ORDER.get(opponent, 1000),
        opponent,
    )


def _cells_by_key(payload: dict[str, Any] | None) -> dict[tuple[str, str], dict[str, Any]]:
    if not payload:
        return {}
    cells = payload.get("cells")
    if not isinstance(cells, list):
        return {}
    return {
        (str(cell.get("policy")), str(cell.get("opponent"))): cell
        for cell in cells
        if isinstance(cell, dict)
    }


def _score_bar(value: Any, *, scale: float = 5.0, width: int = 20) -> str:
    if not isinstance(value, (int, float)):
        return ""
    clipped = max(-scale, min(scale, float(value)))
    center = width // 2
    magnitude = int(round(abs(clipped) / scale * center))
    cells = ["."] * width
    cells[center] = "|"
    if clipped > 0:
        for index in range(center + 1, min(width, center + 1 + magnitude)):
            cells[index] = "+"
    elif clipped < 0:
        for index in range(max(0, center - magnitude), center):
            cells[index] = "-"
    return "`" + "".join(cells) + "`"


def _delta_rows(
    cells: dict[tuple[str, str], dict[str, Any]],
    *,
    candidate: str,
    reference: str,
    exclude_builtin: bool = False,
) -> list[tuple[str, float, float, float]]:
    opponents = {
        opponent
        for policy, opponent in cells
        if policy in {candidate, reference}
    }
    rows: list[tuple[str, float, float, float]] = []
    for opponent in sorted(opponents, key=lambda name: (OPPONENT_ORDER.get(name, 1000), name)):
        if exclude_builtin and opponent == "builtin":
            continue
        candidate_mean = _cell_mean(cells.get((candidate, opponent)))
        reference_mean = _cell_mean(cells.get((reference, opponent)))
        if candidate_mean is None or reference_mean is None:
            continue
        rows.append((opponent, candidate_mean, reference_mean, candidate_mean - reference_mean))
    return rows


def _comparison_summary_lines(
    cells: dict[tuple[str, str], dict[str, Any]],
    *,
    candidate: str,
    reference: str,
    label: str,
    exclude_builtin: bool = False,
) -> list[str]:
    rows = _delta_rows(
        cells,
        candidate=candidate,
        reference=reference,
        exclude_builtin=exclude_builtin,
    )
    if not rows:
        return [f"- `{label}`: no common holdout opponents are available."]
    better = sum(1 for _opponent, _candidate, _reference, delta in rows if delta > 0)
    worse = sum(1 for _opponent, _candidate, _reference, delta in rows if delta < 0)
    tied = len(rows) - better - worse
    avg_delta = _mean([delta for _opponent, _candidate, _reference, delta in rows])
    lines = [
        f"- `{label}`: {better} better, {worse} worse, {tied} tied over {len(rows)} common holdout opponents; mean delta `{_stats(avg_delta)}`."
    ]
    lines.extend(
        [
            "",
            "| Opponent | Candidate mean | Reference mean | Delta |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for opponent, candidate_mean, reference_mean, delta in rows:
        lines.append(
            f"| {opponent} | {_stats(candidate_mean)} | {_stats(reference_mean)} | {_stats(delta)} |"
        )
    return lines


def _holdout_matrix_lines(
    payload: dict[str, Any] | None,
    *,
    artifact_label: str = "holdout_final.json",
) -> list[str]:
    if not payload:
        return [f"No `{artifact_label}` artifact is available yet."]
    cells = [cell for cell in payload.get("cells", []) if isinstance(cell, dict)]
    lines = [
        f"Artifact: `{artifact_label}`. Split: `{payload.get('split', '')}`. Matchups: `{payload.get('matchup_count', '')}`. Episodes per matchup: `{payload.get('episodes_per_matchup', '')}`.",
        "",
        "| Policy | Opponent | Mean | Win rate | Wins | Losses | Draws | Episodes | Steps | Score bar |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for cell in sorted(cells, key=_cell_key):
        lines.append(
            "| {policy} | {opponent} | {mean} | {win_rate} | {wins} | {losses} | {draws} | {episodes} | {steps} | {bar} |".format(
                policy=cell.get("policy", ""),
                opponent=cell.get("opponent", ""),
                mean=_stats(cell.get("mean")),
                win_rate=_stats(cell.get("win_rate")),
                wins=cell.get("wins", ""),
                losses=cell.get("losses", ""),
                draws=cell.get("draws", ""),
                episodes=cell.get("episodes", ""),
                steps=cell.get("environment_steps", ""),
                bar=_score_bar(cell.get("mean")),
            )
        )
    return lines


def _headline_comparison_lines(payload: dict[str, Any] | None) -> list[str]:
    cells = _cells_by_key(payload)
    if not cells:
        return ["No holdout cells are available for headline comparisons."]
    lines: list[str] = []
    lines.extend(
        _comparison_summary_lines(
            cells,
            candidate="improved",
            reference="initial",
            label="improved vs initial",
        )
    )
    lines.append("")
    lines.extend(
        _comparison_summary_lines(
            cells,
            candidate="improved",
            reference="tuned",
            label="improved vs tuned scalar baseline",
        )
    )
    baseline_builtin = cells.get(("baseline-rnn", "builtin"))
    improved_builtin = cells.get(("improved", "builtin"))
    if baseline_builtin and improved_builtin:
        gap = _cell_mean(baseline_builtin) - _cell_mean(improved_builtin)  # type: ignore[operator]
        lines.extend(
            [
                "",
                f"- `baseline-rnn` vs `improved` on built-in holdout: mean gap `{_stats(gap)}` in favor of the packaged RNN comparator.",
            ]
        )
    return lines


def _builtin_gap_lines(payload: dict[str, Any] | None) -> list[str]:
    cells = _cells_by_key(payload)
    if not cells:
        return ["No holdout cells are available for the built-in opponent gap."]
    lines = [
        "The built-in opponent is the hardest recorded opponent and is the clearest place where the heuristic system is not deep-RL comparable.",
        "",
        "| Policy | Mean | Wins | Losses | Draws | Win rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy in ["random", "initial", "tuned", "improved", "baseline-rnn"]:
        cell = cells.get((policy, "builtin"))
        if not cell:
            continue
        lines.append(
            "| {policy} | {mean} | {wins} | {losses} | {draws} | {win_rate} |".format(
                policy=policy,
                mean=_stats(cell.get("mean")),
                wins=cell.get("wins", ""),
                losses=cell.get("losses", ""),
                draws=cell.get("draws", ""),
                win_rate=_stats(cell.get("win_rate")),
            )
        )
    improved = cells.get(("improved", "builtin"))
    baseline = cells.get(("baseline-rnn", "builtin"))
    if improved and baseline:
        lines.append("")
        lines.append(
            f"`improved` recorded `{improved.get('wins', '')}` wins in `{improved.get('episodes', '')}` holdout built-in episodes; `baseline-rnn` recorded `{baseline.get('wins', '')}` wins and `{baseline.get('draws', '')}` draws."
        )
    return lines


def _opponent_pool_lines(payload: dict[str, Any] | None) -> list[str]:
    cells = _cells_by_key(payload)
    if not cells:
        return ["No holdout cells are available for opponent-pool robustness."]
    lines = [
        "This view excludes the built-in opponent and asks whether the maintained heuristic became broadly stronger against random and archived heuristic opponents.",
        "",
    ]
    lines.extend(
        _comparison_summary_lines(
            cells,
            candidate="improved",
            reference="initial",
            label="non-built-in improved vs initial",
            exclude_builtin=True,
        )
    )
    lines.append("")
    lines.extend(
        _comparison_summary_lines(
            cells,
            candidate="improved",
            reference="tuned",
            label="non-built-in improved vs tuned",
            exclude_builtin=True,
        )
    )
    return lines


def _generation_2_final_evidence_lines(
    *,
    generation_ledger_path: Path,
    generation_holdout_path: Path,
    generation_tournament_path: Path,
    generation_search_best_path: Path,
) -> list[str]:
    """Render generation-2 evidence beside the original holdout run."""

    lines = [
        "Generation-2 is the fresh-seed follow-up after the original holdout was consumed.",
        "Generation-2 holdout, when present, is final-only and must not be used for further policy, scalar-config, or opponent-pool tuning.",
        f"- Generation-2 ledger: `{generation_ledger_path}`",
        f"- Generation-2 holdout: `{generation_holdout_path}`",
        f"- Generation-2 tournament: `{generation_tournament_path}`",
        f"- Generation-2 scalar search: `{generation_search_best_path}`",
    ]

    if generation_ledger_path.exists():
        entries = read_entries(generation_ledger_path)
        split_counts = Counter(str(entry.get("seed_range", {}).get("split", "unknown")) for entry in entries)
        lines.extend(
            [
                f"- Generation-2 ledger rows: `{len(entries)}`",
                f"- Generation-2 split counts: `{dict(sorted(split_counts.items()))}`",
            ]
        )
    else:
        lines.append("- Generation-2 ledger rows: `0` because the ledger is not present.")

    payload = _read_json(generation_holdout_path)
    if not payload:
        lines.extend(
            [
                "",
                "No generation-2 final holdout matrix is available yet. If policy work continues, keep holdout uninspected until the next generation is frozen.",
            ]
        )
        return lines

    seed_start = payload.get("seed_start")
    episodes_per_matchup = payload.get("episodes_per_matchup")
    if isinstance(seed_start, int) and isinstance(episodes_per_matchup, int):
        lines.append(f"- Generation-2 holdout seeds: `{seed_start}..{seed_start + episodes_per_matchup - 1}`")
    lines.extend(["", *_holdout_matrix_lines(payload, artifact_label="holdout_g2_final.json")])

    cells = _cells_by_key(payload)
    improved_builtin = cells.get(("improved", "builtin"))
    baseline_builtin = cells.get(("baseline-rnn", "builtin"))
    if improved_builtin and baseline_builtin:
        lines.extend(
            [
                "",
                "Generation-2 built-in-opponent headline: `improved` mean `{heuristic}` with `{heuristic_wins}` wins, while `baseline-rnn` mean `{baseline}` with `{baseline_wins}` wins and `{baseline_draws}` draws.".format(
                    heuristic=_stats(improved_builtin.get("mean")),
                    heuristic_wins=improved_builtin.get("wins", ""),
                    baseline=_stats(baseline_builtin.get("mean")),
                    baseline_wins=baseline_builtin.get("wins", ""),
                    baseline_draws=baseline_builtin.get("draws", ""),
                ),
            ]
        )
    return lines


def _entry_seed_label(entry: dict[str, Any]) -> str:
    seed_range = entry.get("seed_range", {})
    start = seed_range.get("start")
    stop_exclusive = seed_range.get("stop_exclusive")
    if isinstance(start, int) and isinstance(stop_exclusive, int):
        return f"{start}..{stop_exclusive - 1}"
    return ""


def _generation_3_development_lines(
    *,
    generation3_ledger_path: Path,
    generation3_holdout_path: Path,
    generation3_tournament_path: Path,
    generation3_search_best_path: Path,
) -> list[str]:
    """Render generation-3 evidence while preserving the holdout anti-tuning boundary."""

    holdout_present = generation3_holdout_path.exists()
    if holdout_present:
        status_line = (
            "Generation-3 now includes final-only holdout evidence from the frozen policy/config/opponent/test state. "
            "It must not be used for subsequent tuning."
        )
    else:
        status_line = (
            "Generation-3 development evidence is not holdout evidence. It is safe to inspect for diagnosis, "
            "but `holdout_g3_final.json` remains final-only until the policy, scalar config, opponent pool, and tests are frozen."
        )
    lines = [
        status_line,
        f"- Generation-3 ledger: `{generation3_ledger_path}`",
        f"- Generation-3 scalar search: `{generation3_search_best_path}`",
        f"- Generation-3 tournament: `{generation3_tournament_path}`",
        f"- Generation-3 holdout: `{generation3_holdout_path}`",
    ]

    entries = read_entries(generation3_ledger_path) if generation3_ledger_path.exists() else []
    if not entries:
        lines.extend(
            [
                "- Generation-3 ledger rows: `0` because the ledger is not present or has no rows.",
                "- No generation-3 development performance row is available yet.",
            ]
        )
    else:
        split_counts = Counter(str(entry.get("seed_range", {}).get("split", "unknown")) for entry in entries)
        pass_fail_counts = Counter(str(entry.get("pass_fail", "unknown")) for entry in entries)
        holdout_rows = [
            entry for entry in entries
            if entry.get("seed_range", {}).get("split") == "holdout"
        ]
        lines.extend(
            [
                f"- Generation-3 ledger rows: `{len(entries)}`",
                f"- Generation-3 split counts: `{dict(sorted(split_counts.items()))}`",
                f"- Generation-3 pass/fail counts: `{dict(sorted(pass_fail_counts.items()))}`",
                f"- Generation-3 holdout rows: `{len(holdout_rows)}`",
                "",
                "| Timestamp | Split | Seeds | Policy | Opponent | Pass/fail | Episodes | Steps | Mean | W/L/D |",
                "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for entry in entries[-8:]:
            wld = entry.get("win_loss_draw", {})
            score_stats = entry.get("score_stats", {})
            lines.append(
                "| {timestamp} | {split} | {seeds} | {policy} | {opponent} | {pass_fail} | {episodes} | {steps} | {mean} | {wins}/{losses}/{draws} |".format(
                    timestamp=entry.get("timestamp", ""),
                    split=entry.get("seed_range", {}).get("split", ""),
                    seeds=_entry_seed_label(entry),
                    policy=entry.get("policy_version", ""),
                    opponent=entry.get("opponent_name", ""),
                    pass_fail=entry.get("pass_fail", ""),
                    episodes=entry.get("episodes", ""),
                    steps=entry.get("environment_steps", ""),
                    mean=_stats(score_stats.get("mean")),
                    wins=wld.get("wins", ""),
                    losses=wld.get("losses", ""),
                    draws=wld.get("draws", ""),
                )
            )

    if generation3_search_best_path.exists():
        lines.append("- Generation-3 scalar-search artifact is present.")
    else:
        lines.append("- Generation-3 scalar-search artifact is not present yet; do not compare generation-3 against scalar tuning until it exists.")
    if generation3_tournament_path.exists():
        lines.append("- Generation-3 round-robin tournament artifact is present.")
    else:
        lines.append("- Generation-3 round-robin tournament artifact is not present yet; opponent-pool robustness remains generation-2 evidence only.")
    if generation3_holdout_path.exists():
        lines.append("- Generation-3 holdout artifact is present and final-only; do not use it for subsequent tuning.")
    else:
        lines.append("- Generation-3 holdout artifact is missing, so the generation-3 holdout remains unopened in the current evidence set.")
    return lines


def _tournament_lines(payload: dict[str, Any] | None) -> list[str]:
    if not payload:
        return ["No `round_robin_dev.json` artifact is available yet."]
    lines = [
        f"Development tournament split: `{payload.get('split', '')}`. Participants: `{', '.join(payload.get('participants', []))}`. Matchups: `{payload.get('matchup_count', '')}`.",
        "",
        "| Rank | Policy | Mean score across opponents | Win rate | Wins | Losses | Draws | Steps |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(payload.get("standings", []), start=1):
        if not isinstance(row, dict):
            continue
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
    lines.append("")
    lines.append(
        "The tournament is development evidence only; it is useful for diagnosing exploitability against archived policies, not for final holdout tuning."
    )
    return lines


def _scalar_search_lines(payload: dict[str, Any] | None) -> list[str]:
    if not payload:
        return ["No `search_best_dev.json` artifact is available yet."]
    means = payload.get("opponent_means", {})
    rendered_means = ", ".join(
        f"{name}={_stats(value)}" for name, value in sorted(means.items())
    ) if isinstance(means, dict) else ""
    return [
        "Scalar/config search is a separate baseline, not a structural heuristic-improvement claim.",
        "",
        f"- Split: `{payload.get('split', '')}`",
        f"- Candidate budget: `{payload.get('candidate_count', '')}`",
        f"- Selected candidate index: `{payload.get('candidate_index', '')}`",
        f"- Selection score: `{_stats(payload.get('selection_score'))}`",
        f"- Opponents: `{', '.join(payload.get('opponents', []))}`",
        f"- Config: `{json.dumps(payload.get('config', {}), sort_keys=True)}`",
        f"- Opponent means: `{rendered_means}`",
    ]


def _cost_lines(
    entries: list[dict[str, Any]],
    *,
    generation_entries: list[dict[str, Any]] | None = None,
    generation3_entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    generation_entries = generation_entries or []
    generation3_entries = generation3_entries or []
    all_entries = [*entries, *generation_entries, *generation3_entries]
    if not all_entries:
        return ["No ledger rows are available for cost context."]
    split_counts = Counter(str(entry.get("seed_range", {}).get("split", "")) for entry in entries)
    generation_split_counts = Counter(
        str(entry.get("seed_range", {}).get("split", "")) for entry in generation_entries
    )
    generation3_split_counts = Counter(
        str(entry.get("seed_range", {}).get("split", "")) for entry in generation3_entries
    )
    change_type_counts = Counter(str(entry.get("change_type", "")) for entry in all_entries)
    scalar_entries = [entry for entry in all_entries if entry.get("change_type") == "scalar/config tuning"]
    structural_entries = [
        entry for entry in all_entries
        if entry.get("change_type") == "structural policy improvement"
    ]
    return [
        "This cost context distinguishes environment samples from the coding-agent maintenance process and includes generation-2 and generation-3 rows when present.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Generation-1 ledger rows | {len(entries)} |",
        f"| Generation-2 ledger rows | {len(generation_entries)} |",
        f"| Generation-3 ledger rows | {len(generation3_entries)} |",
        f"| Total ledger rows | {len(all_entries)} |",
        f"| Total episodes | {int(_sum_numeric(all_entries, 'episodes'))} |",
        f"| Total environment steps | {int(_sum_numeric(all_entries, 'environment_steps'))} |",
        f"| Total wall-clock seconds | {_stats(_sum_numeric(all_entries, 'wall_clock_seconds'))} |",
        f"| Structural-improvement rows | {len(structural_entries)} |",
        f"| Scalar-search rows | {len(scalar_entries)} |",
        f"| Scalar-search episodes | {int(_sum_numeric(scalar_entries, 'episodes'))} |",
        "",
        f"- Generation-1 rows by split: `{dict(sorted(split_counts.items()))}`",
        f"- Generation-2 rows by split: `{dict(sorted(generation_split_counts.items()))}`",
        f"- Generation-3 rows by split: `{dict(sorted(generation3_split_counts.items()))}`",
        f"- Rows by change type across all performance ledgers: `{dict(sorted(change_type_counts.items()))}`",
        "- LLM call/token accounting remains limited to what the ledger captured; unavailable values are preserved rather than inferred.",
    ]


def _interpretation_lines(holdout_payload: dict[str, Any] | None) -> list[str]:
    cells = _cells_by_key(holdout_payload)
    improved_builtin = cells.get(("improved", "builtin"))
    baseline_builtin = cells.get(("baseline-rnn", "builtin"))
    lines = [
        "The current SlimeVolley evidence is weak or mixed support for the Learning Beyond Gradients hypothesis.",
        "",
        "Short verdict: not deep-RL comparable.",
        "",
        "Supported: the agent-maintained heuristic improved over the initial handwritten policy and scalar-tuned baseline across the non-built-in holdout opponent pool while preserving archived policies for regression and opponent-pool checks.",
        "",
        "Weakened: the same heuristic still failed the built-in opponent and remains far behind the packaged `baseline-rnn` comparator, so it should not be described as performing similarly to deep RL on this testbed.",
    ]
    if improved_builtin and baseline_builtin:
        lines.append("")
        lines.append(
            "Concrete built-in evidence: `improved` mean `{heuristic}` with `{heuristic_wins}` wins; `baseline-rnn` mean `{baseline}` with `{baseline_wins}` wins and `{baseline_draws}` draws.".format(
                heuristic=_stats(improved_builtin.get("mean")),
                heuristic_wins=improved_builtin.get("wins", ""),
                baseline=_stats(baseline_builtin.get("mean")),
                baseline_wins=baseline_builtin.get("wins", ""),
                baseline_draws=baseline_builtin.get("draws", ""),
            )
        )
    return lines


def _next_step_lines(*, generation_2_holdout_present: bool, generation_3_holdout_present: bool) -> list[str]:
    if generation_3_holdout_present:
        return [
            "Do not tune on the already-used holdout seeds in `holdout_final.json`, `holdout_g2_final.json`, or `holdout_g3_final.json`.",
            "",
            "Recommended next performance step: treat the current SlimeVolley generation as closed for policy selection. Further SlimeVolley work needs a fresh generation-4 protocol with new development, holdout, and audit seeds, or a move to another environment adapter.",
        ]
    if generation_2_holdout_present:
        return [
            "Do not tune on the already-used holdout seeds in `holdout_final.json` or `holdout_g2_final.json`.",
            "",
            "Recommended next performance step: use the predeclared generation-3 protocol, inspect only generation-3 development traces, complete the generation-3 scalar-search and round-robin artifacts, and keep `holdout_g3_final.json` unopened until policy code, scalar config, opponent pool, and tests are frozen.",
        ]
    return [
        "Do not tune on the already-used holdout seeds in `holdout_final.json`.",
        "",
        "Recommended next performance step: use the audited `configs/generation_2_protocol.json` and `reports/generation_2_protocol.md` artifacts, then diagnose the built-in-opponent losses from generation-2 development traces only. A credible structural attempt would target serve/return timing or high-arc defense, keep archived opponents frozen, run `make slimevolley-verify`, and evaluate against the full development opponent pool before any new holdout is opened; once generation-2 holdout is consumed, move to a generation-3 protocol for further policy work.",
    ]


def render_slimevolley_performance_report(
    *,
    ledger_path: Path = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    holdout_path: Path | None = None,
    tournament_path: Path | None = None,
    search_best_path: Path | None = None,
    generation_ledger_path: Path | None = None,
    generation_holdout_path: Path | None = None,
    generation_tournament_path: Path | None = None,
    generation_search_best_path: Path | None = None,
    generation3_ledger_path: Path | None = None,
    generation3_holdout_path: Path | None = None,
    generation3_tournament_path: Path | None = None,
    generation3_search_best_path: Path | None = None,
) -> str:
    """Return a performance-focused report from existing SlimeVolley artifacts."""

    if holdout_path is None:
        holdout_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json"
    if tournament_path is None:
        tournament_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_dev.json"
    if search_best_path is None:
        search_best_path = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json"
    if generation_ledger_path is None:
        generation_ledger_path = ledger_path.with_name("generation_2_trials.jsonl")
    if generation_holdout_path is None:
        generation_holdout_path = ledger_path.with_name("holdout_g2_final.json")
    if generation_tournament_path is None:
        generation_tournament_path = ledger_path.with_name("round_robin_g2_dev.json")
    if generation_search_best_path is None:
        generation_search_best_path = ledger_path.with_name("search_best_g2_dev.json")
    if generation3_ledger_path is None:
        generation3_ledger_path = ledger_path.with_name("generation_3_trials.jsonl")
    if generation3_holdout_path is None:
        generation3_holdout_path = ledger_path.with_name("holdout_g3_final.json")
    if generation3_tournament_path is None:
        generation3_tournament_path = ledger_path.with_name("round_robin_g3_dev.json")
    if generation3_search_best_path is None:
        generation3_search_best_path = ledger_path.with_name("search_best_g3_dev.json")

    entries = read_entries(ledger_path) if ledger_path.exists() else []
    holdout_payload = _read_json(holdout_path)
    generation_entries = read_entries(generation_ledger_path) if generation_ledger_path.exists() else []
    generation3_entries = read_entries(generation3_ledger_path) if generation3_ledger_path.exists() else []
    generation_holdout_payload = _read_json(generation_holdout_path)
    generation3_holdout_payload = _read_json(generation3_holdout_path)
    primary_holdout_payload = generation3_holdout_payload or generation_holdout_payload or holdout_payload
    if generation3_holdout_payload:
        primary_holdout_label = "holdout_g3_final.json"
    elif generation_holdout_payload:
        primary_holdout_label = "holdout_g2_final.json"
    else:
        primary_holdout_label = "holdout_final.json"
    tournament_payload = _read_json(tournament_path)
    search_best_payload = _read_json(search_best_path)

    sections: list[tuple[str, list[str]]] = [
        (
            "## Status",
            [
                "This report is generated from existing artifacts only. It does not run evaluation, scalar search, tournaments, or holdout evaluation.",
                "",
                "Holdout evidence in `holdout_final.json`, `holdout_g2_final.json`, and `holdout_g3_final.json` is final-only when present; do not use it for policy tuning.",
            ],
        ),
        (
            "## Evidence Sources",
            [
                f"- Ledger: `{ledger_path}`",
                f"- Original holdout matrix: `{holdout_path}`",
                f"- Generation-2 holdout matrix: `{generation_holdout_path}`",
                f"- Development round-robin: `{tournament_path}`",
                f"- Generation-2 round-robin: `{generation_tournament_path}`",
                f"- Scalar-search selection: `{search_best_path}`",
                f"- Generation-2 scalar-search selection: `{generation_search_best_path}`",
                f"- Generation-3 ledger: `{generation3_ledger_path}`",
                f"- Generation-3 holdout matrix: `{generation3_holdout_path}`",
                f"- Generation-3 round-robin: `{generation3_tournament_path}`",
                f"- Generation-3 scalar-search selection: `{generation3_search_best_path}`",
                "- Compared policy labels include `initial`, `tuned`, `improved`, and `baseline-rnn`.",
            ],
        ),
        ("## Holdout Matrix", _holdout_matrix_lines(primary_holdout_payload, artifact_label=primary_holdout_label)),
        (
            "## Generation-2 Final Evidence",
            _generation_2_final_evidence_lines(
                generation_ledger_path=generation_ledger_path,
                generation_holdout_path=generation_holdout_path,
                generation_tournament_path=generation_tournament_path,
                generation_search_best_path=generation_search_best_path,
            ),
        ),
        (
            "## Generation-3 Evidence",
            _generation_3_development_lines(
                generation3_ledger_path=generation3_ledger_path,
                generation3_holdout_path=generation3_holdout_path,
                generation3_tournament_path=generation3_tournament_path,
                generation3_search_best_path=generation3_search_best_path,
            ),
        ),
        ("## Headline Comparisons", _headline_comparison_lines(primary_holdout_payload)),
        ("## Built-In Opponent Gap", _builtin_gap_lines(primary_holdout_payload)),
        ("## Opponent-Pool Robustness", _opponent_pool_lines(primary_holdout_payload)),
        ("## Development Round-Robin", _tournament_lines(tournament_payload)),
        ("## Scalar Search Context", _scalar_search_lines(search_best_payload)),
        (
            "## Cost Context",
            _cost_lines(
                entries,
                generation_entries=generation_entries,
                generation3_entries=generation3_entries,
            ),
        ),
        ("## Interpretation", _interpretation_lines(primary_holdout_payload)),
        (
            "## Next Performance Step",
            _next_step_lines(
                generation_2_holdout_present=generation_holdout_payload is not None,
                generation_3_holdout_present=generation3_holdout_payload is not None,
            ),
        ),
    ]

    lines = [
        "# SlimeVolley Performance Deep Dive",
        "",
        "A reviewer-oriented explanation of what the current SlimeVolley scores do and do not show.",
    ]
    for heading, body in sections:
        lines.extend(["", heading, "", *body])
    return "\n".join(lines).rstrip() + "\n"


def write_slimevolley_performance_report(
    *,
    output_path: Path = DEFAULT_PERFORMANCE_REPORT_PATH,
    ledger_path: Path = env_ledger_path(SLIMEVOLLEY_ENV_ID),
    holdout_path: Path | None = None,
    tournament_path: Path | None = None,
    search_best_path: Path | None = None,
    generation_ledger_path: Path | None = None,
    generation_holdout_path: Path | None = None,
    generation_tournament_path: Path | None = None,
    generation_search_best_path: Path | None = None,
    generation3_ledger_path: Path | None = None,
    generation3_holdout_path: Path | None = None,
    generation3_tournament_path: Path | None = None,
    generation3_search_best_path: Path | None = None,
) -> Path:
    """Write the generated performance deep-dive report and return its path."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_slimevolley_performance_report(
            ledger_path=ledger_path,
            holdout_path=holdout_path,
            tournament_path=tournament_path,
            search_best_path=search_best_path,
            generation_ledger_path=generation_ledger_path,
            generation_holdout_path=generation_holdout_path,
            generation_tournament_path=generation_tournament_path,
            generation_search_best_path=generation_search_best_path,
            generation3_ledger_path=generation3_ledger_path,
            generation3_holdout_path=generation3_holdout_path,
            generation3_tournament_path=generation3_tournament_path,
            generation3_search_best_path=generation3_search_best_path,
        ),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=env_ledger_path(SLIMEVOLLEY_ENV_ID))
    parser.add_argument(
        "--holdout",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json",
    )
    parser.add_argument(
        "--tournament",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_dev.json",
    )
    parser.add_argument(
        "--search-best",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_dev.json",
    )
    parser.add_argument(
        "--generation-ledger",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_trials.jsonl",
    )
    parser.add_argument(
        "--generation-holdout",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g2_final.json",
    )
    parser.add_argument(
        "--generation-tournament",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g2_dev.json",
    )
    parser.add_argument(
        "--generation-search-best",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g2_dev.json",
    )
    parser.add_argument(
        "--generation3-ledger",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_trials.jsonl",
    )
    parser.add_argument(
        "--generation3-holdout",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g3_final.json",
    )
    parser.add_argument(
        "--generation3-tournament",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g3_dev.json",
    )
    parser.add_argument(
        "--generation3-search-best",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g3_dev.json",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_PERFORMANCE_REPORT_PATH)
    args = parser.parse_args()
    path = write_slimevolley_performance_report(
        output_path=args.output,
        ledger_path=args.ledger,
        holdout_path=args.holdout,
        tournament_path=args.tournament,
        search_best_path=args.search_best,
        generation_ledger_path=args.generation_ledger,
        generation_holdout_path=args.generation_holdout,
        generation_tournament_path=args.generation_tournament,
        generation_search_best_path=args.generation_search_best,
        generation3_ledger_path=args.generation3_ledger,
        generation3_holdout_path=args.generation3_holdout,
        generation3_tournament_path=args.generation3_tournament,
        generation3_search_best_path=args.generation3_search_best,
    )
    print(path)


if __name__ == "__main__":
    main()
