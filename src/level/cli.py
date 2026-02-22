"""
level CLI

Dispatcher-based CLI for the `level` project.
"""

import argparse
import importlib
import pkgutil
import sys
from pathlib import Path
from typing import Any, cast

import level.commands
from level import __version__
from level.logging import configure_logging

# ---------------------------------------------------------------------------
# Registration Helpers
# ---------------------------------------------------------------------------


def register_command(
    subparsers: argparse._SubParsersAction[Any],
    name: str,
    help_text: str,
) -> argparse.ArgumentParser:
    return cast(argparse.ArgumentParser, subparsers.add_parser(name, help=help_text))


# ---------------------------------------------------------------------------
# Parser Construction
# ---------------------------------------------------------------------------


def build_parser(prog_name: str | None = None) -> argparse.ArgumentParser:
    # Use the executable name as the program name for help messages, except if
    # explicitly provided (tests)
    if prog_name is None:
        prog_name = Path(sys.argv[0]).name

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=prog_name,
        description="A personal career operating system for engineers.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        "--debug",
        dest="debug",
        action="store_true",
        help="Enable debug logging.",
    )

    subparsers: argparse._SubParsersAction[Any] = parser.add_subparsers(dest="command")

    # Load all commands in the command folder
    for _, module_name, _ in pkgutil.iter_modules(level.commands.__path__):
        module = importlib.import_module(f"level.commands.{module_name}")
        if hasattr(module, "register"):
            module.register(subparsers)

    # Automatically attach help-as-default for command groups that
    # define subparsers but did not explicitly set a default handler.
    for subparser in subparsers.choices.values():
        # If the parser already defines a default func, respect it.
        if "func" in getattr(subparser, "_defaults", {}):
            continue

        # If the parser has its own subparsers, attach help as default.
        for action in subparser._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparser.set_defaults(func=lambda args, p=subparser: p.print_help())
                break

    return parser


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()

    # Pre-parse only global flags (without triggering subparser parsing) so
    # flags like --debug are position independent.
    global_parser = argparse.ArgumentParser(add_help=False)
    global_parser.add_argument(
        "-v",
        "--verbose",
        "--debug",
        dest="debug",
        action="store_true",
    )

    global_args, remaining = global_parser.parse_known_args()

    # Configure logging early
    configure_logging(debug=getattr(global_args, "debug", False))

    # Now parse full CLI with remaining args
    args = parser.parse_args(remaining)

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
