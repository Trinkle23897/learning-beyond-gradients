from __future__ import annotations

import numpy as np

from hl_benchmark.policies import make_policy


def test_cartpole_golden_actions() -> None:
    initial = make_policy("CartPole-v1", "initial")
    improved = make_policy("CartPole-v1", "improved")

    assert initial.act(np.asarray([0.0, 0.0, 0.10, 0.0])) == 1
    assert initial.act(np.asarray([0.0, 0.0, -0.10, 0.0])) == 0
    assert improved.act(np.asarray([1.20, 0.0, 0.0, 0.0])) == 0
    assert improved.act(np.asarray([-1.20, 0.0, 0.0, 0.0])) == 1


def test_mountain_car_golden_actions() -> None:
    initial = make_policy("MountainCar-v0", "initial")
    improved = make_policy("MountainCar-v0", "improved")

    assert initial.act(np.asarray([-0.5, -0.01])) == 0
    assert initial.act(np.asarray([-0.5, 0.01])) == 2

    for state, expected_action in [
        ([-1.10, -0.01], 2),
        ([0.00, 0.001], 0),
        ([-0.50, 0.01], 1),
    ]:
        improved.reset(0)
        assert improved.act(np.asarray(state)) == expected_action


def test_policy_outputs_are_basic_valid_values() -> None:
    cases = [
        ("Acrobot-v1", np.asarray([1.0, 0.0, 1.0, 0.0, 0.5, -0.1]), {0, 1, 2}),
        ("LunarLander-v3", np.zeros(8), {0, 1, 2, 3}),
    ]
    for env_id, obs, valid in cases:
        for policy_name in ["initial", "improved"]:
            action = make_policy(env_id, policy_name).act(obs)
            assert action in valid


def test_acrobot_tree_policy_outputs_valid_actions() -> None:
    policy = make_policy("Acrobot-v1", "tree")
    action = policy.act(np.asarray([1.0, 0.0, 1.0, 0.0, 0.5, -0.1]))
    assert action in {0, 1, 2}
    config = policy.config()
    assert config["policy_type"] == "acrobot_distilled_decision_tree"
    assert config["node_count"] == 223


def test_bipedal_policy_shape_and_range() -> None:
    obs = np.zeros(24)
    obs[8] = 1.0
    for policy_name in ["initial", "improved"]:
        policy = make_policy("BipedalWalker-v3", policy_name)
        action = policy.act(obs)
        assert action.shape == (4,)
        assert np.all(action >= -1.0)
        assert np.all(action <= 1.0)



def test_policy_factory_returns_environment_specific_classes() -> None:
    expected_modules = {
        ("CartPole-v1", "initial"): "hl_benchmark.policies.cartpole",
        ("MountainCar-v0", "initial"): "hl_benchmark.policies.mountain_car",
        ("Acrobot-v1", "initial"): "hl_benchmark.policies.acrobot",
        ("Acrobot-v1", "tree"): "hl_benchmark.policies.acrobot",
        ("LunarLander-v3", "initial"): "hl_benchmark.policies.lunar_lander",
        ("BipedalWalker-v3", "initial"): "hl_benchmark.policies.bipedal_walker",
    }
    for (env_id, policy_name), module_name in expected_modules.items():
        policy = make_policy(env_id, policy_name)
        assert policy.__class__.__module__ == module_name
