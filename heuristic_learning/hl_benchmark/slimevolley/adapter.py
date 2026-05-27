"""Optional SlimeVolley compatibility adapter and episode runner."""

from __future__ import annotations

import importlib
import importlib.metadata as metadata
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from hl_benchmark.policies.base import BasePolicy


SLIMEVOLLEY_ENV_ID = "SlimeVolley-v0"


class SlimeVolleyDependencyError(RuntimeError):
    """Raised when the optional legacy SlimeVolley stack is unavailable."""


@dataclass(frozen=True)
class SlimeVolleyEpisodeResult:
    """Compact diagnostics for one SlimeVolley episode."""

    seed: int
    score: float
    steps: int
    outcome: str
    lives: int | None
    opponent_lives: int | None
    life_difference: int | None
    action_counts: dict[str, int] = field(default_factory=dict)
    opponent_action_counts: dict[str, int] = field(default_factory=dict)
    point_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not_installed"


def check_slimevolley_available() -> tuple[bool, str]:
    """Return whether the optional legacy SlimeVolley stack is importable."""

    try:
        importlib.import_module("gym")
        importlib.import_module("slimevolleygym")
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, "available"


def make_slimevolley_env(env_id: str = SLIMEVOLLEY_ENV_ID) -> Any:
    """Create the legacy Gym SlimeVolley environment."""

    ok, message = check_slimevolley_available()
    if not ok:
        raise SlimeVolleyDependencyError(
            "SlimeVolley requires optional legacy dependencies: gym and slimevolleygym. "
            f"Current status: {message}"
        )
    gym = importlib.import_module("gym")
    importlib.import_module("slimevolleygym")
    return gym.make(env_id)


def reset_slimevolley_env(env: Any, seed: int) -> tuple[Any, dict[str, Any]]:
    """Reset old-Gym or Gymnasium-like SlimeVolley envs with deterministic seed handling."""

    if hasattr(env, "seed"):
        env.seed(seed)
    try:
        result = env.reset(seed=seed)
    except TypeError:
        result = env.reset()
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
        return result
    return result, {}


def step_slimevolley_env(env: Any, action: Any, opponent_action: Any | None) -> tuple[Any, float, bool, dict[str, Any]]:
    """Step old-Gym or Gymnasium-like SlimeVolley envs."""

    if opponent_action is None:
        result = env.step(action)
    else:
        result = env.step(action, opponent_action)
    if isinstance(result, tuple) and len(result) == 5:
        obs, reward, terminated, truncated, info = result
        return obs, float(reward), bool(terminated or truncated), dict(info)
    if isinstance(result, tuple) and len(result) == 4:
        obs, reward, done, info = result
        return obs, float(reward), bool(done), dict(info)
    raise ValueError(f"unexpected SlimeVolley step result shape: {type(result).__name__}")


def _action_key(action: Any) -> str:
    values = np.asarray(action if action is not None else [0, 0, 0], dtype=int).reshape(-1)[:3]
    return "".join(str(int(value > 0)) for value in values)


def _policy_diagnostics(policy: BasePolicy) -> dict[str, Any] | None:
    diagnostics = getattr(policy, "diagnostics", None)
    if not callable(diagnostics):
        return None
    payload = diagnostics()
    return payload if isinstance(payload, dict) and payload else None


def _state_summary(obs: Any) -> dict[str, float | int]:
    values = np.asarray(obs, dtype=float).reshape(-1)
    if values.size < 12:
        return {"raw_obs_size": int(values.size)}
    x, y, vx, vy, ball_x, ball_y, ball_vx, ball_vy, opp_x, opp_y, opp_vx, opp_vy = values[:12]
    return {
        "agent_x": float(x),
        "agent_y": float(y),
        "agent_vx": float(vx),
        "agent_vy": float(vy),
        "ball_x": float(ball_x),
        "ball_y": float(ball_y),
        "ball_vx": float(ball_vx),
        "ball_vy": float(ball_vy),
        "opponent_x": float(opp_x),
        "opponent_y": float(opp_y),
        "opponent_vx": float(opp_vx),
        "opponent_vy": float(opp_vy),
    }


