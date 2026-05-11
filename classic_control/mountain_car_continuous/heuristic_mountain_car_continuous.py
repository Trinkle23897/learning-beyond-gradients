"""Run MountainCarContinuous-v0 with a small handwritten energy-pump heuristic.

The policy uses only the native observation `(position, velocity)`.  It applies
force in the direction of travel to build energy, then keeps pushing right once
the car is on the right hill.  There is no gradient training, reward-model
training, environment-state lookup, or seed-specific route.

Example:

```bash
python classic_control/mountain_car_continuous/heuristic_mountain_car_continuous.py \
  --episodes 100 \
  --seed 10000
```

Local EnvPool 1.2.2 validation over seeds 10000..10099 from Arthur Yau's
independent heuristic-learning harness:

```text
mean = 93.69343671277166
std = 0.9122827223292292
min = 92.38399665057659
max = 94.75199676305056
```
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class EnergyPumpConfig:
    """Scalar parameters for the MountainCarContinuous heuristic."""

    force: float = 0.8
    left_force: float = -0.8
    hill_threshold: float = 0.15
    deadband: float = 0.0


def policy_action(obs: np.ndarray, config: EnergyPumpConfig) -> np.ndarray:
    """Return one continuous action from `(position, velocity)`."""

    position, velocity = np.asarray(obs, dtype=np.float64)
    if abs(velocity) <= config.deadband:
        force = config.force if position >= -0.5 else config.left_force
    else:
        force = config.force if velocity >= 0.0 else config.left_force
    if position > config.hill_threshold:
        force = config.force
    return np.asarray([force], dtype=np.float32)


def make_env(*, episodes: int, seed: int, max_episode_steps: int | None) -> Any:
    """Create an EnvPool vector environment lazily.

    The blog artifacts were written against EnvPool.  This helper accepts both
    newer `make_gymnasium` and older `make_gym` style constructors so the script
    is easier to run across local experiment environments.
    """

    import envpool

    kwargs: dict[str, Any] = {
        "num_envs": episodes,
        "batch_size": episodes,
        "seed": seed,
    }
    if max_episode_steps is not None:
        kwargs["max_episode_steps"] = max_episode_steps
    if hasattr(envpool, "make_gymnasium"):
        return envpool.make_gymnasium("MountainCarContinuous-v0", **kwargs)
    return envpool.make_gym("MountainCarContinuous-v0", **kwargs)


def _env_ids(info: Any, fallback_size: int) -> np.ndarray:
    if isinstance(info, dict):
        for key in ("env_id", "env_ids"):
            if key in info:
                return np.asarray(info[key], dtype=np.int64)
    return np.arange(fallback_size, dtype=np.int64)


def run(
    *,
    episodes: int,
    seed: int,
    max_steps: int,
    max_episode_steps: int | None,
    config: EnergyPumpConfig,
) -> np.ndarray:
    """Evaluate one episode per EnvPool slot and return episode scores."""

    env = make_env(episodes=episodes, seed=seed, max_episode_steps=max_episode_steps)
    reset_out = env.reset()
    if isinstance(reset_out, tuple) and len(reset_out) == 2:
        obs, info = reset_out
    else:
        obs, info = reset_out, {}

    scores = np.zeros(episodes, dtype=np.float64)
    lengths = np.zeros(episodes, dtype=np.int64)
    active = np.ones(episodes, dtype=bool)

    for _ in range(max_steps):
        obs_array = np.asarray(obs)
        actions = np.asarray([policy_action(obs_array[i], config) for i in range(episodes)])
        step_out = env.step(actions)
        if len(step_out) == 5:
            next_obs, reward, terminated, truncated, info = step_out
            done = np.asarray(terminated, dtype=bool) | np.asarray(truncated, dtype=bool)
        elif len(step_out) == 4:
            next_obs, reward, done, info = step_out
            done = np.asarray(done, dtype=bool)
        else:
            raise RuntimeError(f"unexpected EnvPool step output length: {len(step_out)}")

        reward = np.asarray(reward, dtype=np.float64)
        env_ids = _env_ids(info, len(reward))
        for row, env_id in enumerate(env_ids):
            env_id_int = int(env_id)
            if env_id_int >= episodes:
                continue
            if active[env_id_int]:
                scores[env_id_int] += float(reward[row])
                lengths[env_id_int] += 1
                if bool(done[row]):
                    active[env_id_int] = False
        obs = next_obs
        if not np.any(active):
            break
    else:
        unfinished = np.flatnonzero(active).tolist()
        raise RuntimeError(f"evaluation exceeded max_steps with unfinished envs: {unfinished}")

    return scores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a pure heuristic MountainCarContinuous-v0 policy."
    )
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--max-episode-steps", type=int, default=None)
    parser.add_argument("--force", type=float, default=0.8)
    parser.add_argument("--left-force", type=float, default=-0.8)
    parser.add_argument("--hill-threshold", type=float, default=0.15)
    parser.add_argument("--deadband", type=float, default=0.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = EnergyPumpConfig(
        force=args.force,
        left_force=args.left_force,
        hill_threshold=args.hill_threshold,
        deadband=args.deadband,
    )
    scores = run(
        episodes=args.episodes,
        seed=args.seed,
        max_steps=args.max_steps,
        max_episode_steps=args.max_episode_steps,
        config=config,
    )
    print("scores =", np.array2string(scores, precision=6, separator=", "))
    print(
        "eval_summary:",
        f"episodes={len(scores)}",
        f"seed={args.seed}",
        f"mean={np.mean(scores):.6f}",
        f"std={np.std(scores):.6f}",
        f"min={np.min(scores):.6f}",
        f"max={np.max(scores):.6f}",
    )


if __name__ == "__main__":
    main()
