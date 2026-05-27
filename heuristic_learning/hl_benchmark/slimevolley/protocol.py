"""Generate predeclared SlimeVolley experiment-generation protocols."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hl_benchmark.artifacts import env_configs_dir, env_ledger_path, env_reports_dir, env_results_dir, env_summary_path
from hl_benchmark.envs import SEED_SPLITS
from hl_benchmark.environments import registration_for
from hl_benchmark.slimevolley.adapter import SLIMEVOLLEY_ENV_ID


PROTOCOL_ID = "slimevolley-g2"
PROTOCOL_STATUS = "predeclared-not-run"
DEFAULT_PROTOCOL_JSON_PATH = env_configs_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_protocol.json"
DEFAULT_PROTOCOL_REPORT_PATH = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_protocol.md"
GENERATION_3_PROTOCOL_ID = "slimevolley-g3"
DEFAULT_GENERATION_3_PROTOCOL_JSON_PATH = env_configs_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_protocol.json"
DEFAULT_GENERATION_3_PROTOCOL_REPORT_PATH = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_protocol.md"
GENERATION_4_PROTOCOL_ID = "slimevolley-g4"
DEFAULT_GENERATION_4_PROTOCOL_JSON_PATH = env_configs_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_protocol.json"
DEFAULT_GENERATION_4_PROTOCOL_REPORT_PATH = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_protocol.md"
GENERATION_5_PROTOCOL_ID = "slimevolley-g5"
DEFAULT_GENERATION_5_PROTOCOL_JSON_PATH = env_configs_dir(SLIMEVOLLEY_ENV_ID) / "generation_5_protocol.json"
DEFAULT_GENERATION_5_PROTOCOL_REPORT_PATH = env_reports_dir(SLIMEVOLLEY_ENV_ID) / "generation_5_protocol.md"

GENERATION_2_SEED_SPLITS = {
    "smoke": {"start": 3000, "stop_exclusive": 3002, "purpose": "dependency and command smoke checks only"},
    "dev": {"start": 3000, "stop_exclusive": 3050, "purpose": "diagnosis, structural policy iteration, scalar search, and tournament development evidence"},
    "holdout": {"start": 4000, "stop_exclusive": 4050, "purpose": "final-only generation-2 evaluation after policies and scalar configs are frozen"},
    "audit": {"start": 5000, "stop_exclusive": 5050, "purpose": "reserved independent audit seeds, not available for tuning"},
}

GENERATION_2_POLICIES = ["random", "initial", "tuned", "improved", "baseline-rnn"]
GENERATION_2_DEV_OPPONENTS = [
    "builtin",
    "random",
    "initial",
    "improved-v0",
    "improved-v1",
    "improved-v2",
    "improved",
]
GENERATION_2_SEARCH_OPPONENTS = ["builtin", "random", "initial", "improved-v0", "improved-v2"]
GENERATION_2_HOLDOUT_OPPONENTS = ["builtin", "random", "initial", "improved-v0", "improved-v2"]

GENERATION_3_SEED_SPLITS = {
    "smoke": {"start": 6000, "stop_exclusive": 6002, "purpose": "dependency and command smoke checks only"},
    "dev": {"start": 6000, "stop_exclusive": 6050, "purpose": "diagnosis, structural policy iteration, scalar search, and tournament development evidence"},
    "holdout": {"start": 7000, "stop_exclusive": 7050, "purpose": "final-only generation-3 evaluation after policies and scalar configs are frozen"},
    "audit": {"start": 8000, "stop_exclusive": 8050, "purpose": "reserved independent audit seeds, not available for tuning"},
}
GENERATION_3_POLICIES = GENERATION_2_POLICIES
GENERATION_3_DEV_OPPONENTS = GENERATION_2_DEV_OPPONENTS
GENERATION_3_SEARCH_OPPONENTS = GENERATION_2_SEARCH_OPPONENTS
GENERATION_3_HOLDOUT_OPPONENTS = [*GENERATION_2_HOLDOUT_OPPONENTS, "improved-v3"]

GENERATION_4_SEED_SPLITS = {
    "smoke": {"start": 9000, "stop_exclusive": 9002, "purpose": "dependency and command smoke checks only"},
    "dev": {"start": 9000, "stop_exclusive": 9050, "purpose": "diagnosis, structural policy iteration, scalar search, and tournament development evidence"},
    "holdout": {"start": 10000, "stop_exclusive": 10050, "purpose": "final-only generation-4 evaluation after policies and scalar configs are frozen"},
    "audit": {"start": 11000, "stop_exclusive": 11050, "purpose": "reserved independent audit seeds, not available for tuning"},
}
GENERATION_4_POLICIES = [*GENERATION_3_POLICIES, "improved-v4", "improved-v5", "improved-v6", "improved-tuned", "attack", "rally-serve", "temporal", "planner", "teacher-assisted"]
GENERATION_4_DEV_OPPONENTS = [*GENERATION_3_DEV_OPPONENTS, "improved-v3", "improved-v4", "improved-v5", "improved-v6", "improved-tuned", "attack", "rally-serve", "temporal", "planner", "teacher-assisted"]
GENERATION_4_SEARCH_OPPONENTS = [*GENERATION_3_SEARCH_OPPONENTS, "improved-v3", "improved-v4", "improved-v5", "improved-v6"]
GENERATION_4_HOLDOUT_OPPONENTS = [*GENERATION_3_HOLDOUT_OPPONENTS, "improved-v4", "improved-v5", "improved-v6"]

GENERATION_5_SEED_SPLITS = {
    "smoke": {"start": 12000, "stop_exclusive": 12002, "purpose": "dependency and command smoke checks only"},
    "dev": {"start": 12000, "stop_exclusive": 12050, "purpose": "fresh post-generation-4 diagnosis, structural policy iteration, scalar search, and tournament development evidence"},
    "holdout": {"start": 13000, "stop_exclusive": 13050, "purpose": "final-only generation-5 evaluation after policies and scalar configs are frozen"},
    "audit": {"start": 14000, "stop_exclusive": 14050, "purpose": "reserved independent audit seeds, not available for tuning"},
}
GENERATION_5_POLICIES = [*GENERATION_4_POLICIES, "net-pressure"]
GENERATION_5_DEV_OPPONENTS = [*GENERATION_4_DEV_OPPONENTS, "net-pressure"]
GENERATION_5_SEARCH_OPPONENTS = GENERATION_4_SEARCH_OPPONENTS
GENERATION_5_HOLDOUT_OPPONENTS = GENERATION_4_HOLDOUT_OPPONENTS


def _custom_module_root() -> str:
    """Return the registered custom harness root for SlimeVolley."""

    return registration_for(SLIMEVOLLEY_ENV_ID).custom_module_root


def _protocol_module_name() -> str:
    return f"{_custom_module_root()}.protocol"


def _audit_module_command() -> str:
    return f"python3 -m {_custom_module_root()}.audit --format json"


def _range_payload(seed_range: range) -> dict[str, Any]:
    return {
        "start": seed_range.start,
        "stop_exclusive": seed_range.stop,
        "episodes": len(seed_range),
        "label": f"{seed_range.start}..{seed_range.stop - 1}",
    }


def _generation_split_payload(seed_splits: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for split, spec in seed_splits.items():
        start = int(spec["start"])
        stop_exclusive = int(spec["stop_exclusive"])
        payload[split] = {
            "start": start,
            "stop_exclusive": stop_exclusive,
            "episodes": stop_exclusive - start,
            "label": f"{start}..{stop_exclusive - 1}",
            "purpose": spec["purpose"],
        }
    return payload


def _generation_2_split_payload() -> dict[str, dict[str, Any]]:
    return _generation_split_payload(GENERATION_2_SEED_SPLITS)


def _generation_3_split_payload() -> dict[str, dict[str, Any]]:
    return _generation_split_payload(GENERATION_3_SEED_SPLITS)


def _generation_4_split_payload() -> dict[str, dict[str, Any]]:
    return _generation_split_payload(GENERATION_4_SEED_SPLITS)


def _generation_5_split_payload() -> dict[str, dict[str, Any]]:
    return _generation_split_payload(GENERATION_5_SEED_SPLITS)


def generation_2_protocol_payload() -> dict[str, Any]:
    """Return the deterministic SlimeVolley generation-2 protocol payload."""

    g2_ledger = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_trials.jsonl"
    g2_summary = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_summary.csv"
    g2_search = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g2_dev.json"
    g2_tournament = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g2_dev.json"
    g2_holdout = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g2_final.json"

    return {
        "environment": SLIMEVOLLEY_ENV_ID,
        "protocol_id": PROTOCOL_ID,
        "status": PROTOCOL_STATUS,
        "created_by": _protocol_module_name(),
        "source_generation": {
            "id": "slimevolley-g1",
            "ledger": str(env_ledger_path(SLIMEVOLLEY_ENV_ID)),
            "summary": str(env_summary_path(SLIMEVOLLEY_ENV_ID)),
            "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json"),
            "holdout_seeds": _range_payload(SEED_SPLITS["holdout"]),
            "audit_seeds": _range_payload(SEED_SPLITS["audit"]),
            "rule": "Generation-1 holdout is already opened; do not tune, debug, or select policies on those seeds.",
        },
        "generation_2": {
            "id": PROTOCOL_ID,
            "ledger": str(g2_ledger),
            "summary": str(g2_summary),
            "seed_splits": _generation_2_split_payload(),
            "policy_start": "improved",
            "policies": GENERATION_2_POLICIES,
            "development_opponents": GENERATION_2_DEV_OPPONENTS,
            "scalar_search_opponents": GENERATION_2_SEARCH_OPPONENTS,
            "holdout_opponents": GENERATION_2_HOLDOUT_OPPONENTS,
            "artifacts": {
                "search_best": str(g2_search),
                "round_robin": str(g2_tournament),
                "holdout": str(g2_holdout),
            },
        },
        "guardrails": [
            "Use the generation-2 ledger and summary paths for all generation-2 evidence; do not append generation-2 rows to the generation-1 ledger until audit support is explicitly extended.",
            "Use generation-2 development seeds for diagnosis, structural edits, scalar search, and tournaments.",
            "Do not inspect generation-2 holdout seeds until the policy code, scalar config, opponent pool, and tests are frozen.",
            "Do not use generation-1 holdout results as tuning feedback; treat them only as historical final evidence.",
            "Record tests_run, tests_pass_fail, agent_iterations, code_edits, and failure_analysis on every generation-2 ledger-producing run.",
        ],
        "diagnosis_targets": [
            "built-in opponent serve and return timing",
            "high-arc defense before the ball drops below reachable height",
            "low-ball contact timing without late jump overcommit",
            "recovery to defensive home position after contact",
            "exploitability against archived heuristic opponents",
        ],
        "commands": {
            "regenerate_protocol": "make slimevolley-protocol",
            "verification_before_edits": "make slimevolley-verify",
            "dev_builtin_trace": (
                "make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_2_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_2_summary.csv "
                "--seed-start 3000 --episodes 50 --trace-window 8 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
            "scalar_search": (
                "make slimevolley-search MAX_CANDIDATES=16 "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_2_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_2_summary.csv "
                "--output experiments/slimevolley/results/search_best_g2_dev.json "
                "--seed-start 3000 --episodes 50 --opponents builtin random initial improved-v0 improved-v2\""
            ),
            "development_tournament": (
                "make slimevolley-tournament SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_2_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_2_summary.csv "
                "--output experiments/slimevolley/results/round_robin_g2_dev.json "
                "--seed-start 3000 --episodes 50\""
            ),
            "final_holdout_once": (
                "make slimevolley-final-eval "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_2_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_2_summary.csv "
                "--output experiments/slimevolley/results/holdout_g2_final.json "
                "--best-config experiments/slimevolley/results/search_best_g2_dev.json "
                "--seed-start 4000 --episodes 50 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
        },
        "promotion_checks": [
            "make verify",
            "make slimevolley-verify",
            _audit_module_command(),
        ],
    }




def generation_3_protocol_payload() -> dict[str, Any]:
    """Return the deterministic SlimeVolley generation-3 protocol payload."""

    g3_ledger = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_trials.jsonl"
    g3_summary = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_summary.csv"
    g3_search = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g3_dev.json"
    g3_tournament = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g3_dev.json"
    g3_holdout = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g3_final.json"

    return {
        "environment": SLIMEVOLLEY_ENV_ID,
        "protocol_id": GENERATION_3_PROTOCOL_ID,
        "status": PROTOCOL_STATUS,
        "created_by": _protocol_module_name(),
        "prior_generations": [
            {
                "id": "slimevolley-g1",
                "ledger": str(env_ledger_path(SLIMEVOLLEY_ENV_ID)),
                "summary": str(env_summary_path(SLIMEVOLLEY_ENV_ID)),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json"),
                "holdout_seeds": _range_payload(SEED_SPLITS["holdout"]),
                "audit_seeds": _range_payload(SEED_SPLITS["audit"]),
                "rule": "Generation-1 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
            {
                "id": "slimevolley-g2",
                "ledger": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_trials.jsonl"),
                "summary": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_summary.csv"),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g2_final.json"),
                "holdout_seeds": _range_payload(range(4000, 4050)),
                "audit_seeds": _range_payload(range(5000, 5050)),
                "rule": "Generation-2 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
        ],
        "generation_3": {
            "id": GENERATION_3_PROTOCOL_ID,
            "ledger": str(g3_ledger),
            "summary": str(g3_summary),
            "seed_splits": _generation_3_split_payload(),
            "policy_start": "improved",
            "policies": GENERATION_3_POLICIES,
            "development_opponents": GENERATION_3_DEV_OPPONENTS,
            "scalar_search_opponents": GENERATION_3_SEARCH_OPPONENTS,
            "holdout_opponents": GENERATION_3_HOLDOUT_OPPONENTS,
            "artifacts": {
                "search_best": str(g3_search),
                "round_robin": str(g3_tournament),
                "holdout": str(g3_holdout),
            },
        },
        "guardrails": [
            "Use the generation-3 ledger and summary paths for all generation-3 evidence; do not append generation-3 rows to generation-1 or generation-2 ledgers.",
            "Use generation-3 development seeds for diagnosis, structural edits, scalar search, and tournaments.",
            "Do not inspect generation-3 holdout seeds until the policy code, scalar config, opponent pool, and tests are frozen.",
            "Do not use generation-1 or generation-2 holdout results as tuning feedback; treat them only as historical final evidence.",
            "Record tests_run, tests_pass_fail, agent_iterations, code_edits, and failure_analysis on every generation-3 ledger-producing run.",
            "If generation-3 policy work starts, archive the current `improved` policy as a frozen opponent before changing current behavior.",
        ],
        "diagnosis_targets": [
            "built-in opponent serve and return timing without using generation-2 holdout outcomes for tuning",
            "high-arc defense before the ball drops below reachable height",
            "low-ball contact timing without late jump overcommit",
            "recovery to defensive home position after contact",
            "exploitability against archived heuristic opponents",
        ],
        "commands": {
            "regenerate_protocol": "make slimevolley-generation3-protocol",
            "verification_before_edits": "make slimevolley-verify",
            "dev_builtin_trace": (
                "make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_3_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_3_summary.csv "
                "--seed-start 6000 --episodes 50 --trace-window 8 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
            "scalar_search": (
                "make slimevolley-search MAX_CANDIDATES=16 "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_3_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_3_summary.csv "
                "--output experiments/slimevolley/results/search_best_g3_dev.json "
                "--seed-start 6000 --episodes 50 --opponents builtin random initial improved-v0 improved-v2\""
            ),
            "development_tournament": (
                "make slimevolley-tournament SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_3_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_3_summary.csv "
                "--output experiments/slimevolley/results/round_robin_g3_dev.json "
                "--seed-start 6000 --episodes 50\""
            ),
            "final_holdout_once": (
                "make slimevolley-final-eval "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_3_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_3_summary.csv "
                "--output experiments/slimevolley/results/holdout_g3_final.json "
                "--best-config experiments/slimevolley/results/search_best_g3_dev.json "
                "--seed-start 7000 --episodes 50 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
        },
        "promotion_checks": [
            "make verify",
            "make slimevolley-verify",
            _audit_module_command(),
        ],
    }

def generation_4_protocol_payload() -> dict[str, Any]:
    """Return the deterministic SlimeVolley generation-4 protocol payload."""

    g4_ledger = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_trials.jsonl"
    g4_summary = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_summary.csv"
    g4_search = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g4_dev.json"
    g4_tournament = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g4_dev.json"
    g4_holdout = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g4_final.json"

    return {
        "environment": SLIMEVOLLEY_ENV_ID,
        "protocol_id": GENERATION_4_PROTOCOL_ID,
        "status": PROTOCOL_STATUS,
        "created_by": _protocol_module_name(),
        "prior_generations": [
            {
                "id": "slimevolley-g1",
                "ledger": str(env_ledger_path(SLIMEVOLLEY_ENV_ID)),
                "summary": str(env_summary_path(SLIMEVOLLEY_ENV_ID)),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json"),
                "holdout_seeds": _range_payload(SEED_SPLITS["holdout"]),
                "audit_seeds": _range_payload(SEED_SPLITS["audit"]),
                "rule": "Generation-1 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
            {
                "id": "slimevolley-g2",
                "ledger": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_trials.jsonl"),
                "summary": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_summary.csv"),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g2_final.json"),
                "holdout_seeds": _range_payload(range(4000, 4050)),
                "audit_seeds": _range_payload(range(5000, 5050)),
                "rule": "Generation-2 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
            {
                "id": "slimevolley-g3",
                "ledger": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_trials.jsonl"),
                "summary": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_summary.csv"),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g3_final.json"),
                "holdout_seeds": _range_payload(range(7000, 7050)),
                "audit_seeds": _range_payload(range(8000, 8050)),
                "rule": "Generation-3 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
        ],
        "generation_4": {
            "id": GENERATION_4_PROTOCOL_ID,
            "ledger": str(g4_ledger),
            "summary": str(g4_summary),
            "seed_splits": _generation_4_split_payload(),
            "policy_start": "improved",
            "policies": GENERATION_4_POLICIES,
            "development_opponents": GENERATION_4_DEV_OPPONENTS,
            "scalar_search_opponents": GENERATION_4_SEARCH_OPPONENTS,
            "holdout_opponents": GENERATION_4_HOLDOUT_OPPONENTS,
            "artifacts": {
                "search_best": str(g4_search),
                "round_robin": str(g4_tournament),
                "holdout": str(g4_holdout),
            },
        },
        "guardrails": [
            "Use the generation-4 ledger and summary paths for all generation-4 evidence; do not append generation-4 rows to earlier ledgers.",
            "Use generation-4 development seeds for diagnosis, structural edits, scalar search, and tournaments.",
            "Do not inspect generation-4 holdout seeds until the policy code, scalar config, opponent pool, and tests are frozen.",
            "Do not use generation-1, generation-2, or generation-3 holdout results as tuning feedback; treat them only as historical final evidence.",
            "Record tests_run, tests_pass_fail, agent_iterations, code_edits, and failure_analysis on every generation-4 ledger-producing run.",
            "Before any generation-4 policy edit, archive the current `improved` policy as a frozen opponent so previous behavior remains testable.",
        ],
        "diagnosis_targets": [
            "built-in opponent serve and return timing without using any consumed holdout outcomes for tuning",
            "high-arc defense before the ball drops below reachable height",
            "low-ball contact timing without late jump overcommit",
            "recovery to defensive home position after contact",
            "exploitability against archived heuristic opponents including improved-v3, improved-v4, improved-v5, and improved-v6",
        ],
        "commands": {
            "regenerate_protocol": "make slimevolley-generation4-protocol",
            "verification_before_edits": "make slimevolley-verify",
            "dev_builtin_trace": (
                "make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_4_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_4_summary.csv "
                "--seed-start 9000 --episodes 50 --trace-window 8 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
            "scalar_search": (
                "make slimevolley-search MAX_CANDIDATES=16 "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_4_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_4_summary.csv "
                "--output experiments/slimevolley/results/search_best_g4_dev.json "
                "--seed-start 9000 --episodes 50 --opponents builtin random initial improved-v0 improved-v2 improved-v3\""
            ),
            "development_tournament": (
                "make slimevolley-tournament SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_4_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_4_summary.csv "
                "--output experiments/slimevolley/results/round_robin_g4_dev.json "
                "--seed-start 9000 --episodes 50\""
            ),
            "final_holdout_once": (
                "make slimevolley-final-eval "
                "ARGS=\"--policies random initial improved improved-tuned attack rally-serve baseline-rnn "
                "--ledger experiments/slimevolley/results/generation_4_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_4_summary.csv "
                "--output experiments/slimevolley/results/holdout_g4_final.json "
                "--best-config experiments/slimevolley/results/search_best_g4_dev.json "
                "--seed-start 10000 --episodes 50 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
        },
        "promotion_checks": [
            "make verify",
            "make slimevolley-verify",
            _audit_module_command(),
        ],
    }


def generation_5_protocol_payload() -> dict[str, Any]:
    """Return the deterministic SlimeVolley generation-5 protocol payload."""

    g5_ledger = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_5_trials.jsonl"
    g5_summary = env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_5_summary.csv"
    g5_search = env_results_dir(SLIMEVOLLEY_ENV_ID) / "search_best_g5_dev.json"
    g5_tournament = env_results_dir(SLIMEVOLLEY_ENV_ID) / "round_robin_g5_dev.json"
    g5_holdout = env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g5_final.json"

    return {
        "environment": SLIMEVOLLEY_ENV_ID,
        "protocol_id": GENERATION_5_PROTOCOL_ID,
        "status": PROTOCOL_STATUS,
        "created_by": _protocol_module_name(),
        "prior_generations": [
            {
                "id": "slimevolley-g1",
                "ledger": str(env_ledger_path(SLIMEVOLLEY_ENV_ID)),
                "summary": str(env_summary_path(SLIMEVOLLEY_ENV_ID)),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_final.json"),
                "holdout_seeds": _range_payload(SEED_SPLITS["holdout"]),
                "audit_seeds": _range_payload(SEED_SPLITS["audit"]),
                "rule": "Generation-1 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
            {
                "id": "slimevolley-g2",
                "ledger": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_trials.jsonl"),
                "summary": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_2_summary.csv"),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g2_final.json"),
                "holdout_seeds": _range_payload(range(4000, 4050)),
                "audit_seeds": _range_payload(range(5000, 5050)),
                "rule": "Generation-2 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
            {
                "id": "slimevolley-g3",
                "ledger": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_trials.jsonl"),
                "summary": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_3_summary.csv"),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g3_final.json"),
                "holdout_seeds": _range_payload(range(7000, 7050)),
                "audit_seeds": _range_payload(range(8000, 8050)),
                "rule": "Generation-3 holdout is already opened; do not tune, debug, or select policies on those seeds.",
            },
            {
                "id": "slimevolley-g4",
                "ledger": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_trials.jsonl"),
                "summary": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "generation_4_summary.csv"),
                "holdout_artifact": str(env_results_dir(SLIMEVOLLEY_ENV_ID) / "holdout_g4_final.json"),
                "holdout_seeds": _range_payload(range(10000, 10050)),
                "audit_seeds": _range_payload(range(11000, 11050)),
                "rule": "Generation-4 holdout is already opened; do not tune, debug, or select policies on those seeds. Generation-4 audit seeds remain reserved and unavailable for tuning.",
            },
        ],
        "generation_5": {
            "id": GENERATION_5_PROTOCOL_ID,
            "ledger": str(g5_ledger),
            "summary": str(g5_summary),
            "seed_splits": _generation_5_split_payload(),
            "policy_start": "rally-serve",
            "policies": GENERATION_5_POLICIES,
            "development_opponents": GENERATION_5_DEV_OPPONENTS,
            "scalar_search_opponents": GENERATION_5_SEARCH_OPPONENTS,
            "holdout_opponents": GENERATION_5_HOLDOUT_OPPONENTS,
            "artifacts": {
                "search_best": str(g5_search),
                "round_robin": str(g5_tournament),
                "holdout": str(g5_holdout),
            },
        },
        "guardrails": [
            "Use the generation-5 ledger and summary paths for all generation-5 evidence; do not append generation-5 rows to earlier ledgers.",
            "Use generation-5 development seeds for diagnosis, structural edits, scalar search, and tournaments.",
            "Do not inspect generation-5 holdout seeds until the policy code, scalar config, opponent pool, and tests are frozen.",
            "Do not use generation-1, generation-2, generation-3, or generation-4 holdout results as tuning feedback; treat them only as historical final evidence.",
            "Do not use generation-4 audit seeds for tuning; they remain reserved even though generation-4 holdout has been consumed.",
            "Record tests_run, tests_pass_fail, agent_iterations, code_edits, and failure_analysis on every generation-5 ledger-producing run.",
            "Any candidate that beats `baseline-rnn` on built-in development seeds must also pass the fixed development opponent pool before any generation-5 holdout use.",
        ],
        "diagnosis_targets": [
            "fresh post-generation-4 built-in opponent gap on development seeds without using consumed holdout outcomes for tuning",
            "whether `rally-serve` relies on draws rather than wins under new development seeds",
            "serve/return timing, high-arc defense, and low-ball contact timing from generation-5 traces",
            "robustness against archived heuristic opponents including improved-v4, improved-v5, improved-v6, attack, and rally-serve",
            "candidate exploitability versus the packaged `baseline-rnn` comparator before any holdout use",
        ],
        "commands": {
            "regenerate_protocol": "make slimevolley-generation5-protocol",
            "verification_before_edits": "make slimevolley-verify",
            "dev_builtin_trace": (
                "make slimevolley-eval POLICY=rally-serve OPPONENT=builtin SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_5_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_5_summary.csv "
                "--seed-start 12000 --episodes 50 --trace-window 8 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
            "development_rnn_comparator": (
                "make slimevolley-eval POLICY=baseline-rnn OPPONENT=builtin SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_5_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_5_summary.csv "
                "--seed-start 12000 --episodes 50 --trace-window 8 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
            "scalar_search": (
                "make slimevolley-search MAX_CANDIDATES=16 "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_5_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_5_summary.csv "
                "--output experiments/slimevolley/results/search_best_g5_dev.json "
                "--seed-start 12000 --episodes 50 --opponents builtin random initial improved-v0 improved-v2 improved-v3 improved-v5 improved-v6\""
            ),
            "development_tournament": (
                "make slimevolley-tournament SPLIT=dev "
                "ARGS=\"--ledger experiments/slimevolley/results/generation_5_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_5_summary.csv "
                "--output experiments/slimevolley/results/round_robin_g5_dev.json "
                "--seed-start 12000 --episodes 50\""
            ),
            "final_holdout_once": (
                "make slimevolley-final-eval "
                "ARGS=\"--policies random initial improved improved-tuned attack rally-serve net-pressure baseline-rnn "
                "--ledger experiments/slimevolley/results/generation_5_trials.jsonl "
                "--summary experiments/slimevolley/results/generation_5_summary.csv "
                "--output experiments/slimevolley/results/holdout_g5_final.json "
                "--best-config experiments/slimevolley/results/search_best_g5_dev.json "
                "--seed-start 13000 --episodes 50 "
                "--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass\""
            ),
        },
        "promotion_checks": [
            "make verify",
            "make slimevolley-verify",
            _audit_module_command(),
        ],
    }



def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _column in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return lines


def render_generation_2_protocol_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render a human-readable Markdown version of the generation-2 protocol."""

    payload = payload or generation_2_protocol_payload()
    generation = payload["generation_2"]
    seed_rows = [
        {"split": split, **spec}
        for split, spec in generation["seed_splits"].items()
    ]
    command_rows = [
        {"name": name, "command": command}
        for name, command in payload["commands"].items()
    ]
    lines = [
        "# SlimeVolley Generation-2 Protocol",
        "",
        f"Protocol ID: `{payload['protocol_id']}`",
        f"Status: `{payload['status']}`",
        "",
        "This artifact predeclares the next SlimeVolley experiment generation. It is generated without running evaluation, search, tournaments, or holdout evaluation.",
        "",
        "## Prior Holdout Lock",
        "",
        payload["source_generation"]["rule"],
        "",
        f"- Generation-1 holdout artifact: `{payload['source_generation']['holdout_artifact']}`",
        f"- Generation-1 holdout seeds: `{payload['source_generation']['holdout_seeds']['label']}`",
        "",
        "## Generation-2 Seed Ranges",
        "",
        *_markdown_table(seed_rows, ["split", "label", "episodes", "purpose"]),
        "",
        "## Opponent Protocol",
        "",
        f"- Policies: `{', '.join(generation['policies'])}`",
        f"- Development opponents: `{', '.join(generation['development_opponents'])}`",
        f"- Scalar-search opponents: `{', '.join(generation['scalar_search_opponents'])}`",
        f"- Holdout opponents: `{', '.join(generation['holdout_opponents'])}`",
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.extend([
        "",
        "## Diagnosis Targets",
        "",
    ])
    lines.extend(f"- {item}" for item in payload["diagnosis_targets"])
    lines.extend([
        "",
        "## Commands",
        "",
        *_markdown_table(command_rows, ["name", "command"]),
        "",
        "## Promotion Checks",
        "",
    ])
    lines.extend(f"- `{item}`" for item in payload["promotion_checks"])
    lines.append("")
    return "\n".join(lines)




def render_generation_3_protocol_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render a human-readable Markdown version of the generation-3 protocol."""

    payload = payload or generation_3_protocol_payload()
    generation = payload["generation_3"]
    seed_rows = [
        {"split": split, **spec}
        for split, spec in generation["seed_splits"].items()
    ]
    command_rows = [
        {"name": name, "command": command}
        for name, command in payload["commands"].items()
    ]
    lines = [
        "# SlimeVolley Generation-3 Protocol",
        "",
        f"Protocol ID: `{payload['protocol_id']}`",
        f"Status: `{payload['status']}`",
        "",
        "This artifact predeclares the next SlimeVolley experiment generation. It is generated without running evaluation, search, tournaments, or holdout evaluation.",
        "",
        "## Prior Holdout Locks",
        "",
    ]
    for prior_generation in payload["prior_generations"]:
        lines.extend(
            [
                prior_generation["rule"],
                f"- {prior_generation['id']} holdout artifact: `{prior_generation['holdout_artifact']}`",
                f"- {prior_generation['id']} holdout seeds: `{prior_generation['holdout_seeds']['label']}`",
                "",
            ]
        )
    lines.extend([
        "## Generation-3 Seed Ranges",
        "",
        *_markdown_table(seed_rows, ["split", "label", "episodes", "purpose"]),
        "",
        "## Opponent Protocol",
        "",
        f"- Policies: `{', '.join(generation['policies'])}`",
        f"- Development opponents: `{', '.join(generation['development_opponents'])}`",
        f"- Scalar-search opponents: `{', '.join(generation['scalar_search_opponents'])}`",
        f"- Holdout opponents: `{', '.join(generation['holdout_opponents'])}`",
        "",
        "## Guardrails",
        "",
    ])
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.extend([
        "",
        "## Diagnosis Targets",
        "",
    ])
    lines.extend(f"- {item}" for item in payload["diagnosis_targets"])
    lines.extend([
        "",
        "## Commands",
        "",
        *_markdown_table(command_rows, ["name", "command"]),
        "",
        "## Promotion Checks",
        "",
    ])
    lines.extend(f"- `{item}`" for item in payload["promotion_checks"])
    lines.append("")
    return "\n".join(lines)

def render_generation_4_protocol_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render a human-readable Markdown version of the generation-4 protocol."""

    payload = payload or generation_4_protocol_payload()
    generation = payload["generation_4"]
    seed_rows = [
        {"split": split, **spec}
        for split, spec in generation["seed_splits"].items()
    ]
    command_rows = [
        {"name": name, "command": command}
        for name, command in payload["commands"].items()
    ]
    lines = [
        "# SlimeVolley Generation-4 Protocol",
        "",
        f"Protocol ID: `{payload['protocol_id']}`",
        f"Status: `{payload['status']}`",
        "",
        "This artifact predeclares the next SlimeVolley experiment generation. It is generated without running evaluation, search, tournaments, or holdout evaluation.",
        "",
        "## Prior Holdout Locks",
        "",
    ]
    for prior_generation in payload["prior_generations"]:
        lines.extend(
            [
                prior_generation["rule"],
                f"- {prior_generation['id']} holdout artifact: `{prior_generation['holdout_artifact']}`",
                f"- {prior_generation['id']} holdout seeds: `{prior_generation['holdout_seeds']['label']}`",
                "",
            ]
        )
    lines.extend([
        "## Generation-4 Seed Ranges",
        "",
        *_markdown_table(seed_rows, ["split", "label", "episodes", "purpose"]),
        "",
        "## Opponent Protocol",
        "",
        f"- Policies: `{', '.join(generation['policies'])}`",
        f"- Development opponents: `{', '.join(generation['development_opponents'])}`",
        f"- Scalar-search opponents: `{', '.join(generation['scalar_search_opponents'])}`",
        f"- Holdout opponents: `{', '.join(generation['holdout_opponents'])}`",
        "",
        "## Guardrails",
        "",
    ])
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.extend([
        "",
        "## Diagnosis Targets",
        "",
    ])
    lines.extend(f"- {item}" for item in payload["diagnosis_targets"])
    lines.extend([
        "",
        "## Commands",
        "",
        *_markdown_table(command_rows, ["name", "command"]),
        "",
        "## Promotion Checks",
        "",
    ])
    lines.extend(f"- `{item}`" for item in payload["promotion_checks"])
    lines.append("")
    return "\n".join(lines)


def render_generation_5_protocol_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render a human-readable Markdown version of the generation-5 protocol."""

    payload = payload or generation_5_protocol_payload()
    generation = payload["generation_5"]
    seed_rows = [
        {"split": split, **spec}
        for split, spec in generation["seed_splits"].items()
    ]
    command_rows = [
        {"name": name, "command": command}
        for name, command in payload["commands"].items()
    ]
    lines = [
        "# SlimeVolley Generation-5 Protocol",
        "",
        f"Protocol ID: `{payload['protocol_id']}`",
        f"Status: `{payload['status']}`",
        "",
        "This artifact predeclares the next SlimeVolley experiment generation after generation-4 holdout was consumed. It is generated without running evaluation, search, tournaments, or holdout evaluation.",
        "",
        "## Prior Holdout Locks",
        "",
    ]
    for prior_generation in payload["prior_generations"]:
        lines.extend(
            [
                prior_generation["rule"],
                f"- {prior_generation['id']} holdout artifact: `{prior_generation['holdout_artifact']}`",
                f"- {prior_generation['id']} holdout seeds: `{prior_generation['holdout_seeds']['label']}`",
                "",
            ]
        )
    lines.extend([
        "## Generation-5 Seed Ranges",
        "",
        *_markdown_table(seed_rows, ["split", "label", "episodes", "purpose"]),
        "",
        "## Opponent Protocol",
        "",
        f"- Policies: `{', '.join(generation['policies'])}`",
        f"- Development opponents: `{', '.join(generation['development_opponents'])}`",
        f"- Scalar-search opponents: `{', '.join(generation['scalar_search_opponents'])}`",
        f"- Holdout opponents: `{', '.join(generation['holdout_opponents'])}`",
        "",
        "## Guardrails",
        "",
    ])
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.extend([
        "",
        "## Diagnosis Targets",
        "",
    ])
    lines.extend(f"- {item}" for item in payload["diagnosis_targets"])
    lines.extend([
        "",
        "## Commands",
        "",
        *_markdown_table(command_rows, ["name", "command"]),
        "",
        "## Promotion Checks",
        "",
    ])
    lines.extend(f"- `{item}`" for item in payload["promotion_checks"])
    lines.append("")
    return "\n".join(lines)



def write_generation_2_protocol(
    *,
    json_path: Path = DEFAULT_PROTOCOL_JSON_PATH,
    markdown_path: Path = DEFAULT_PROTOCOL_REPORT_PATH,
) -> dict[str, Path]:
    """Write deterministic generation-2 protocol JSON and Markdown artifacts."""

    payload = generation_2_protocol_payload()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_generation_2_protocol_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}




def write_generation_3_protocol(
    *,
    json_path: Path = DEFAULT_GENERATION_3_PROTOCOL_JSON_PATH,
    markdown_path: Path = DEFAULT_GENERATION_3_PROTOCOL_REPORT_PATH,
) -> dict[str, Path]:
    """Write deterministic generation-3 protocol JSON and Markdown artifacts."""

    payload = generation_3_protocol_payload()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_generation_3_protocol_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}

def write_generation_4_protocol(
    *,
    json_path: Path = DEFAULT_GENERATION_4_PROTOCOL_JSON_PATH,
    markdown_path: Path = DEFAULT_GENERATION_4_PROTOCOL_REPORT_PATH,
) -> dict[str, Path]:
    """Write deterministic generation-4 protocol JSON and Markdown artifacts."""

    payload = generation_4_protocol_payload()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_generation_4_protocol_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}



def write_generation_5_protocol(
    *,
    json_path: Path = DEFAULT_GENERATION_5_PROTOCOL_JSON_PATH,
    markdown_path: Path = DEFAULT_GENERATION_5_PROTOCOL_REPORT_PATH,
) -> dict[str, Path]:
    """Write deterministic generation-5 protocol JSON and Markdown artifacts."""

    payload = generation_5_protocol_payload()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_generation_5_protocol_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", type=int, choices=(2, 3, 4, 5), default=2)
    parser.add_argument("--json-output", type=Path, default=None)
    parser.add_argument("--markdown-output", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    if args.generation == 5:
        paths = write_generation_5_protocol(
            json_path=args.json_output or DEFAULT_GENERATION_5_PROTOCOL_JSON_PATH,
            markdown_path=args.markdown_output or DEFAULT_GENERATION_5_PROTOCOL_REPORT_PATH,
        )
    elif args.generation == 4:
        paths = write_generation_4_protocol(
            json_path=args.json_output or DEFAULT_GENERATION_4_PROTOCOL_JSON_PATH,
            markdown_path=args.markdown_output or DEFAULT_GENERATION_4_PROTOCOL_REPORT_PATH,
        )
    elif args.generation == 3:
        paths = write_generation_3_protocol(
            json_path=args.json_output or DEFAULT_GENERATION_3_PROTOCOL_JSON_PATH,
            markdown_path=args.markdown_output or DEFAULT_GENERATION_3_PROTOCOL_REPORT_PATH,
        )
    else:
        paths = write_generation_2_protocol(
            json_path=args.json_output or DEFAULT_PROTOCOL_JSON_PATH,
            markdown_path=args.markdown_output or DEFAULT_PROTOCOL_REPORT_PATH,
        )
    if args.format == "json":
        print(json.dumps({key: str(value) for key, value in paths.items()}, indent=2, sort_keys=True))
    else:
        print(paths["json"])
        print(paths["markdown"])


if __name__ == "__main__":
    main()
