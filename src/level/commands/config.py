"""
Config command module.
"""

import argparse
from typing import Any

from level.config import (
    Context,
    initialize_defaults,
    run_diagnostics,
    save_config,
)

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_config_show(context: Context, args: argparse.Namespace) -> None:
    from dataclasses import fields

    print(f"LEVEL_HOME: {context.home}")
    print(f"Config file: {context.config_file}")

    print("Config values:")
    for field in fields(context.config):
        value = getattr(context.config, field.name)
        print(f"  {field.name}: {value}")


def handle_config_set(context: Context, args: argparse.Namespace) -> None:
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


def handle_config_doctor(context: Context, args: argparse.Namespace) -> None:
    fix = getattr(args, "fix", False)

    print("Running configuration diagnostics...\n")

    results = run_diagnostics(context, fix)

    all_ok = True
    for result in results:
        status = "✔" if result.ok else "✖"
        print(f"{status} {result.message}")
        if not result.ok:
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
