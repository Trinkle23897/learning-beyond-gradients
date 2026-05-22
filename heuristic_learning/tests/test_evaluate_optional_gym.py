from __future__ import annotations

import pytest

from hl_benchmark.evaluate import evaluate_policy
from hl_benchmark.envs import benchmark_env_ids, make_env
from hl_benchmark.policies import make_policy


gymnasium = pytest.importorskip("gymnasium")


def _make_or_skip(env_id: str):
    try:
        return make_env(env_id)
    except Exception as exc:
        pytest.skip(f"{env_id} unavailable: {exc}")


def test_policy_actions_fit_gymnasium_spaces() -> None:
    for env_id in benchmark_env_ids():
        env = _make_or_skip(env_id)
        try:
            obs, _info = env.reset(seed=0)
            for policy_name in ["initial", "improved", "random"]:
                policy = make_policy(env_id, policy_name, action_space=env.action_space)
                policy.reset(0)
                action = policy.act(obs)
                assert env.action_space.contains(action), (env_id, policy_name, action)
        finally:
            env.close()


def test_cartpole_evaluation_is_deterministic_without_ledger() -> None:
    _make_or_skip("CartPole-v1").close()
    first = evaluate_policy(
        env_id="CartPole-v1",
        policy_name="improved",
        split="smoke",
        ledger_path=None,
        summary_path=None,
    )
    second = evaluate_policy(
        env_id="CartPole-v1",
        policy_name="improved",
        split="smoke",
        ledger_path=None,
        summary_path=None,
    )
    assert first["per_episode"] == second["per_episode"]
    assert first["score_stats"] == second["score_stats"]


def test_cartpole_regression_smoke_preserves_solved_behavior() -> None:
    _make_or_skip("CartPole-v1").close()
    for policy_name in ["initial", "improved"]:
        entry = evaluate_policy(
            env_id="CartPole-v1",
            policy_name=policy_name,
            split="smoke",
            ledger_path=None,
            summary_path=None,
        )
        assert entry["pass_fail"] == "pass"
        assert entry["score_stats"]["min"] == 500.0


def test_mountain_car_structural_regression_smoke() -> None:
    _make_or_skip("MountainCar-v0").close()
    initial = evaluate_policy(
        env_id="MountainCar-v0",
        policy_name="initial",
        split="smoke",
        ledger_path=None,
        summary_path=None,
    )
    improved = evaluate_policy(
        env_id="MountainCar-v0",
        policy_name="improved",
        split="smoke",
        ledger_path=None,
        summary_path=None,
    )
    assert improved["pass_fail"] == "pass"
    assert improved["score_stats"]["mean"] >= initial["score_stats"]["mean"]
    assert improved["score_stats"]["mean"] >= -120.0

