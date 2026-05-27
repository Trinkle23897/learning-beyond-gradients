"""Shared SlimeVolley audit/report schema constants."""

from __future__ import annotations

import statistics

from typing import Any


CANONICAL_CHANGE_TYPES = frozenset(
    {
        "structural policy improvement",
        "scalar/config tuning",
        "opponent-pool change",
        "evaluation-harness change",
        "logging/diagnostics change",
        "bug fix",
        "invalid/rolled back",
    }
)

NEURAL_BASELINE_CHANGE_TYPE = "neural/RL baseline"
LEGACY_NONCANONICAL_CHANGE_TYPES = frozenset(
    {
        "logging/diagnostics",
        NEURAL_BASELINE_CHANGE_TYPE,
    }
)
ALLOWED_CHANGE_TYPES = CANONICAL_CHANGE_TYPES | LEGACY_NONCANONICAL_CHANGE_TYPES

SLIMEVOLLEY_ENV_ID = "SlimeVolley-v0"
SLIMEVOLLEY_ENV_KEY = "slimevolley"
SLIMEVOLLEY_REQUIRED_LEDGER_FIELDS = (
    "environment_id",
    "environment_key",
    "opponent_name",
    "opponent_version",
    "opponent_kind",
    "win_loss_draw",
    "life_difference_stats",
    "action_frequencies",
    "opponent_action_frequencies",
)
WIN_LOSS_DRAW_FIELDS = ("wins", "losses", "draws", "win_rate")
SCORE_STAT_FIELDS = ("mean", "std", "median", "min", "max")
LIFE_DIFFERENCE_STAT_FIELDS = SCORE_STAT_FIELDS
ACTION_FREQUENCY_FIELDS = ("action_frequencies", "opponent_action_frequencies")
EPISODE_OUTCOMES = {"win", "loss", "draw"}
POINT_EVENT_OUTCOMES = {"point_won", "point_lost"}
TESTS_PASS_FAIL_VALUES = {"pass", "fail", "not_recorded"}
LLM_COST_NUMERIC_FIELDS = ("calls", "prompt_tokens", "completion_tokens", "total_tokens")
REQUIRED_RUNTIME_PACKAGE_KEYS = ("gymnasium", "numpy", "pytest", "slimevolleygym")
REQUIRED_CONFIG_PACKAGE_KEYS = ("numpy", "slimevolleygym")
STAT_TOLERANCE = 1e-9


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_number_or_none(value: Any) -> bool:
    return value is None or _is_number(value)


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _float_matches(observed: float | int, expected: float | int) -> bool:
    return abs(float(observed) - float(expected)) <= STAT_TOLERANCE


def _stats_from_values(values: list[float]) -> dict[str, float]:
    return {
        "mean": float(statistics.fmean(values)),
        "std": float(statistics.pstdev(values)) if len(values) > 1 else 0.0,
        "median": float(statistics.median(values)),
        "min": float(min(values)),
        "max": float(max(values)),
    }


def _stat_consistency_issues(
    stats: Any,
    values: list[float],
    stats_label: str,
    values_label: str,
) -> list[str]:
    if not values or not isinstance(stats, dict):
        return []

    issues: list[str] = []
    expected = _stats_from_values(values)
    for field, expected_value in expected.items():
        observed = stats.get(field)
        if _is_number(observed) and not _float_matches(observed, expected_value):
            issues.append(f"{stats_label}.{field} does not match {values_label}")
    return issues


def _package_map_issues(
    packages: Any,
    label: str,
    *,
    required_keys: tuple[str, ...],
) -> list[str]:
    if not isinstance(packages, dict) or not packages:
        return [f"{label} is missing or empty"]

    issues: list[str] = []
    for package_name, version in packages.items():
        if not isinstance(package_name, str) or not package_name.strip():
            issues.append(f"{label} contains a missing or non-string package name")
        if not isinstance(version, str) or not version.strip():
            issues.append(f"{label}.{package_name!r} is missing or not a string")
    for package_name in required_keys:
        if package_name not in packages:
            issues.append(f"{label} missing required package: {package_name}")
    return issues


