"""
Config command module.
"""

import argparse
from typing import Any, Callable, Tuple

from level.config import (
    build_context,
    save_config,
    initialize_defaults,
)

# ---------------------------------------------------------------------------
# Doctor checks
# ---------------------------------------------------------------------------


def check_level_home(context: Any, fix: bool) -> Tuple[bool, str]:
    if context.home.exists():
        return True, f"LEVEL_HOME exists: {context.home}"

    if not fix:
        return False, f"LEVEL_HOME missing: {context.home}"

    context.home.mkdir(parents=True, exist_ok=True)
    return True, f"LEVEL_HOME created: {context.home}"


def check_data_dir(context: Any, fix: bool) -> Tuple[bool, str]:
    data_dir = context.config.data_dir or (context.home / "data")

    if data_dir.exists():
        if not data_dir.is_dir():
            return False, f"data_dir is not a directory: {data_dir}"
        return True, f"data_dir exists: {data_dir}"

    if not fix:
        return False, f"data_dir missing: {data_dir}"

    data_dir.mkdir(parents=True, exist_ok=True)
    return True, f"data_dir created: {data_dir}"


CHECKS: list[Callable[[Any, bool], Tuple[bool, str]]] = [
    check_level_home,
    check_data_dir,
]


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_config_show(args: argparse.Namespace) -> None:
    from dataclasses import fields

    context = build_context()
    print(f"LEVEL_HOME: {context.home}")
    print(f"Config file: {context.config_file}")

    print("Config values:")
    for field in fields(context.config):
        value = getattr(context.config, field.name)
        print(f"  {field.name}: {value}")


def handle_config_set(args: argparse.Namespace) -> None:
    context = build_context()

    # If no key provided → initialize defaults
    if args.key is None:
        initialize_defaults(context)
        print("[level] Configuration initialized (missing values filled with defaults)")
        return

    if args.value is None:
        print("[level] Usage: level config set <key> <value>")
        return

    try:
        save_config(context, {args.key: args.value})
    except ValueError as e:
        print(f"[level] {e}")
        return

    print(f"[level] Set {args.key} = {args.value}")


def handle_config_doctor(args: argparse.Namespace) -> None:
    context = build_context()

    fix = getattr(args, "fix", False)

    print("Running configuration diagnostics...\n")

    all_ok = True

    for check in CHECKS:
        ok, message = check(context, fix)
        status = "✔" if ok else "✖"
        print(f"{status} {message}")
        if not ok:
            all_ok = False

    if not all_ok and not fix:
        print("\nRun with --fix to attempt automatic repairs.")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction[Any]) -> None:
    config_parser = subparsers.add_parser(
        "config",
        help="Configuration and environment commands",
    )

    config_subparsers = config_parser.add_subparsers(dest="config_command")

    # config show
    parser_show = config_subparsers.add_parser(
        "show",
        help="Show configuration",
    )
    parser_show.set_defaults(func=handle_config_show)

    # config set
    parser_set = config_subparsers.add_parser(
        "set",
        help="Set config value",
    )
    parser_set.add_argument("key", nargs="?")
    parser_set.add_argument("value", nargs="?")
    parser_set.set_defaults(func=handle_config_set)

    # config doctor
    parser_doctor = config_subparsers.add_parser(
        "doctor",
        help="Validate setup",
    )
    parser_doctor.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to automatically fix detected issues",
    )
    parser_doctor.set_defaults(func=handle_config_doctor)
