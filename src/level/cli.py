"""
level CLI

Dispatcher-based CLI for the `level` project.
"""

import argparse
from typing import Callable

import importlib
import pkgutil
import level.commands


# ---------------------------------------------------------------------------
# Registration Helpers
# ---------------------------------------------------------------------------


def register_command(
    subparsers: argparse._SubParsersAction,
    name: str,
    help_text: str,
) -> argparse.ArgumentParser:
    return subparsers.add_parser(name, help=help_text)


# ---------------------------------------------------------------------------
# Parser Construction
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="level",
        description="A personal career operating system for engineers.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Load all commands in the command folder
    for _, module_name, _ in pkgutil.iter_modules(level.commands.__path__):
        module = importlib.import_module(f"level.commands.{module_name}")
        if hasattr(module, "register"):
            module.register(subparsers)

    return parser


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
