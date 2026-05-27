"""Development-only front-posture probes for SlimeVolley generation 5.

Previous generation-5 probes tried to change the final low-contact action,
reset macro, and short followthrough after contact. This probe tests a more
global alternative: the packaged RNN may win more hard archived-opponent points
because it stays nearer the front court before the low-contact window arrives.

Only generation-5 development seeds are used. The script writes an append-only
JSON artifact and does not edit maintained policies or canonical ledgers.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.policies.slimevolley import (
    RALLY_SERVE_CONFIG,
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyConfig,
    SlimeVolleyNetPressurePolicy,
)
from hl_benchmark.slimevolley.adapter import make_slimevolley_env, run_slimevolley_episode
from hl_benchmark.slimevolley.opponents import make_slimevolley_opponent


SHORT_SEEDS = list(range(12000, 12016))
FULL_SEEDS = list(range(12000, 12050))
HARD_OPPONENTS = ["improved-v3", "improved-v4", "improved-v5", "improved-v6"]
SCREEN_OPPONENTS = ["builtin", *HARD_OPPONENTS]
FULL_POOL = [
    "builtin",
    "random",
    "initial",
    "improved-v0",
    "improved-v2",
    "improved-v3",
    "improved-v4",
    "improved-v5",
    "improved-v6",
]


@dataclass(frozen=True)
class PostureConfig:
    """Readable scalar front-posture candidate around net-pressure."""

    name: str
    label: str
    config: SlimeVolleyConfig


POSTURE_CONFIGS: dict[str, PostureConfig] = {
    "front_home_110": PostureConfig(
        name="front_home_110",
        label="scalar/config: modestly front-shift home and defensive anchors",
        config=replace(
            RALLY_SERVE_CONFIG,
            home_x=1.05,
            defensive_home_x=1.10,
            attack_home_x=0.72,
        ),
    ),
    "front_home_095": PostureConfig(
        name="front_home_095",
        label="scalar/config: front-court default posture with normal overcommit guard",
        config=replace(
            RALLY_SERVE_CONFIG,
            home_x=0.92,
            defensive_home_x=1.00,
            attack_home_x=0.66,
        ),
    ),
    "front_home_080": PostureConfig(
        name="front_home_080",
        label="scalar/config: aggressive front-court default posture",
        config=replace(
            RALLY_SERVE_CONFIG,
            home_x=0.80,
            defensive_home_x=0.90,
            attack_home_x=0.58,
        ),
    ),
    "front_home_095_low_guard": PostureConfig(
        name="front_home_095_low_guard",
        label="scalar/config: front posture with a slightly wider low rescue window",
        config=replace(
            RALLY_SERVE_CONFIG,
            home_x=0.92,
            defensive_home_x=1.00,
            attack_home_x=0.66,
            low_ball_rescue_x_window=0.60,
        ),
    ),
    "front_home_095_fast_land": PostureConfig(
        name="front_home_095_fast_land",
        label="scalar/config: front posture with shorter landing horizon",
        config=replace(
            RALLY_SERVE_CONFIG,
            home_x=0.92,
            defensive_home_x=1.00,
            attack_home_x=0.66,
            landing_horizon=0.30,
        ),
    ),
}


def _policy_for_candidate(candidate: str) -> Any:
    if candidate == "net_pressure_reference":
        return SlimeVolleyNetPressurePolicy()
    if candidate == "baseline_rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if candidate not in POSTURE_CONFIGS:
        raise ValueError(f"unknown candidate {candidate!r}")
    return SlimeVolleyNetPressurePolicy(POSTURE_CONFIGS[candidate].config)


def evaluate_candidate(candidate: str, opponent_name: str, seeds: list[int], *, trace_window: int = 0) -> dict[str, Any]:
    env = make_slimevolley_env()
    policy = _policy_for_candidate(candidate)
    opponent = make_slimevolley_opponent(opponent_name)
    scores: list[float] = []
    outcomes: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    terminal_modes: Counter[str] = Counter()
    steps = 0
    points_won = 0
    points_lost = 0
    try:
        for seed in seeds:
            episode = run_slimevolley_episode(
                env=env,
                policy=policy,
                opponent=opponent,
                seed=seed,
                trace_window=trace_window,
            )
            scores.append(float(episode.score))
            outcomes[episode.outcome] += 1
            action_counts.update(episode.action_counts)
            steps += int(episode.steps)
            for event in episode.point_events:
                if event.get("outcome") == "point_won":
                    points_won += 1
                elif event.get("outcome") == "point_lost":
                    points_lost += 1
                diagnostics = event.get("policy_diagnostics") or {}
                mode = diagnostics.get("mode")
                if mode:
                    terminal_modes[str(mode)] += 1
    finally:
        env.close()

    if candidate == "net_pressure_reference":
        label = "reference"
        policy_config: dict[str, Any] = SlimeVolleyNetPressurePolicy().config()
    elif candidate == "baseline_rnn":
        label = "neural comparator"
        policy_config = SlimeVolleyBuiltInRnnPolicy().config()
    else:
        label = POSTURE_CONFIGS[candidate].label
        policy_config = asdict(POSTURE_CONFIGS[candidate].config)

    return {
        "candidate": candidate,
        "label": label,
        "opponent": opponent_name,
        "seeds": f"{seeds[0]}..{seeds[-1]}",
        "episodes": len(seeds),
        "mean": float(np.mean(scores)) if scores else None,
        "std": float(np.std(scores)) if scores else None,
        "wins": int(outcomes.get("win", 0)),
        "losses": int(outcomes.get("loss", 0)),
        "draws": int(outcomes.get("draw", 0)),
        "steps": steps,
        "points_won": points_won,
        "points_lost": points_lost,
        "action_counts": dict(sorted(action_counts.items())),
        "terminal_modes": dict(sorted(terminal_modes.items())),
        "policy_config": policy_config,
    }


def run_phase(phase: str, candidates: list[str] | None, *, trace_window: int) -> dict[str, Any]:
    if phase == "screen":
        seeds = SHORT_SEEDS
        opponents = SCREEN_OPPONENTS
        selected = candidates or ["net_pressure_reference", "baseline_rnn", *POSTURE_CONFIGS]
    elif phase == "full":
        seeds = FULL_SEEDS
        opponents = FULL_POOL
        selected = candidates or ["net_pressure_reference", "baseline_rnn"]
    else:
        raise ValueError(f"unknown phase {phase!r}")

    rows: list[dict[str, Any]] = []
    for candidate in selected:
        for opponent in opponents:
            row = evaluate_candidate(
                candidate,
                opponent,
                seeds,
                trace_window=trace_window if opponent == "builtin" else 0,
            )
            rows.append(row)
            print(
                f"{phase:6s} {candidate:28s} vs {opponent:11s} "
                f"mean={row['mean']:.4f} WLD={row['wins']}/{row['losses']}/{row['draws']} "
                f"steps={row['steps']}",
                flush=True,
            )
    return {
        "phase": phase,
        "seed_list": seeds,
        "opponents": opponents,
        "candidates": selected,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["screen", "full"], default="screen")
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--trace-window", type=int, default=24)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/slimevolley/results/generation_5_position_posture_probe.json"),
    )
    args = parser.parse_args()
    payload = {
        "protocol": "generation-5 development-only front-posture scalar/config probe",
        "holdout_audit_used": False,
        "phase_result": run_phase(args.phase, args.candidate, trace_window=args.trace_window),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        payload_to_write = existing if isinstance(existing, dict) and "runs" in existing else {"runs": [existing]}
        payload_to_write["runs"].append(payload)
    else:
        payload_to_write = {"runs": [payload]}
    args.output.write_text(json.dumps(payload_to_write, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.output}", flush=True)


if __name__ == "__main__":
    main()
