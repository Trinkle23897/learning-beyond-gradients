"""Scalar/config search baseline kept separate from structural policy edits."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

from .envs import benchmark_env_ids
from .evaluate import evaluate_policy
from .ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def ensure_search_split_allowed(split: str) -> None:
    """Reject holdout-seed optimization."""

    if split in {"holdout", "audit"}:
        raise ValueError("scalar/config search may not use holdout or audit seeds")


def candidate_configs(env_id: str, *, max_candidates: int = 32) -> list[dict[str, Any]]:
    """Return bounded scalar-only candidate configs for an environment."""

    candidates: list[dict[str, Any]] = []
    if env_id == "CartPole-v1":
        for pole_velocity_gain, cart_position_gain, cart_velocity_gain in itertools.product(
            [0.25, 0.35, 0.50, 0.70],
            [0.00, 0.03, 0.06, 0.10],
            [0.00, 0.02],
        ):
            candidates.append(
                {
                    "pole_velocity_gain": pole_velocity_gain,
                    "cart_position_gain": cart_position_gain,
                    "cart_velocity_gain": cart_velocity_gain,
                }
            )
    elif env_id == "MountainCar-v0":
        for goal_commit_position, goal_commit_velocity, coast_velocity_window in itertools.product(
            [-0.35, -0.20, -0.05, 0.10],
            [-0.020, -0.012, -0.004, 0.0],
            [0.0, 0.004],
        ):
            candidates.append(
                {
                    "goal_commit_position": goal_commit_position,
                    "goal_commit_velocity": goal_commit_velocity,
                    "coast_velocity_window": coast_velocity_window,
                }
            )
    elif env_id == "Acrobot-v1":
        for velocity_gain_1, velocity_gain_2, phase_gain in itertools.product(
            [0.20, 0.35, 0.50, 0.60, 0.75, 0.90, 1.00, 1.20],
            [0.70, 0.90, 1.10, 1.30, 1.50, 1.60, 1.80],
            [0.20, 0.35, 0.50, 0.65, 0.80],
        ):
            candidates.append(
                {
                    "velocity_gain_1": velocity_gain_1,
                    "velocity_gain_2": velocity_gain_2,
                    "phase_gain": phase_gain,
                }
            )
    elif env_id == "LunarLander-v3":
        for angle_vx_gain, hover_y_gain, engine_deadband in itertools.product(
            [0.70, 1.00, 1.30, 1.60],
            [0.35, 0.50, 0.70, 0.90],
            [0.03, 0.05],
        ):
            candidates.append(
                {
                    "angle_vx_gain": angle_vx_gain,
                    "hover_y_gain": hover_y_gain,
                    "engine_deadband": engine_deadband,
                }
            )
    elif env_id == "BipedalWalker-v3":
        for gait_period, hip_amplitude, knee_drive in itertools.product(
            [36, 44, 48, 56],
            [0.45, 0.60, 0.75, 0.90],
            [0.55, 0.75],
        ):
            candidates.append(
                {
                    "gait_period": gait_period,
                    "hip_amplitude": hip_amplitude,
                    "knee_drive": knee_drive,
                }
            )
    else:
        raise ValueError(f"no scalar search space registered for {env_id!r}")
    return candidates[:max_candidates]


def safe_name(env_id: str) -> str:
    return env_id.replace("/", "_").replace(":", "_")


def run_search(
    *,
    env_id: str,
    split: str,
    max_candidates: int,
    episodes: int | None,
    seed_start: int | None,
    std_penalty: float,
    ledger_path: Path,
    summary_path: Path,
    agent_iterations: int,
    code_edits: int,
) -> dict[str, Any] | None:
    """Evaluate scalar candidates on development seeds and persist the best config."""

    ensure_search_split_allowed(split)
    best_entry: dict[str, Any] | None = None
    best_score: float | None = None
    candidates = candidate_configs(env_id, max_candidates=max_candidates)
    for index, config in enumerate(candidates):
        entry = evaluate_policy(
            env_id=env_id,
            policy_name="tuned",
            split=split,
            seed_start=seed_start,
            episodes=episodes,
            config=config,
            ledger_path=ledger_path,
            summary_path=summary_path,
            tests_run=[],
            change_summary=(
                f"Scalar search candidate {index + 1}/{len(candidates)} for {env_id}; "
                "no structural policy logic changed."
            ),
            failure_analysis="No failure observed.",
            next_hypothesis=(
                "Select the best scalar config on development seeds only using "
                f"mean - {std_penalty:g} * std as the selection score."
            ),
            change_type="scalar/config tuning",
            agent_iterations=agent_iterations,
            code_edits=code_edits,
        )
        mean = entry["score_stats"]["mean"]
        std = entry["score_stats"]["std"]
        if entry["pass_fail"] == "pass" and mean is not None:
            score = float(mean) - std_penalty * float(std or 0.0)
            if best_score is None or score > best_score:
                best_score = score
                best_entry = entry
        print(
            f"{env_id:18s} candidate={index + 1:02d}/{len(candidates):02d} "
            f"mean={mean if mean is not None else 'n/a'}"
        )

    if best_entry is not None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        best_path = RESULTS_DIR / f"search_best_{safe_name(env_id)}.json"
        best_path.write_text(json.dumps(best_entry["config"], indent=2, sort_keys=True), encoding="utf-8")
        best_mean = best_entry["score_stats"]["mean"]
        print(f"best {env_id}: mean={best_mean:.6g} score={best_score:.6g} config={best_path}")
    return best_entry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--env", dest="env_id")
    parser.add_argument("--split", default="dev", choices=["dev", "smoke", "holdout", "audit"])
    parser.add_argument("--max-candidates", type=int, default=32)
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument(
        "--std-penalty",
        type=float,
        default=0.0,
        help="development-only robust selection score: mean - penalty * std",
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    args = parser.parse_args()

    ensure_search_split_allowed(args.split)
    env_ids = benchmark_env_ids() if args.all else [args.env_id]
    if not env_ids or env_ids == [None]:
        parser.error("--env is required unless --all is set")
    for env_id in env_ids:
        run_search(
            env_id=env_id,
            split=args.split,
            max_candidates=args.max_candidates,
            episodes=args.episodes,
            seed_start=args.seed_start,
            std_penalty=args.std_penalty,
            ledger_path=args.ledger,
            summary_path=args.summary,
            agent_iterations=args.agent_iterations,
            code_edits=args.code_edits,
        )


if __name__ == "__main__":
    main()

