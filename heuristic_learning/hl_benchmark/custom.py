"""Dispatch standard commands for custom-active benchmark environments."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
from types import ModuleType
from typing import Sequence

from hl_benchmark.artifacts import env_results_dir
from hl_benchmark.environments import registration_for
from hl_benchmark.environments.base import CUSTOM_ACTIVE_STATUS, EnvironmentRegistration
from hl_benchmark.registry import (
    artifact_layout_result,
    environment_readiness_result,
    environment_readiness_summary,
    render_environment_readiness,
    render_environment_readiness_summary,
)


CUSTOM_COMMAND_MODULES = {
    "doctor": "doctor",
    "evaluate": "evaluate",
    "eval": "evaluate",
    "summary": "summarize",
    "summarize": "summarize",
    "search": "search",
    "tournament": "tournament",
    "report": "report",
    "performance-report": "performance_report",
    "performance_report": "performance_report",
    "generation-report": "generation_report",
    "generation_report": "generation_report",
    "contact-diagnostics": "contact_diagnostics",
    "contact_diagnostics": "contact_diagnostics",
    "protocol": "protocol",
    "audit": "audit",
    "final-eval": "final_eval",
    "final_eval": "final_eval",
}
VERIFY_REQUIRED_COMMANDS = ("summary", "report", "performance-report", "audit")
CUSTOM_VERIFY_EXTRA_COMMANDS_ATTR = "CUSTOM_VERIFY_EXTRA_COMMANDS"
CUSTOM_VERIFY_EXTRA_ALLOWED_COMMANDS = frozenset(
    {
        "contact-diagnostics",
        "contact_diagnostics",
        "doctor",
        "generation-report",
        "generation_report",
        "protocol",
    }
)
CustomVerifyStep = tuple[str, tuple[str, ...]]


def require_custom_registration(env_id: str) -> EnvironmentRegistration:
    """Return a registration only when the environment uses a custom harness."""

    try:
        registration = registration_for(env_id)
    except KeyError as exc:
        raise ValueError(str(exc)) from exc
    if registration.status != CUSTOM_ACTIVE_STATUS:
        raise ValueError(
            f"{env_id} has status {registration.status!r}; expected {CUSTOM_ACTIVE_STATUS!r}"
        )
    return registration


def custom_command_module_name(env_id: str, command: str) -> str:
    """Return the module path that implements one custom-environment command."""

    registration = require_custom_registration(env_id)
    if command not in CUSTOM_COMMAND_MODULES:
        known = ", ".join(sorted((*CUSTOM_COMMAND_MODULES, "verify")))
        raise ValueError(f"unknown custom command {command!r}; expected one of {known}")
    return f"{registration.custom_module_root}.{CUSTOM_COMMAND_MODULES[command]}"


def _module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _command_main_available(module_name: str) -> bool:
    """Return whether a custom command module imports and exposes main()."""

    if not _module_available(module_name):
        return False
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return callable(getattr(module, "main", None))


def custom_verify_extra_commands(env_id: str) -> tuple[CustomVerifyStep, ...]:
    """Return harness-declared non-evaluation commands for custom verify.

    Custom environments can define ``CUSTOM_VERIFY_EXTRA_COMMANDS`` in their
    package root as ``((command, (arg, ...)), ...)``. These commands run after
    summary regeneration and before report/audit regeneration, so harnesses can
    refresh diagnostics or protocol artifacts without adding Makefile targets.
    """

    registration = require_custom_registration(env_id)
    try:
        root_module = importlib.import_module(registration.custom_module_root)
    except Exception:
        return ()
    raw_steps = getattr(root_module, CUSTOM_VERIFY_EXTRA_COMMANDS_ATTR, ())
    if raw_steps is None:
        return ()

    steps: list[CustomVerifyStep] = []
    for index, raw_step in enumerate(raw_steps):
        if not isinstance(raw_step, (tuple, list)) or len(raw_step) != 2:
            raise ValueError(
                f"{CUSTOM_VERIFY_EXTRA_COMMANDS_ATTR}[{index}] must be (command, args)"
            )
        command, forwarded_args = raw_step
        if not isinstance(command, str) or command not in CUSTOM_COMMAND_MODULES:
            raise ValueError(
                f"{CUSTOM_VERIFY_EXTRA_COMMANDS_ATTR}[{index}] has unknown command {command!r}"
            )
        if command not in CUSTOM_VERIFY_EXTRA_ALLOWED_COMMANDS:
            raise ValueError(
                f"{CUSTOM_VERIFY_EXTRA_COMMANDS_ATTR}[{index}] command {command!r} is not allowed in custom verify extras; use only non-evaluation diagnostics or protocol commands"
            )
        if isinstance(forwarded_args, (str, bytes)) or not isinstance(forwarded_args, Sequence):
            raise ValueError(
                f"{CUSTOM_VERIFY_EXTRA_COMMANDS_ATTR}[{index}] args must be a sequence of strings"
            )
        args_tuple: tuple[str, ...] = tuple(forwarded_args)
        if any(not isinstance(arg, str) for arg in args_tuple):
            raise ValueError(
                f"{CUSTOM_VERIFY_EXTRA_COMMANDS_ATTR}[{index}] args must be a sequence of strings"
            )
        steps.append((command, args_tuple))
    return tuple(steps)


def available_custom_commands(env_id: str) -> tuple[str, ...]:
    """Return implemented custom commands for one custom-active environment."""

    commands = [
        command
        for command in sorted(CUSTOM_COMMAND_MODULES)
        if _command_main_available(custom_command_module_name(env_id, command))
    ]
    if all(command in commands for command in VERIFY_REQUIRED_COMMANDS):
        commands.append("verify")
    return tuple(commands)


def render_available_custom_commands(env_id: str) -> str:
    """Render available custom commands for humans."""

    registration = require_custom_registration(env_id)
    commands = available_custom_commands(env_id)
    lines = [
        f"Custom environment commands: {env_id}",
        f"- Module root: {registration.custom_module_root}",
        f"- Commands: {', '.join(commands) if commands else 'none'}",
    ]
    return "\n".join(lines) + "\n"


def _load_module(module_name: str) -> ModuleType:
    if not _module_available(module_name):
        raise ValueError(f"missing custom command module: {module_name}")
    return importlib.import_module(module_name)


def _run_module_main(module_name: str, forwarded_args: Sequence[str]) -> str:
    module = _load_module(module_name)
    main = getattr(module, "main", None)
    if not callable(main):
        raise ValueError(f"custom command module has no callable main(): {module_name}")
    old_argv = sys.argv[:]
    try:
        sys.argv = [module_name, *forwarded_args]
        main()
    finally:
        sys.argv = old_argv
    return module_name


def _render_artifact_layout_result(result: dict[str, object]) -> str:
    if result.get("errors"):
        return "\n".join(str(error) for error in result["errors"]) + "\n"
    return "runnable artifact layout ok\n"


def _ensure_pass(result: dict[str, object], label: str) -> None:
    if result.get("pass_fail") != "pass":
        raise RuntimeError(f"{label} failed")


def run_custom_verify(env_id: str) -> None:
    """Run the standard non-evaluation verification chain for a custom env."""

    require_custom_registration(env_id)

    readiness = environment_readiness_result(env_id)
    print(render_environment_readiness(readiness), end="")
    _ensure_pass(readiness, "environment readiness")

    readiness_summary = environment_readiness_summary()
    print(render_environment_readiness_summary(readiness_summary), end="")
    _ensure_pass(readiness_summary, "runnable environment readiness")

    layout = artifact_layout_result()
    print(_render_artifact_layout_result(layout), end="")
    _ensure_pass(layout, "artifact layout")

    extra_steps = custom_verify_extra_commands(env_id)
    run_custom_command(env_id, "summary", ())
    for command, forwarded_args in extra_steps:
        run_custom_command(env_id, command, forwarded_args)
    run_custom_command(env_id, "report", ())
    run_custom_command(env_id, "performance-report", ())
    if ("generation-report" in available_custom_commands(env_id)
            and ("generation-report", ()) not in extra_steps):
        run_custom_command(env_id, "generation-report", ())
    run_custom_command(
        env_id,
        "audit",
        ("--output", str(env_results_dir(env_id) / "audit_latest.json")),
    )


def run_custom_command(
    env_id: str,
    command: str,
    forwarded_args: Sequence[str] = (),
) -> str:
    """Run one standard custom-environment command by importing its module."""

    if command == "verify":
        if forwarded_args:
            raise ValueError(
                "custom verify uses fixed arguments; use audit/report directly for command-specific flags"
            )
        run_custom_verify(env_id)
        return "verify"
    module_name = custom_command_module_name(env_id, command)
    return _run_module_main(module_name, tuple(forwarded_args))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", required=True, help="Registered custom-active environment id.")
    parser.add_argument(
        "command",
        nargs="?",
        default="list",
        help="Command to run. Omit it to list commands for the environment.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args, forwarded_args = parser.parse_known_args(argv)
    if forwarded_args and forwarded_args[0] == "--":
        forwarded_args = forwarded_args[1:]

    try:
        if args.command == "list":
            commands = available_custom_commands(args.env)
            if args.format == "json":
                print(
                    json.dumps(
                        {"env_id": args.env, "commands": commands},
                        indent=2,
                        sort_keys=True,
                    )
                )
            else:
                print(render_available_custom_commands(args.env), end="")
            return
        if args.format != "text":
            forwarded_args = ["--format", args.format, *forwarded_args]
        run_custom_command(args.env, args.command, tuple(forwarded_args))
    except (RuntimeError, ValueError) as exc:
        parser.exit(1, f"custom command failed: {exc}\n")


if __name__ == "__main__":
    main()
