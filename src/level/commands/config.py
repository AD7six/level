"""
Config command module.

Responsible for registering and handling `level config` subcommands.
"""

import argparse
from pathlib import Path
import os

ENV_VAR = "LEVEL_HOME"
DEFAULT_DIR_NAME = ".level"
CONFIG_FILE_NAME = "config.toml"


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_config_show(args: argparse.Namespace) -> None:
    print("[level] Showing configuration (not yet implemented)")


def handle_config_set(args: argparse.Namespace) -> None:
    if args.key is None or args.value is None:
        print("[level] Usage: level config set <key> <value>")
        return

    # Resolve level home
    level_home = Path(
        os.environ.get(ENV_VAR, Path.home() / DEFAULT_DIR_NAME)
    ).expanduser()

    level_home.mkdir(parents=True, exist_ok=True)

    config_file = level_home / CONFIG_FILE_NAME

    # Very simple key=value storage (TOML-like but minimal)
    existing = {}
    if config_file.exists():
        for line in config_file.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                existing[k.strip()] = v.strip()

    existing[args.key] = args.value

    content = "\n".join(f"{k} = {v}" for k, v in existing.items())
    config_file.write_text(content + "\n")

    print(f"[level] Set {args.key} = {args.value}")
    print(f"[level] Config file: {config_file}")


def handle_config_doctor(args: argparse.Namespace) -> None:
    print("[level] Validating setup (not yet implemented)")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction) -> None:
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
    parser_doctor.set_defaults(func=handle_config_doctor)