def _config_issues(entry: dict[str, Any]) -> list[str]:
    config = entry.get("config")
    if not isinstance(config, dict):
        return ["config is missing or not an object"]
    return _package_map_issues(
        config.get("dependency_versions"),
        "config.dependency_versions",
        required_keys=REQUIRED_CONFIG_PACKAGE_KEYS,
    )


def _llm_cost_issues(entry: dict[str, Any]) -> list[str]:
    llm_cost = entry.get("llm_cost")
    if not isinstance(llm_cost, dict):
        return ["llm_cost is missing or not an object"]

    issues: list[str] = []
    for field in LLM_COST_NUMERIC_FIELDS:
        value = llm_cost.get(field)
        if value != "unavailable" and not _is_non_negative_int(value):
            issues.append(f"llm_cost.{field} is not a non-negative integer or 'unavailable'")

    prompt_tokens = llm_cost.get("prompt_tokens")
    completion_tokens = llm_cost.get("completion_tokens")
    total_tokens = llm_cost.get("total_tokens")
    if (
        _is_non_negative_int(prompt_tokens)
        and _is_non_negative_int(completion_tokens)
        and total_tokens == "unavailable"
    ):
        issues.append("llm_cost.total_tokens is unavailable despite numeric prompt/completion tokens")
    if (
        _is_non_negative_int(prompt_tokens)
        and _is_non_negative_int(completion_tokens)
        and _is_non_negative_int(total_tokens)
        and total_tokens != prompt_tokens + completion_tokens
    ):
        issues.append("llm_cost.total_tokens does not match prompt_tokens + completion_tokens")

    source = llm_cost.get("source")
    if not isinstance(source, str) or not source.strip():
        issues.append("llm_cost.source is missing or empty")
    return issues


