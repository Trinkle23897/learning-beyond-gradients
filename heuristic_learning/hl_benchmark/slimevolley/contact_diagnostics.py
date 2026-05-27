"""Generate SlimeVolley contact/return diagnostics from persisted traces."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.artifacts import env_reports_dir, env_results_dir
from hl_benchmark.ledger import read_entries
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID


DEFAULT_POLICY = "improved"
DEFAULT_OPPONENT = "builtin"
DEFAULT_SPLIT = "dev"
DEFAULT_LEDGER = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_trials.jsonl"
DEFAULT_JSON = env_results_dir(SLIMEVOLLEY_ENV_ID) / "contact_diagnostics_g3_dev.json"
DEFAULT_MARKDOWN = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "contact_diagnostics_g3_dev.md"


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, np.floating)):
        return float(value)
    return None


def _summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
    array = np.asarray(values, dtype=float)
    return {
        "count": int(array.size),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def _state(event_or_frame: dict[str, Any]) -> dict[str, Any]:
    if "state" in event_or_frame and isinstance(event_or_frame["state"], dict):
        return event_or_frame["state"]
    if "state_before_step" in event_or_frame and isinstance(event_or_frame["state_before_step"], dict):
        return event_or_frame["state_before_step"]
    return {}


def _loss_bucket(state: dict[str, Any]) -> str:
    ball_x = _as_float(state.get("ball_x"))
    ball_y = _as_float(state.get("ball_y"))
    if ball_x is None or ball_y is None:
        return "unknown"
    if ball_y > 1.25:
        return "high"
    if ball_y < 0.35 and ball_x > 1.8:
        return "low_far_right"
    if ball_y < 0.35 and ball_x > 1.0:
        return "low_mid_right"
    if ball_y < 0.35 and ball_x < 0.2:
        return "low_left_or_net"
    return "other"


def _x_bucket(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value < 0.2:
        return "near_net"
    if value < 1.0:
        return "front_half"
    if value < 1.8:
        return "back_half"
    return "rear_wall"


def _frames_for_event(event: dict[str, Any]) -> list[dict[str, Any]]:
    frames = [frame for frame in event.get("pre_event_trace", []) if isinstance(frame, dict)]
    frames.append(
        {
            "step": event.get("step"),
            "action": event.get("action"),
            "state": event.get("state_before_step", {}),
        }
    )
    return frames


def _candidate_contact(prev_frame: dict[str, Any], curr_frame: dict[str, Any]) -> dict[str, Any] | None:
    prev = _state(prev_frame)
    curr = _state(curr_frame)
    prev_bvx = _as_float(prev.get("ball_vx"))
    curr_bvx = _as_float(curr.get("ball_vx"))
    prev_bvy = _as_float(prev.get("ball_vy"))
    curr_bvy = _as_float(curr.get("ball_vy"))
    agent_x = _as_float(curr.get("agent_x"))
    ball_x = _as_float(curr.get("ball_x"))
    ball_y = _as_float(curr.get("ball_y"))
    agent_y = _as_float(curr.get("agent_y"))
    if None in (prev_bvx, curr_bvx, prev_bvy, curr_bvy, agent_x, ball_x, ball_y):
        return None

    distance = abs(float(ball_x) - float(agent_x))
    delta_bvx = float(curr_bvx) - float(prev_bvx)
    delta_bvy = float(curr_bvy) - float(prev_bvy)
    horizontal_flip = (
        float(prev_bvx) * float(curr_bvx) < 0.0
        and abs(float(prev_bvx)) > 0.4
        and abs(float(curr_bvx)) > 0.4
    )
    sharp_velocity_change = abs(delta_bvx) >= 0.85 or abs(delta_bvy) >= 0.85
    plausible_near_agent = distance <= 0.42 and 0.12 <= float(ball_y) <= 0.85
    if not (plausible_near_agent and (horizontal_flip or sharp_velocity_change)):
        return None

    return {
        "step": curr_frame.get("step"),
        "prev_action": prev_frame.get("action"),
        "action": curr_frame.get("action"),
        "ball_x": float(ball_x),
        "ball_y": float(ball_y),
        "agent_x": float(agent_x),
        "agent_y": None if agent_y is None else float(agent_y),
        "ball_agent_x_distance": distance,
        "prev_ball_vx": float(prev_bvx),
        "ball_vx": float(curr_bvx),
        "delta_ball_vx": delta_bvx,
        "prev_ball_vy": float(prev_bvy),
        "ball_vy": float(curr_bvy),
        "delta_ball_vy": delta_bvy,
        "horizontal_flip": bool(horizontal_flip),
        "x_bucket": _x_bucket(float(ball_x)),
    }


def _select_entry(
    entries: list[dict[str, Any]],
    *,
    policy: str,
    opponent: str,
    split: str,
) -> dict[str, Any] | None:
    matching = [
        entry for entry in entries
        if entry.get("policy_version") == policy
        and entry.get("opponent_name") == opponent
        and entry.get("pass_fail") == "pass"
        and entry.get("seed_range", {}).get("split") == split
        and entry.get("per_episode")
        and int(entry.get("config", {}).get("trace_window") or 0) > 0
    ]
    if not matching:
        return None
    return sorted(matching, key=lambda entry: str(entry.get("timestamp", "")))[-1]


def build_contact_diagnostics(
    entries: list[dict[str, Any]],
    *,
    policy: str = DEFAULT_POLICY,
    opponent: str = DEFAULT_OPPONENT,
    split: str = DEFAULT_SPLIT,
) -> dict[str, Any]:
    """Return contact/return diagnostics for the latest traced matching row."""

    entry = _select_entry(entries, policy=policy, opponent=opponent, split=split)
    if entry is None:
        return {
            "status": "no_data",
            "environment": SLIMEVOLLEY_ENV_ID,
            "policy": policy,
            "opponent": opponent,
            "split": split,
            "anti_tuning_note": "No holdout rows are read or summarized by this diagnostic.",
            "message": "No traced matching development entry was found.",
        }

    point_events: list[dict[str, Any]] = []
    for episode in entry.get("per_episode", []):
        if not isinstance(episode, dict):
            continue
        for event in episode.get("point_events", []):
            if isinstance(event, dict):
                event = dict(event)
                event["seed"] = episode.get("seed")
                point_events.append(event)

    outcomes = Counter(str(event.get("outcome", "")) for event in point_events)
    action_by_outcome: dict[str, Counter[str]] = {"point_lost": Counter(), "point_won": Counter()}
    loss_buckets: Counter[str] = Counter()
    loss_values: dict[str, list[float]] = {
        "agent_x": [],
        "agent_y": [],
        "ball_x": [],
        "ball_y": [],
        "ball_vx": [],
        "ball_vy": [],
    }
    contact_candidates: list[dict[str, Any]] = []

    for event in point_events:
        outcome = str(event.get("outcome", ""))
        if outcome in action_by_outcome:
            action_by_outcome[outcome][str(event.get("action", ""))] += 1
        state = _state(event)
        if outcome == "point_lost":
            loss_buckets[_loss_bucket(state)] += 1
            for key, values in loss_values.items():
                maybe_value = _as_float(state.get(key))
                if maybe_value is not None:
                    values.append(maybe_value)

        frames = _frames_for_event(event)
        for prev_frame, curr_frame in zip(frames, frames[1:]):
            contact = _candidate_contact(prev_frame, curr_frame)
            if contact is None:
                continue
            contact["event_outcome"] = outcome
            contact["seed"] = event.get("seed")
            contact["event_step"] = event.get("step")
            contact_candidates.append(contact)

    contacts_by_outcome = Counter(str(contact.get("event_outcome")) for contact in contact_candidates)
    contacts_by_action = Counter(str(contact.get("action")) for contact in contact_candidates)
    contacts_by_x_bucket = Counter(str(contact.get("x_bucket")) for contact in contact_candidates)
    examples = sorted(
        contact_candidates,
        key=lambda item: (str(item.get("event_outcome")), int(item.get("event_step") or 0), int(item.get("step") or 0)),
    )[:12]

    return {
        "status": "pass",
        "environment": SLIMEVOLLEY_ENV_ID,
        "policy": policy,
        "opponent": opponent,
        "split": split,
        "selected_entry": {
            "timestamp": entry.get("timestamp"),
            "policy_version": entry.get("policy_version"),
            "opponent_name": entry.get("opponent_name"),
            "change_type": entry.get("change_type"),
            "change_summary": entry.get("change_summary"),
            "score_stats": entry.get("score_stats", {}),
            "win_loss_draw": entry.get("win_loss_draw", {}),
            "seed_range": entry.get("seed_range", {}),
            "trace_window": entry.get("config", {}).get("trace_window"),
        },
        "event_counts": dict(sorted(outcomes.items())),
        "loss_state_buckets": dict(loss_buckets.most_common()),
        "loss_state_stats": {key: _summary(values) for key, values in loss_values.items()},
        "point_action_counts": {
            outcome: dict(counter.most_common())
            for outcome, counter in action_by_outcome.items()
        },
        "contact_candidate_summary": {
            "count": len(contact_candidates),
            "by_event_outcome": dict(contacts_by_outcome.most_common()),
            "by_action": dict(contacts_by_action.most_common()),
            "by_x_bucket": dict(contacts_by_x_bucket.most_common()),
        },
        "contact_candidate_examples": examples,
        "limitations": [
            "Contacts are inferred from compact pre-event trace velocity changes, not from engine contact callbacks.",
            "The default artifact reads development rows only and does not inspect generation-3 holdout seeds.",
            "Trace windows are short, so absence of a candidate does not prove absence of contact earlier in a rally.",
        ],
        "next_hypotheses": [
            "Target return placement after inferred contact instead of restarting serve behavior.",
            "Separate front-net and rear-wall low-loss buckets; they may need different recovery modes.",
            "Before a new policy edit, run this diagnostic on the current dev row and compare contact candidate locations against failed attempts.",
        ],
        "anti_tuning_note": "This artifact is generated from development traces only. Generation-3 holdout remains final-only and must not be inspected for policy design.",
    }


def _format(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def render_contact_diagnostics_markdown(payload: dict[str, Any]) -> str:
    """Render the contact diagnostics payload as Markdown."""

    lines = [
        "# SlimeVolley Generation-3 Contact/Return Diagnostics",
        "",
        "This report is generated from persisted development traces only. It does not run evaluation and does not inspect generation-3 holdout seeds.",
        "",
        "## Selection",
        "",
        f"- Status: `{payload.get('status')}`",
        f"- Environment: `{payload.get('environment')}`",
        f"- Policy/opponent/split: `{payload.get('policy')}` vs `{payload.get('opponent')}` on `{payload.get('split')}`",
    ]
    selected = payload.get("selected_entry", {})
    if selected:
        seed_range = selected.get("seed_range", {})
        stop_exclusive = seed_range.get("stop_exclusive")
        stop_label = stop_exclusive - 1 if isinstance(stop_exclusive, int) else ""
        lines.extend(
            [
                f"- Selected row: `{selected.get('timestamp')}`",
                f"- Change type: `{selected.get('change_type')}`",
                f"- Seeds: `{seed_range.get('start')}..{stop_label}`",
                f"- Trace window: `{selected.get('trace_window')}`",
                f"- Score mean: `{_format(selected.get('score_stats', {}).get('mean'))}`",
                f"- W/L/D: `{selected.get('win_loss_draw', {}).get('wins')}/{selected.get('win_loss_draw', {}).get('losses')}/{selected.get('win_loss_draw', {}).get('draws')}`",
            ]
        )
    else:
        lines.append(f"- Message: {payload.get('message', '')}")

    lines.extend(["", "## Point Outcomes", "", "| Outcome | Count |", "| --- | ---: |"])
    for outcome, count in payload.get("event_counts", {}).items():
        lines.append(f"| {outcome} | {count} |")

    lines.extend(["", "## Loss Buckets", "", "| Bucket | Count |", "| --- | ---: |"])
    for bucket, count in payload.get("loss_state_buckets", {}).items():
        lines.append(f"| {bucket} | {count} |")

    lines.extend(["", "## Inferred Contact Candidates", ""])
    summary = payload.get("contact_candidate_summary", {})
    lines.append(f"- Candidate count: `{summary.get('count', 0)}`")
    lines.append(f"- By event outcome: `{summary.get('by_event_outcome', {})}`")
    lines.append(f"- By action: `{summary.get('by_action', {})}`")
    lines.append(f"- By x bucket: `{summary.get('by_x_bucket', {})}`")

    examples = payload.get("contact_candidate_examples", [])
    if examples:
        lines.extend(
            [
                "",
                "| Seed | Event step | Candidate step | Outcome | Action | X bucket | Ball x/y | Ball vx delta |",
                "| ---: | ---: | ---: | --- | --- | --- | --- | ---: |",
            ]
        )
        for item in examples:
            lines.append(
                "| {seed} | {event_step} | {step} | {outcome} | {action} | {bucket} | {ball_x}/{ball_y} | {delta} |".format(
                    seed=item.get("seed"),
                    event_step=item.get("event_step"),
                    step=item.get("step"),
                    outcome=item.get("event_outcome"),
                    action=item.get("action"),
                    bucket=item.get("x_bucket"),
                    ball_x=_format(item.get("ball_x")),
                    ball_y=_format(item.get("ball_y")),
                    delta=_format(item.get("delta_ball_vx")),
                )
            )
    else:
        lines.append("- No inferred contact candidates were found in the selected trace windows.")

    lines.extend(["", "## Limitations", ""])
    for item in payload.get("limitations", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Next Hypotheses", ""])
    for item in payload.get("next_hypotheses", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Anti-Tuning Note", "", str(payload.get("anti_tuning_note", "")), ""])
    return "\n".join(lines)


def write_contact_diagnostics(
    *,
    ledger_path: Path = DEFAULT_LEDGER,
    json_path: Path = DEFAULT_JSON,
    markdown_path: Path = DEFAULT_MARKDOWN,
    policy: str = DEFAULT_POLICY,
    opponent: str = DEFAULT_OPPONENT,
    split: str = DEFAULT_SPLIT,
) -> dict[str, Any]:
    entries = read_entries(ledger_path) if ledger_path.exists() else []
    payload = build_contact_diagnostics(entries, policy=policy, opponent=opponent, split=split)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_contact_diagnostics_markdown(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--opponent", default=DEFAULT_OPPONENT)
    parser.add_argument("--split", default=DEFAULT_SPLIT)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    payload = write_contact_diagnostics(
        ledger_path=args.ledger,
        json_path=args.json_output,
        markdown_path=args.markdown_output,
        policy=args.policy,
        opponent=args.opponent,
        split=args.split,
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        selected = payload.get("selected_entry", {})
        print(
            "SlimeVolley contact diagnostics: {status} policy={policy} opponent={opponent} "
            "split={split} row={row} candidates={candidates}".format(
                status=payload.get("status"),
                policy=payload.get("policy"),
                opponent=payload.get("opponent"),
                split=payload.get("split"),
                row=selected.get("timestamp", "none"),
                candidates=payload.get("contact_candidate_summary", {}).get("count", 0),
            )
        )


if __name__ == "__main__":
    main()
