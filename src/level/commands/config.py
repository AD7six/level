"""
Config command module.

Responsible for registering and handling `level config` subcommands.
"""

import argparse


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_config_show(args: argparse.Namespace) -> None:
    print("[level] Showing configuration (not yet implemented)")


def handle_config_set(args: argparse.Namespace) -> None:
    print("[level] Setting configuration value (not yet implemented)")


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
    parser_set.set_defaults(func=handle_config_set)

    # config doctor
    parser_doctor = config_subparsers.add_parser(
        "doctor",
        help="Validate setup",
    )
    parser_doctor.set_defaults(func=handle_config_doctor)
