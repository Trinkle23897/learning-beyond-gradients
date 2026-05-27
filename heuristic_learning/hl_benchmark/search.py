"""Scalar/config search baseline kept separate from structural policy edits."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

from .artifacts import env_ledger_path, env_results_dir, env_summary_path
from .environments import registration_for
from .envs import benchmark_env_ids
from .evaluate import evaluate_policy
from .ledger import DEFAULT_LEDGER_PATH, DEFAULT_SUMMARY_PATH


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def ensure_search_split_allowed(split: str) -> None:
    """Reject holdout-seed optimization."""

    if split in {"holdout", "audit"}:
        raise ValueError("scalar/config search may not use holdout or audit seeds")


def _candidate_config_builder(env_id: str) -> Any:
    """Return the policy-local scalar search-space builder for an environment."""

    try:
        registration = registration_for(env_id)
    except KeyError as exc:
        raise ValueError(f"no scalar search space registered for {env_id!r}") from exc
    module = importlib.import_module(registration.policy_module)
    builder = getattr(module, "candidate_configs", None)
    if not callable(builder):
        raise ValueError(
            f"policy module {registration.policy_module!r} does not expose "
            "callable candidate_configs(max_candidates=...) for scalar search"
        )
    return builder


def candidate_configs(env_id: str, *, max_candidates: int = 32) -> list[dict[str, Any]]:
    """Return bounded scalar-only candidate configs from the env-local policy module."""

    builder = _candidate_config_builder(env_id)
    candidates = list(builder(max_candidates=max_candidates))
    if not candidates:
        raise ValueError(f"scalar search space for {env_id!r} is empty")
    if not all(isinstance(candidate, dict) for candidate in candidates):
        raise TypeError(f"scalar search space for {env_id!r} must contain dictionaries")
    return candidates[:max_candidates]


def safe_name(env_id: str) -> str:
    return env_id.replace("/", "_").replace(":", "_")


def search_best_path(
    env_id: str,
    *,
    split: str = "dev",
    env_artifacts: bool = False,
) -> Path:
    """Return where scalar-search should write the selected config."""

    if env_artifacts:
        return env_results_dir(env_id) / f"search_best_{split}.json"
    return RESULTS_DIR / f"search_best_{safe_name(env_id)}.json"


def resolve_search_paths(
    env_id: str,
    *,
    split: str,
    ledger_path: Path | None,
    summary_path: Path | None,
    output_path: Path | None,
    env_artifacts: bool = False,
) -> tuple[Path, Path, Path]:
    """Return ledger, summary, and best-config paths for one search run."""

    if env_artifacts:
        return (
            ledger_path or env_ledger_path(env_id),
            summary_path or env_summary_path(env_id),
            output_path or search_best_path(env_id, split=split, env_artifacts=True),
        )
    return (
        ledger_path or DEFAULT_LEDGER_PATH,
        summary_path or DEFAULT_SUMMARY_PATH,
        output_path or search_best_path(env_id, split=split, env_artifacts=False),
    )


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
    output_path: Path,
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
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(best_entry["config"], indent=2, sort_keys=True), encoding="utf-8")
        best_mean = best_entry["score_stats"]["mean"]
        print(f"best {env_id}: mean={best_mean:.6g} score={best_score:.6g} config={output_path}")
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
    parser.add_argument("--ledger", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None, help="Path for the selected best scalar config JSON. Only valid for one environment.")
    parser.add_argument(
        "--env-artifacts",
        action="store_true",
        help="Write search ledger, summary, and best config under experiments/<env_slug>/results/.",
    )
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    args = parser.parse_args()

    ensure_search_split_allowed(args.split)
    env_ids = benchmark_env_ids() if args.all else [args.env_id]
    if not env_ids or env_ids == [None]:
        parser.error("--env is required unless --all is set")
    if args.output is not None and len(env_ids) != 1:
        parser.error("--output is only valid when searching one environment")
    for env_id in env_ids:
        ledger_path, summary_path, output_path = resolve_search_paths(
            env_id,
            split=args.split,
            ledger_path=args.ledger,
            summary_path=args.summary,
            output_path=args.output,
            env_artifacts=args.env_artifacts,
        )
        run_search(
            env_id=env_id,
            split=args.split,
            max_candidates=args.max_candidates,
            episodes=args.episodes,
            seed_start=args.seed_start,
            std_penalty=args.std_penalty,
            ledger_path=ledger_path,
            summary_path=summary_path,
            output_path=output_path,
            agent_iterations=args.agent_iterations,
            code_edits=args.code_edits,
        )


if __name__ == "__main__":
    main()

