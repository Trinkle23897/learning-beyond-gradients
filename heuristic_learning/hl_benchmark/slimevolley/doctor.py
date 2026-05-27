"""Write SlimeVolley environment diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from hl_benchmark.artifacts import env_results_dir
from hl_benchmark.envs import discover_runtime_metadata
from hl_benchmark.slimevolley.adapter import (
    SLIMEVOLLEY_ENV_ID,
    check_slimevolley_available,
    dependency_versions,
    make_slimevolley_env,
    reset_slimevolley_env,
)


def _native_step_api_label(result: Any) -> str:
    if isinstance(result, tuple) and len(result) == 4:
        return "legacy-4-tuple"
    if isinstance(result, tuple) and len(result) == 5:
        return "gymnasium-5-tuple"
    return f"unexpected-{type(result).__name__}"


def _safe_native_step_probe(env: Any, *, other_action: bool) -> str:
    action = np.asarray([0, 0, 0], dtype=np.int8)
    try:
        if other_action:
            result = env.step(action, action)
        else:
            result = env.step(action)
    except Exception as exc:  # pragma: no cover - depends on optional env internals.
        return f"error:{type(exc).__name__}: {exc}"
    return _native_step_api_label(result)


def _seed_api_probe(env: Any) -> dict[str, Any]:
    probe_seed = 12345
    try:
        first_obs, _first_info = reset_slimevolley_env(env, probe_seed)
        second_obs, _second_info = reset_slimevolley_env(env, probe_seed)
        first = np.asarray(first_obs, dtype=float).reshape(-1)
        second = np.asarray(second_obs, dtype=float).reshape(-1)
        same_shape = first.shape == second.shape
        same_values = bool(same_shape and np.allclose(first, second, equal_nan=True))
    except Exception as exc:  # pragma: no cover - depends on optional env internals.
        return {
            "seed_api_behavior": f"error:{type(exc).__name__}: {exc}",
            "same_seed_reset_observation_equal": False,
            "seed_probe_seed": probe_seed,
        }
    return {
        "seed_api_behavior": "env.seed(seed) before reset; reset(seed=seed) if accepted, otherwise reset()",
        "same_seed_reset_observation_equal": same_values,
        "seed_probe_seed": probe_seed,
    }


def collect_slimevolley_metadata(env_id: str = SLIMEVOLLEY_ENV_ID) -> dict[str, Any]:
    """Collect package, API, and space metadata without hiding dependency gaps."""

    available, message = check_slimevolley_available()
    payload: dict[str, Any] = {
        "environment_id": env_id,
        "status": "available" if available else "unavailable",
        "message": message,
        "packages": dependency_versions(),
        "runtime_metadata": discover_runtime_metadata(),
        "expected_observation_space": "Box(12)",
        "expected_action_space": "MultiBinary(3)",
        "expected_step_api": "legacy Gym: obs, reward, done, info; multi-agent step(action, otherAction)",
        "reward_semantics": "+1 when opponent loses a life, -1 when agent loses a life, episode ends at 5 lives or 3000 steps.",
        "seed_api_behavior": "not probed; environment unavailable",
        "same_seed_reset_observation_equal": False,
        "observed_step_api": "unavailable",
        "multiagent_step_api_observed": "unavailable",
        "seed_probe_seed": None,
    }
    if not available:
        return payload
    env = make_slimevolley_env(env_id)
    try:
        payload.update(
            {
                "observation_space": repr(env.observation_space),
                "action_space": repr(env.action_space),
                "max_episode_steps": getattr(env, "t_limit", "unavailable"),
                "has_seed_method": hasattr(env, "seed"),
                "has_multiagent_other_action": True,
            }
        )
        payload.update(_seed_api_probe(env))
        reset_slimevolley_env(env, 0)
        payload["observed_step_api"] = _safe_native_step_probe(env, other_action=False)
        reset_slimevolley_env(env, 0)
        payload["multiagent_step_api_observed"] = _safe_native_step_probe(env, other_action=True)
    finally:
        env.close()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-id", default=SLIMEVOLLEY_ENV_ID)
    parser.add_argument(
        "--output",
        type=Path,
        default=env_results_dir(SLIMEVOLLEY_ENV_ID) / "environment_diagnostics.json",
    )
    args = parser.parse_args()
    metadata = collect_slimevolley_metadata(args.env_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": metadata["status"], "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