def _trace_frame(
    *,
    step: int,
    obs: Any,
    action: Any,
    opponent_action: Any | None,
    policy_diagnostics: dict[str, Any] | None = None,
    opponent_diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    frame = {
        "step": int(step),
        "action": _action_key(action),
        "opponent_action": None if opponent_action is None else _action_key(opponent_action),
        "state": _state_summary(obs),
    }
    if policy_diagnostics:
        frame["policy_diagnostics"] = policy_diagnostics
    if opponent_diagnostics:
        frame["opponent_diagnostics"] = opponent_diagnostics
    return frame


def _event_from_obs(
    *,
    step: int,
    reward: float,
    obs: Any,
    action: Any,
    opponent_action: Any | None,
    info: dict[str, Any],
    pre_event_trace: list[dict[str, Any]] | None = None,
    policy_diagnostics: dict[str, Any] | None = None,
    opponent_diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = {
        "step": int(step),
        "reward": float(reward),
        "outcome": "point_won" if reward > 0 else "point_lost",
        "action": _action_key(action),
        "opponent_action": None if opponent_action is None else _action_key(opponent_action),
        "lives": info.get("ale.lives"),
        "opponent_lives": info.get("ale.otherLives"),
        "state_before_step": _state_summary(obs),
    }
    if pre_event_trace:
        event["pre_event_trace"] = pre_event_trace
    if policy_diagnostics:
        event["policy_diagnostics"] = policy_diagnostics
    if opponent_diagnostics:
        event["opponent_diagnostics"] = opponent_diagnostics
    return event


def _outcome(score: float, lives: int | None, opponent_lives: int | None) -> str:
    if lives is not None and opponent_lives is not None and lives != opponent_lives:
        return "win" if lives > opponent_lives else "loss"
    if score > 0:
        return "win"
    if score < 0:
        return "loss"
    return "draw"


def run_slimevolley_episode(
    *,
    env: Any,
    policy: BasePolicy,
    opponent: BasePolicy,
    seed: int,
    max_steps: int | None = None,
    trace_window: int = 0,
) -> SlimeVolleyEpisodeResult:
    """Run one SlimeVolley episode and collect lightweight diagnostics."""

    if hasattr(env, "action_space") and hasattr(env.action_space, "seed"):
        env.action_space.seed(seed)
    policy.reset(seed)
    opponent.reset(seed + 1)
    if getattr(opponent, "uses_env_builtin", False) and hasattr(getattr(env, "policy", None), "reset"):
        env.policy.reset()
    obs, info = reset_slimevolley_env(env, seed)
    opponent_obs = info.get("otherObs", obs)
    score = 0.0
    steps = 0
    done = False
    lives: int | None = None
    opponent_lives: int | None = None
    action_counts: dict[str, int] = {}
    opponent_action_counts: dict[str, int] = {}
    point_events: list[dict[str, Any]] = []
    trace_history: deque[dict[str, Any]] | None = deque(maxlen=trace_window) if trace_window > 0 else None

    while not done:
        obs_before = obs
        action = policy.act(obs)
        policy_diagnostics = _policy_diagnostics(policy)
        if getattr(opponent, "uses_env_builtin", False):
            opponent_action = None
            opponent_diagnostics = None
        else:
            opponent_action = opponent.act(opponent_obs)
            opponent_diagnostics = _policy_diagnostics(opponent)
            opponent_action_counts[_action_key(opponent_action)] = opponent_action_counts.get(_action_key(opponent_action), 0) + 1
        action_counts[_action_key(action)] = action_counts.get(_action_key(action), 0) + 1
        if trace_history is not None:
            trace_history.append(
                _trace_frame(
                    step=steps,
                    obs=obs_before,
                    action=action,
                    opponent_action=opponent_action,
                    policy_diagnostics=policy_diagnostics,
                    opponent_diagnostics=opponent_diagnostics,
                )
            )
        obs, reward, done, info = step_slimevolley_env(env, action, opponent_action)
        if reward != 0:
            point_events.append(
                _event_from_obs(
                    step=steps,
                    reward=reward,
                    obs=obs_before,
                    action=action,
                    opponent_action=opponent_action,
                    info=info,
                    pre_event_trace=list(trace_history) if trace_history is not None else None,
                    policy_diagnostics=policy_diagnostics,
                    opponent_diagnostics=opponent_diagnostics,
                )
            )
        score += reward
        steps += 1
        opponent_obs = info.get("otherObs", opponent_obs)
        lives = info.get("ale.lives", lives)
        opponent_lives = info.get("ale.otherLives", opponent_lives)
        if max_steps is not None and steps >= max_steps:
            done = True

    life_difference = None
    if lives is not None and opponent_lives is not None:
        life_difference = int(lives) - int(opponent_lives)
    return SlimeVolleyEpisodeResult(
        seed=seed,
        score=score,
        steps=steps,
        outcome=_outcome(score, lives, opponent_lives),
        lives=None if lives is None else int(lives),
        opponent_lives=None if opponent_lives is None else int(opponent_lives),
        life_difference=life_difference,
        action_counts=action_counts,
        opponent_action_counts=opponent_action_counts,
        point_events=point_events,
    )


def dependency_versions() -> dict[str, str]:
    """Return exact optional dependency versions for SlimeVolley reports."""

    return {
        "gym": _package_version("gym"),
        "numpy": _package_version("numpy"),
        "opencv-python": _package_version("opencv-python"),
        "slimevolleygym": _package_version("slimevolleygym"),
    }