def _provenance_issues(entry: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in ("git_commit", "diff_identifier"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{field} is missing or empty")
    tests_run = entry.get("tests_run")
    if not isinstance(tests_run, list) or not tests_run:
        issues.append("tests_run is missing or empty")
    elif not all(isinstance(command, str) and command.strip() for command in tests_run):
        issues.append("tests_run contains a non-string or empty command")

    tests_pass_fail = entry.get("tests_pass_fail")
    if tests_pass_fail is not None and tests_pass_fail not in TESTS_PASS_FAIL_VALUES:
        issues.append("tests_pass_fail is not one of pass, fail, or not_recorded")
    if tests_pass_fail in {"pass", "fail"} and (not isinstance(tests_run, list) or not tests_run):
        issues.append("tests_pass_fail records a status but tests_run is empty")
    return issues


def _core_ledger_issues(entry: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in ("timestamp", "policy_version", "change_summary", "failure_analysis", "next_hypothesis", "change_type"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{field} is missing or empty")
    change_type = entry.get("change_type")
    if isinstance(change_type, str) and change_type.strip() and change_type not in ALLOWED_CHANGE_TYPES:
        issues.append(f"change_type {change_type!r} is not a recognized SlimeVolley change type")
    if entry.get("pass_fail") not in {"pass", "fail"}:
        issues.append("pass_fail is not 'pass' or 'fail'")

    seed_range = entry.get("seed_range")
    if not isinstance(seed_range, dict):
        issues.append("seed_range is missing or not an object")
    else:
        split = seed_range.get("split")
        if not isinstance(split, str) or not split.strip():
            issues.append("seed_range.split is missing or empty")
        seeds = seed_range.get("seeds")
        valid_seed_list = isinstance(seeds, list) and all(
            isinstance(seed, int) and not isinstance(seed, bool)
            for seed in seeds
        )
        if not valid_seed_list:
            issues.append("seed_range.seeds is missing or not a list of integers")
        start = seed_range.get("start")
        stop = seed_range.get("stop_exclusive")
        if valid_seed_list and seeds:
            if start != min(seeds):
                issues.append("seed_range.start does not match the minimum seed")
            if stop != max(seeds) + 1:
                issues.append("seed_range.stop_exclusive does not match the maximum seed plus one")
        elif valid_seed_list and (start is not None or stop is not None):
            issues.append("empty seed_range.seeds should use null start and stop_exclusive")
    return issues


def _runtime_metadata_issues(entry: dict[str, Any]) -> list[str]:
    runtime_metadata = entry.get("runtime_metadata")
    if not isinstance(runtime_metadata, dict):
        return ["runtime_metadata is missing or not an object"]
    issues: list[str] = []
    if not isinstance(runtime_metadata.get("python"), str) or not runtime_metadata.get("python"):
        issues.append("runtime_metadata.python is missing or empty")
    if not isinstance(runtime_metadata.get("platform"), str) or not runtime_metadata.get("platform"):
        issues.append("runtime_metadata.platform is missing or empty")
    issues.extend(
        _package_map_issues(
            runtime_metadata.get("packages"),
            "runtime_metadata.packages",
            required_keys=REQUIRED_RUNTIME_PACKAGE_KEYS,
        )
    )
    return issues


def _frequency_issues(entry: dict[str, Any], field: str) -> list[str]:
    values = entry.get(field)
    if not isinstance(values, dict):
        return [f"{field} is missing or not an object"]
    return _action_count_map_issues(values, field)


def _action_count_map_issues(
    values: Any,
    label: str,
    *,
    steps: int | None = None,
    require_step_total: bool = False,
) -> list[str]:
    issues: list[str] = []
    if not isinstance(values, dict):
        return [f"{label} is missing or not an object"]

    valid_counts = True
    for action, count in values.items():
        if not isinstance(action, str):
            issues.append(f"{label} contains non-string action key: {action!r}")
            valid_counts = False
        if not _is_non_negative_int(count):
            issues.append(f"{label} count for {action!r} is not a non-negative integer")
            valid_counts = False
    if (
        require_step_total
        and steps is not None
        and valid_counts
        and sum(values.values()) != steps
    ):
        issues.append(f"{label} total does not match environment steps")
    return issues


def _per_episode_aggregate_issues(
    entry: dict[str, Any],
    *,
    environment_steps: Any,
    seed_range_seeds: Any,
) -> list[str]:
    if entry.get("pass_fail") != "pass":
        return []

    per_episode = entry.get("per_episode")
    if not isinstance(per_episode, list):
        return []

    issues: list[str] = []
    episode_seeds: list[int] = []
    seed_values_valid = True
    step_total = 0
    step_values_valid = True
    outcome_counts = {"win": 0, "loss": 0, "draw": 0}
    outcome_values_valid = True
    score_values: list[float] = []
    score_values_valid = True
    life_difference_values: list[float] = []
    life_difference_values_valid = True

    for episode in per_episode:
        if not isinstance(episode, dict):
            return []
        seed = episode.get("seed")
        if isinstance(seed, int) and not isinstance(seed, bool):
            episode_seeds.append(seed)
        else:
            seed_values_valid = False
        steps = episode.get("steps")
        if _is_non_negative_int(steps):
            step_total += steps
        else:
            step_values_valid = False
        outcome = episode.get("outcome")
        if outcome in outcome_counts:
            outcome_counts[outcome] += 1
        else:
            outcome_values_valid = False
        score = episode.get("score")
        if _is_number(score):
            score_values.append(float(score))
        else:
            score_values_valid = False
        life_difference = episode.get("life_difference")
        if _is_number(life_difference):
            life_difference_values.append(float(life_difference))
        else:
            life_difference_values_valid = False

    valid_seed_range = isinstance(seed_range_seeds, list) and all(
        isinstance(seed, int) and not isinstance(seed, bool)
        for seed in seed_range_seeds
    )
    if seed_values_valid and valid_seed_range and episode_seeds != seed_range_seeds:
        issues.append("per_episode seeds do not match seed_range.seeds")

    if step_values_valid and _is_non_negative_int(environment_steps):
        if step_total != environment_steps:
            issues.append("per_episode steps total does not match environment_steps")

    if score_values_valid:
        issues.extend(
            _stat_consistency_issues(
                entry.get("score_stats"),
                score_values,
                "score_stats",
                "per_episode scores",
            )
        )
    if life_difference_values_valid:
        issues.extend(
            _stat_consistency_issues(
                entry.get("life_difference_stats"),
                life_difference_values,
                "life_difference_stats",
                "per_episode life_difference values",
            )
        )

    wld = entry.get("win_loss_draw")
    if outcome_values_valid and isinstance(wld, dict):
        wins = wld.get("wins")
        losses = wld.get("losses")
        draws = wld.get("draws")
        if all(_is_non_negative_int(value) for value in (wins, losses, draws)):
            observed = (outcome_counts["win"], outcome_counts["loss"], outcome_counts["draw"])
            expected = (wins, losses, draws)
            if observed != expected:
                issues.append("per_episode outcomes do not match win_loss_draw")

    return issues


def _per_episode_issues(entry: dict[str, Any]) -> list[str]:
    if entry.get("pass_fail") != "pass":
        return []

    issues: list[str] = []
    episodes = entry.get("episodes")
    per_episode = entry.get("per_episode")
    if not isinstance(per_episode, list):
        return ["passing row per_episode is missing or not a list"]
    if isinstance(episodes, int) and len(per_episode) != episodes:
        issues.append("passing row per_episode length does not match episodes")

    for episode_index, episode in enumerate(per_episode, start=1):
        prefix = f"per_episode[{episode_index}]"
        if not isinstance(episode, dict):
            issues.append(f"{prefix} is not an object")
            continue
        seed = episode.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool):
            issues.append(f"{prefix}.seed is not an integer")
        score = episode.get("score")
        if not _is_number(score):
            issues.append(f"{prefix}.score is not numeric")
        life_difference = episode.get("life_difference")
        if not _is_number(life_difference):
            issues.append(f"{prefix}.life_difference is not numeric")
        steps = episode.get("steps")
        valid_steps = _is_non_negative_int(steps)
        if not valid_steps:
            issues.append(f"{prefix}.steps is not a non-negative integer")
        outcome = episode.get("outcome")
        if outcome not in EPISODE_OUTCOMES:
            issues.append(f"{prefix}.outcome is not one of {sorted(EPISODE_OUTCOMES)}")
        if valid_steps:
            issues.extend(
                _action_count_map_issues(
                    episode.get("action_counts"),
                    f"{prefix}.action_counts",
                    steps=steps,
                    require_step_total=True,
                )
            )
            opponent_action_counts = episode.get("opponent_action_counts")
            issues.extend(
                _action_count_map_issues(
                    opponent_action_counts,
                    f"{prefix}.opponent_action_counts",
                    steps=steps if opponent_action_counts else None,
                    require_step_total=bool(opponent_action_counts),
                )
            )
            if entry.get("opponent_name") != "builtin" and opponent_action_counts == {}:
                issues.append(
                    f"{prefix}.opponent_action_counts is empty for explicit opponent policy"
                )
        else:
            issues.extend(
                _action_count_map_issues(
                    episode.get("action_counts"),
                    f"{prefix}.action_counts",
                )
            )
            issues.extend(
                _action_count_map_issues(
                    episode.get("opponent_action_counts"),
                    f"{prefix}.opponent_action_counts",
                )
            )
        point_events = episode.get("point_events", [])
        if not isinstance(point_events, list):
            issues.append(f"{prefix}.point_events is not a list")
        else:
            for event_index, event in enumerate(point_events, start=1):
                event_prefix = f"{prefix}.point_events[{event_index}]"
                if not isinstance(event, dict):
                    issues.append(f"{event_prefix} is not an object")
                    continue
                event_step = event.get("step")
                if not _is_non_negative_int(event_step):
                    issues.append(f"{event_prefix}.step is not a non-negative integer")
                elif valid_steps and event_step >= steps:
                    issues.append(f"{event_prefix}.step is outside episode step range")
                reward = event.get("reward")
                outcome = event.get("outcome")
                if not _is_number(reward):
                    issues.append(f"{event_prefix}.reward is not numeric")
                else:
                    if reward == 0:
                        issues.append(f"{event_prefix}.reward is zero despite point event")
                    elif reward > 0 and outcome != "point_won":
                        issues.append(f"{event_prefix}.outcome does not match positive reward")
                    elif reward < 0 and outcome != "point_lost":
                        issues.append(f"{event_prefix}.outcome does not match negative reward")
                if outcome not in POINT_EVENT_OUTCOMES:
                    issues.append(
                        f"{event_prefix}.outcome is not one of {sorted(POINT_EVENT_OUTCOMES)}"
                    )
                if not isinstance(event.get("action"), str) or not event.get("action"):
                    issues.append(f"{event_prefix}.action is missing or empty")
    return issues


def validate_slimevolley_ledger_entry(entry: dict[str, Any]) -> list[str]:
    """Return SlimeVolley-specific ledger schema issues for one entry."""

    issues: list[str] = []
    for field in SLIMEVOLLEY_REQUIRED_LEDGER_FIELDS:
        if field not in entry:
            issues.append(f"missing SlimeVolley ledger field: {field}")

    if entry.get("environment") != SLIMEVOLLEY_ENV_ID:
        issues.append(
            f"environment {entry.get('environment')!r} does not match {SLIMEVOLLEY_ENV_ID}"
        )
    if entry.get("environment_id") != SLIMEVOLLEY_ENV_ID:
        issues.append(
            f"environment_id {entry.get('environment_id')!r} does not match {SLIMEVOLLEY_ENV_ID}"
        )
    if entry.get("environment_key") != SLIMEVOLLEY_ENV_KEY:
        issues.append(
            f"environment_key {entry.get('environment_key')!r} does not match {SLIMEVOLLEY_ENV_KEY}"
        )

    issues.extend(_core_ledger_issues(entry))
    issues.extend(_config_issues(entry))
    issues.extend(_provenance_issues(entry))
    issues.extend(_runtime_metadata_issues(entry))

    episodes = entry.get("episodes")
    if not isinstance(episodes, int) or isinstance(episodes, bool) or episodes < 0:
        issues.append("episodes is not a non-negative integer")

    environment_steps = entry.get("environment_steps")
    if (
        not isinstance(environment_steps, int)
        or isinstance(environment_steps, bool)
        or environment_steps < 0
    ):
        issues.append("environment_steps is not a non-negative integer")

    wall_clock_seconds = entry.get("wall_clock_seconds")
    if not _is_number(wall_clock_seconds) or float(wall_clock_seconds) < 0.0:
        issues.append("wall_clock_seconds is not a non-negative number")

    agent_iterations = entry.get("agent_iterations")
    if not _is_non_negative_int(agent_iterations):
        issues.append("agent_iterations is not a non-negative integer")

    code_edits = entry.get("code_edits")
    if not _is_non_negative_int(code_edits):
        issues.append("code_edits is not a non-negative integer")

    issues.extend(_llm_cost_issues(entry))

    if entry.get("pass_fail") != "pass":
        failure_analysis = str(entry.get("failure_analysis", "")).strip()
        next_hypothesis = str(entry.get("next_hypothesis", "")).strip()
        if not failure_analysis or failure_analysis == "No failure observed.":
            issues.append("failed row is missing specific failure_analysis")
        if not next_hypothesis:
            issues.append("failed row is missing next_hypothesis")

    score_stats = entry.get("score_stats")
    if not isinstance(score_stats, dict):
        issues.append("score_stats is missing or not an object")
    else:
        for field in SCORE_STAT_FIELDS:
            if field not in score_stats:
                issues.append(f"score_stats missing field: {field}")
            elif not _is_number_or_none(score_stats[field]):
                issues.append(f"score_stats.{field} is not numeric or null")

    seed_range = entry.get("seed_range", {})
    seeds = seed_range.get("seeds", []) if isinstance(seed_range, dict) else []
    if isinstance(seeds, list) and isinstance(episodes, int) and len(seeds) != episodes:
        issues.append("seed_range.seeds length does not match episodes")

    issues.extend(_per_episode_issues(entry))
    issues.extend(
        _per_episode_aggregate_issues(
            entry,
            environment_steps=environment_steps,
            seed_range_seeds=seeds,
        )
    )

    wld = entry.get("win_loss_draw")
    if not isinstance(wld, dict):
        issues.append("win_loss_draw is missing or not an object")
    else:
        for field in WIN_LOSS_DRAW_FIELDS:
            if field not in wld:
                issues.append(f"win_loss_draw missing field: {field}")
        for field in ("wins", "losses", "draws"):
            if field in wld and not _is_non_negative_int(wld[field]):
                issues.append(f"win_loss_draw.{field} is not a non-negative integer")
        win_rate = wld.get("win_rate")
        if not _is_number_or_none(win_rate):
            issues.append("win_loss_draw.win_rate is not numeric or null")
        elif _is_number(win_rate) and not 0.0 <= float(win_rate) <= 1.0:
            issues.append("win_loss_draw.win_rate is outside [0, 1]")
        if entry.get("pass_fail") == "pass" and isinstance(episodes, int):
            wins = wld.get("wins")
            losses = wld.get("losses")
            draws = wld.get("draws")
            if all(_is_non_negative_int(value) for value in [wins, losses, draws]):
                if wins + losses + draws != episodes:
                    issues.append("win/loss/draw total does not match episodes")
                if episodes > 0 and _is_number(win_rate):
                    expected_win_rate = float(wins) / float(episodes)
                    if not _float_matches(win_rate, expected_win_rate):
                        issues.append("win_loss_draw.win_rate does not match wins/episodes")
                elif episodes == 0 and win_rate is not None:
                    issues.append("win_loss_draw.win_rate should be null when episodes is zero")

    life_stats = entry.get("life_difference_stats")
    if not isinstance(life_stats, dict):
        issues.append("life_difference_stats is missing or not an object")
    else:
        for field in LIFE_DIFFERENCE_STAT_FIELDS:
            if field not in life_stats:
                issues.append(f"life_difference_stats missing field: {field}")
            elif not _is_number_or_none(life_stats[field]):
                issues.append(f"life_difference_stats.{field} is not numeric or null")

    for field in ACTION_FREQUENCY_FIELDS:
        issues.extend(_frequency_issues(entry, field))

    if entry.get("pass_fail") == "pass" and isinstance(environment_steps, int):
        action_frequencies = entry.get("action_frequencies")
        if isinstance(action_frequencies, dict) and sum(action_frequencies.values()) != environment_steps:
            issues.append("action_frequencies total does not match environment steps")
        opponent_action_frequencies = entry.get("opponent_action_frequencies")
        if isinstance(opponent_action_frequencies, dict):
            if opponent_action_frequencies and sum(opponent_action_frequencies.values()) != environment_steps:
                issues.append(
                    "opponent_action_frequencies total does not match environment steps"
                )
            if entry.get("opponent_name") != "builtin" and not opponent_action_frequencies:
                issues.append(
                    "opponent_action_frequencies is empty for explicit opponent policy"
                )

    return issues
