"""Optional Stable-Baselines3 deep-RL training and evaluation baseline."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import numpy as np

from .envs import get_seeds, make_env
from .ledger import (
    DEFAULT_LEDGER_PATH,
    DEFAULT_SUMMARY_PATH,
    append_entry,
    make_trial_entry,
    write_summary_csv,
)


def _score_stats(scores: list[float]) -> dict[str, float | None]:
    if not scores:
        return {"mean": None, "std": None, "median": None, "min": None, "max": None}
    values = np.asarray(scores, dtype=float)
    return {
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "median": float(np.median(values)),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def _load_sb3_class(class_name: str) -> Any:
    try:
        import stable_baselines3
    except Exception as exc:  # pragma: no cover - depends on optional dependency
        raise RuntimeError(
            "Stable-Baselines3 is not installed. Install optional RL dependencies with "
            "`python3 -m pip install -e '.[rl]'` from heuristic_learning/."
        ) from exc
    return getattr(stable_baselines3, class_name)


def load_hf_baseline(
    *,
    env_id: str,
    algorithm: str,
    repo_id: str,
    filename: str,
) -> Any:
    """Load a pretrained Stable-Baselines3 model from Hugging Face Hub."""

    try:
        from huggingface_hub import hf_hub_download
    except Exception as exc:  # pragma: no cover - depends on optional dependency
        raise RuntimeError("huggingface_hub is required to load pretrained SB3 comparators") from exc

    model_path = hf_hub_download(repo_id=repo_id, filename=filename)
    model_class = _load_sb3_class(algorithm.upper())
    env = make_env(env_id)
    try:
        custom_objects = {
            "observation_space": env.observation_space,
            "action_space": env.action_space,
        }
        return model_class.load(
            model_path,
            env=env,
            device="cpu",
            custom_objects=custom_objects,
        )
    finally:
        env.close()


def train_ppo_baseline(
    *,
    env_id: str,
    train_steps: int,
    train_seed: int,
    learning_rate: float = 3e-4,
    n_steps: int = 1024,
    batch_size: int = 64,
    n_epochs: int = 10,
    gamma: float = 0.99,
    gae_lambda: float = 0.95,
    ent_coef: float = 0.0,
    clip_range: float = 0.2,
) -> Any:
    """Train a small PPO MLP policy for one Gymnasium environment."""

    PPO = _load_sb3_class("PPO")
    env = make_env(env_id)
    try:
        if hasattr(env.action_space, "seed"):
            env.action_space.seed(train_seed)
        env.reset(seed=train_seed)
        model = PPO(
            "MlpPolicy",
            env,
            seed=train_seed,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            gae_lambda=gae_lambda,
            ent_coef=ent_coef,
            clip_range=clip_range,
            verbose=0,
            device="cpu",
        )
        model.learn(total_timesteps=train_steps, progress_bar=False)
    finally:
        env.close()
    return model


def train_dqn_baseline(
    *,
    env_id: str,
    train_steps: int,
    train_seed: int,
    learning_rate: float = 1e-3,
    buffer_size: int = 100_000,
    learning_starts: int = 1_000,
    batch_size: int = 64,
    gamma: float = 0.99,
    exploration_fraction: float = 0.25,
    exploration_final_eps: float = 0.05,
    target_update_interval: int = 500,
    train_freq: int = 4,
    gradient_steps: int = 1,
    net_arch: tuple[int, ...] | None = None,
) -> Any:
    """Train a small DQN MLP policy for one discrete-action environment."""

    DQN = _load_sb3_class("DQN")
    env = make_env(env_id)
    try:
        if not hasattr(env.action_space, "n"):
            raise ValueError(f"DQN requires a discrete action space, got {env.action_space!r}")
        if hasattr(env.action_space, "seed"):
            env.action_space.seed(train_seed)
        env.reset(seed=train_seed)
        policy_kwargs = {"net_arch": list(net_arch)} if net_arch is not None else None
        model = DQN(
            "MlpPolicy",
            env,
            seed=train_seed,
            learning_rate=learning_rate,
            buffer_size=buffer_size,
            learning_starts=learning_starts,
            batch_size=batch_size,
            gamma=gamma,
            exploration_fraction=exploration_fraction,
            exploration_final_eps=exploration_final_eps,
            target_update_interval=target_update_interval,
            train_freq=train_freq,
            gradient_steps=gradient_steps,
            policy_kwargs=policy_kwargs,
            verbose=0,
            device="cpu",
        )
        model.learn(total_timesteps=train_steps, progress_bar=False)
    finally:
        env.close()
    return model


def train_sac_baseline(
    *,
    env_id: str,
    train_steps: int,
    train_seed: int,
    learning_rate: float = 3e-4,
    buffer_size: int = 300_000,
    learning_starts: int = 10_000,
    batch_size: int = 256,
    gamma: float = 0.99,
    tau: float = 0.005,
    ent_coef: str | float = "auto",
) -> Any:
    """Train a small SAC MLP policy for one continuous-action environment."""

    SAC = _load_sb3_class("SAC")
    env = make_env(env_id)
    try:
        if hasattr(env.action_space, "n"):
            raise ValueError(f"SAC requires a continuous action space, got {env.action_space!r}")
        if hasattr(env.action_space, "seed"):
            env.action_space.seed(train_seed)
        env.reset(seed=train_seed)
        model = SAC(
            "MlpPolicy",
            env,
            seed=train_seed,
            learning_rate=learning_rate,
            buffer_size=buffer_size,
            learning_starts=learning_starts,
            batch_size=batch_size,
            gamma=gamma,
            tau=tau,
            ent_coef=ent_coef,
            train_freq=1,
            gradient_steps=1,
            verbose=0,
            device="cpu",
        )
        model.learn(total_timesteps=train_steps, progress_bar=False)
    finally:
        env.close()
    return model


def evaluate_model(
    *,
    model: Any,
    env_id: str,
    split: str,
    episodes: int | None,
) -> tuple[list[float], list[dict[str, Any]], int]:
    """Evaluate a trained SB3 model on fixed seeds."""

    seeds = get_seeds(split, episodes=episodes)
    scores: list[float] = []
    per_episode: list[dict[str, Any]] = []
    environment_steps = 0
    env = make_env(env_id)
    try:
        for seed in seeds:
            if hasattr(env.action_space, "seed"):
                env.action_space.seed(seed)
            obs, _info = env.reset(seed=seed)
            score = 0.0
            steps = 0
            terminated = False
            truncated = False
            while not (terminated or truncated):
                action, _state = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, _info = env.step(action)
                score += float(reward)
                steps += 1
            scores.append(score)
            environment_steps += steps
            per_episode.append({"seed": seed, "score": score, "steps": steps})
    finally:
        env.close()
    return scores, per_episode, environment_steps


def train_evaluate_baseline(
    *,
    env_id: str,
    algorithm: str,
    train_steps: int,
    train_seed: int,
    split: str,
    episodes: int | None,
    ledger_path: Path | None = DEFAULT_LEDGER_PATH,
    summary_path: Path | None = DEFAULT_SUMMARY_PATH,
    tests_run: list[str] | None = None,
    agent_iterations: int = 0,
    code_edits: int = 0,
    learning_rate: float | None = None,
    n_steps: int | None = None,
    batch_size: int | None = None,
    n_epochs: int | None = None,
    gamma: float | None = None,
    gae_lambda: float | None = None,
    ent_coef: float | None = None,
    clip_range: float | None = None,
    buffer_size: int | None = None,
    learning_starts: int | None = None,
    exploration_fraction: float | None = None,
    exploration_final_eps: float | None = None,
    target_update_interval: int | None = None,
    train_freq: int | None = None,
    gradient_steps: int | None = None,
    net_arch: tuple[int, ...] | None = None,
    pretrained_repo_id: str | None = None,
    pretrained_filename: str | None = None,
) -> dict[str, Any]:
    """Train a deep-RL baseline, evaluate it on fixed seeds, and append a ledger entry."""

    started = time.perf_counter()
    pass_fail = "pass"
    error: str | None = None
    scores: list[float] = []
    per_episode: list[dict[str, Any]] = []
    environment_steps = 0
    ppo_kwargs = {
        "learning_rate": 3e-4 if learning_rate is None else learning_rate,
        "n_steps": 1024 if n_steps is None else n_steps,
        "batch_size": 64 if batch_size is None else batch_size,
        "n_epochs": 10 if n_epochs is None else n_epochs,
        "gamma": 0.99 if gamma is None else gamma,
        "gae_lambda": 0.95 if gae_lambda is None else gae_lambda,
        "ent_coef": 0.0 if ent_coef is None else ent_coef,
        "clip_range": 0.2 if clip_range is None else clip_range,
    }
    dqn_kwargs = {
        "learning_rate": 1e-3 if learning_rate is None else learning_rate,
        "buffer_size": 100_000 if buffer_size is None else buffer_size,
        "learning_starts": 1_000 if learning_starts is None else learning_starts,
        "batch_size": 64 if batch_size is None else batch_size,
        "gamma": 0.99 if gamma is None else gamma,
        "exploration_fraction": 0.25 if exploration_fraction is None else exploration_fraction,
        "exploration_final_eps": 0.05 if exploration_final_eps is None else exploration_final_eps,
        "target_update_interval": 500 if target_update_interval is None else target_update_interval,
        "train_freq": 4 if train_freq is None else train_freq,
        "gradient_steps": 1 if gradient_steps is None else gradient_steps,
        "net_arch": net_arch,
    }
    config = {
        "algorithm": algorithm.upper(),
        "policy": "MlpPolicy",
        "train_steps": train_steps,
        "train_seed": train_seed,
    }
    if pretrained_repo_id is not None:
        config.update({
            "pretrained_repo_id": pretrained_repo_id,
            "pretrained_filename": pretrained_filename,
        })
    if algorithm == "ppo":
        config.update(ppo_kwargs)
    if algorithm == "dqn":
        config.update({key: value for key, value in dqn_kwargs.items() if value is not None})
    if algorithm == "sac":
        config.update({"learning_rate": 3e-4 if learning_rate is None else learning_rate})
    try:
        if pretrained_repo_id is not None:
            if pretrained_filename is None:
                raise ValueError("pretrained_filename is required when pretrained_repo_id is set")
            model = load_hf_baseline(
                env_id=env_id,
                algorithm=algorithm,
                repo_id=pretrained_repo_id,
                filename=pretrained_filename,
            )
        elif algorithm == "ppo":
            model = train_ppo_baseline(
                env_id=env_id,
                train_steps=train_steps,
                train_seed=train_seed,
                **ppo_kwargs,
            )
        elif algorithm == "dqn":
            model = train_dqn_baseline(
                env_id=env_id,
                train_steps=train_steps,
                train_seed=train_seed,
                **dqn_kwargs,
            )
        elif algorithm == "sac":
            model = train_sac_baseline(
                env_id=env_id,
                train_steps=train_steps,
                train_seed=train_seed,
                learning_rate=3e-4 if learning_rate is None else learning_rate,
                gamma=0.99 if gamma is None else gamma,
            )
        else:
            raise ValueError(f"unknown RL algorithm {algorithm!r}; expected ppo, dqn, or sac")
        scores, per_episode, environment_steps = evaluate_model(
            model=model,
            env_id=env_id,
            split=split,
            episodes=episodes,
        )
    except Exception as exc:
        pass_fail = "fail"
        error = f"{type(exc).__name__}: {exc}"

    wall_clock_seconds = time.perf_counter() - started
    seeds = get_seeds(split, episodes=episodes)
    failure_analysis = "No failure observed." if error is None else error
    next_hypothesis = (
        f"Use this {algorithm.upper()} result as the deep-RL comparator for ±5% heuristic comparison."
        if error is None
        else "Install/fix optional RL dependencies or adjust the RL training budget."
    )
    entry = make_trial_entry(
        environment=env_id,
        policy_version=f"rl-{algorithm}-hf" if pretrained_repo_id is not None else f"rl-{algorithm}",
        config=config,
        seed_split=split,
        seeds=seeds,
        episodes=len(scores) if pass_fail == "pass" else len(seeds),
        score_stats=_score_stats(scores),
        environment_steps=environment_steps + train_steps,
        wall_clock_seconds=wall_clock_seconds,
        tests_run=tests_run or [],
        pass_fail=pass_fail,
        change_summary=(
            f"Load pretrained {algorithm.upper()} deep-RL baseline from {pretrained_repo_id} "
            f"and evaluate on fixed {split} seeds."
            if pretrained_repo_id is not None
            else f"Train {algorithm.upper()} deep-RL baseline for {train_steps} timesteps on {env_id} "
            f"and evaluate on fixed {split} seeds."
        ),
        failure_analysis=failure_analysis,
        next_hypothesis=next_hypothesis,
        change_type="rl/deep learning baseline",
        agent_iterations=agent_iterations,
        code_edits=code_edits,
        per_episode=per_episode,
        error=error,
    )
    if ledger_path is not None:
        append_entry(ledger_path, entry)
        if summary_path is not None:
            write_summary_csv(ledger_path, summary_path)
    return entry


def train_evaluate_ppo(**kwargs: Any) -> dict[str, Any]:
    """Backward-compatible wrapper for PPO baseline runs."""

    return train_evaluate_baseline(algorithm="ppo", **kwargs)


def train_evaluate_sac(**kwargs: Any) -> dict[str, Any]:
    """Wrapper for SAC baseline runs."""

    return train_evaluate_baseline(algorithm="sac", **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", dest="env_id", required=True)
    parser.add_argument("--algo", choices=["ppo", "dqn", "sac"], default="ppo")
    parser.add_argument("--train-steps", type=int, default=10_000)
    parser.add_argument("--train-seed", type=int, default=0)
    parser.add_argument("--split", choices=["smoke", "dev", "holdout", "audit"], default="dev")
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument("--tests-run", default="")
    parser.add_argument("--learning-rate", type=float, default=None)
    parser.add_argument("--n-steps", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--n-epochs", type=int, default=None)
    parser.add_argument("--gamma", type=float, default=None)
    parser.add_argument("--gae-lambda", type=float, default=None)
    parser.add_argument("--ent-coef", type=float, default=None)
    parser.add_argument("--clip-range", type=float, default=None)
    parser.add_argument("--buffer-size", type=int, default=None)
    parser.add_argument("--learning-starts", type=int, default=None)
    parser.add_argument("--exploration-fraction", type=float, default=None)
    parser.add_argument("--exploration-final-eps", type=float, default=None)
    parser.add_argument("--target-update-interval", type=int, default=None)
    parser.add_argument("--train-freq", type=int, default=None)
    parser.add_argument("--gradient-steps", type=int, default=None)
    parser.add_argument("--net-arch", type=int, nargs="*", default=None)
    parser.add_argument("--pretrained-repo-id", default=None)
    parser.add_argument("--pretrained-filename", default=None)
    parser.add_argument("--agent-iterations", type=int, default=0)
    parser.add_argument("--code-edits", type=int, default=0)
    args = parser.parse_args()
    tests_run = [item for item in args.tests_run.split(",") if item]
    entry = train_evaluate_baseline(
        env_id=args.env_id,
        algorithm=args.algo,
        train_steps=args.train_steps,
        train_seed=args.train_seed,
        split=args.split,
        episodes=args.episodes,
        ledger_path=args.ledger,
        summary_path=args.summary,
        tests_run=tests_run,
        agent_iterations=args.agent_iterations,
        code_edits=args.code_edits,
        learning_rate=args.learning_rate,
        n_steps=args.n_steps,
        batch_size=args.batch_size,
        n_epochs=args.n_epochs,
        gamma=args.gamma,
        gae_lambda=args.gae_lambda,
        ent_coef=args.ent_coef,
        clip_range=args.clip_range,
        buffer_size=args.buffer_size,
        learning_starts=args.learning_starts,
        exploration_fraction=args.exploration_fraction,
        exploration_final_eps=args.exploration_final_eps,
        target_update_interval=args.target_update_interval,
        train_freq=args.train_freq,
        gradient_steps=args.gradient_steps,
        net_arch=tuple(args.net_arch) if args.net_arch else None,
        pretrained_repo_id=args.pretrained_repo_id,
        pretrained_filename=args.pretrained_filename,
    )
    mean = entry["score_stats"]["mean"]
    print(
        f"{entry['pass_fail']:4s} {args.env_id:18s} rl-{args.algo} train_steps={args.train_steps} "
        f"mean={mean if mean is not None else 'n/a'} steps={entry['environment_steps']}"
    )


if __name__ == "__main__":
    main()
