from __future__ import annotations

import numpy as np
import pytest

from hl_benchmark.environments.base import EnvSpec, EnvironmentRegistration
from hl_benchmark.policies import make_policy
import hl_benchmark.policies.factory as factory_module


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



def test_policy_factory_rejects_env_specific_policy_leakage() -> None:
    with pytest.raises(ValueError, match="CartPole-v1 does not support policy"):
        make_policy("CartPole-v1", "baseline-rnn")
    with pytest.raises(ValueError, match="LunarLander-v3 does not support policy"):
        make_policy("LunarLander-v3", "tree")
    with pytest.raises(ValueError, match="SlimeVolley-v0 does not support policy"):
        make_policy("SlimeVolley-v0", "tree")


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


def test_policy_factory_dispatches_to_registered_policy_module(tmp_path, monkeypatch) -> None:
    module_path = tmp_path / "fake_policy_env.py"
    module_path.write_text(
        "from hl_benchmark.policies.base import BasePolicy\n"
        "SUPPORTED_POLICY_NAMES = ('local',)\n"
        "class FakePolicy(BasePolicy):\n"
        "    policy_name = 'local'\n"
        "    def __init__(self, config):\n"
        "        self._config = config or {}\n"
        "    def act(self, obs):\n"
        "        return self._config.get('action', 3)\n"
        "    def config(self):\n"
        "        return dict(self._config)\n"
        "def make_policy(policy_name, *, config=None):\n"
        "    if policy_name not in SUPPORTED_POLICY_NAMES:\n"
        "        raise ValueError(policy_name)\n"
        "    return FakePolicy(config)\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    registration = EnvironmentRegistration(
        key="fake_policy_env",
        policy_module="fake_policy_env",
        artifact_slug="fake_policy_env",
        spec=EnvSpec(
            env_id="FakePolicyEnv-v0",
            category="test",
            observation_summary="test",
            action_summary="test",
            reward_interpretation="test",
            episode_length=1,
            success_target=1.0,
            initial_policy="test",
            known_failure_modes=("test",),
            docs_url="test",
        ),
    )
    monkeypatch.setattr(factory_module, "ALL_REGISTRATIONS", (registration,))
    monkeypatch.setattr(factory_module, "registration_for", lambda _env_id: registration)

    policy = factory_module.make_policy(
        "FakePolicyEnv-v0",
        "local",
        config={"action": 7},
    )

    assert policy.__class__.__module__ == "fake_policy_env"
    assert policy.act(None) == 7


def test_policy_modules_expose_local_factory_contract() -> None:
    for registration in factory_module.ALL_REGISTRATIONS:
        module = factory_module._policy_module(registration.policy_module)
        supported = factory_module._supported_policy_names(module)
        assert supported
        assert callable(getattr(module, "make_policy", None))
