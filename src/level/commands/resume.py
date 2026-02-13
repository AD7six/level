"""
Resume command module.

Responsible for registering and handling `level resume` subcommands.
"""

import argparse
from typing import Any

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_resume_list(args: argparse.Namespace) -> None:
    print("[level] Listing resume versions (not yet implemented)")


def handle_resume_new(args: argparse.Namespace) -> None:
    print("[level] Creating tailored resume (not yet implemented)")


def handle_resume_build(args: argparse.Namespace) -> None:
    print("[level] Building resume output (not yet implemented)")


def handle_resume_diff(args: argparse.Namespace) -> None:
    print("[level] Comparing resume versions (not yet implemented)")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction[Any]) -> None:
    resume_parser = subparsers.add_parser(
        "resume",
        help="Resume management commands",
    )

    resume_subparsers = resume_parser.add_subparsers(dest="resume_command")

    # resume list
    parser_list = resume_subparsers.add_parser(
        "list",
        help="List resume versions",
    )
    parser_list.set_defaults(func=handle_resume_list)

    # resume new
    parser_new = resume_subparsers.add_parser(
        "new",
        help="Create tailored resume",
    )
    parser_new.set_defaults(func=handle_resume_new)

    # resume build
    parser_build = resume_subparsers.add_parser(
        "build",
        help="Generate output (PDF, etc.)",
    )
    parser_build.set_defaults(func=handle_resume_build)

    # resume diff
    parser_diff = resume_subparsers.add_parser(
        "diff",
        help="Compare resume versions",
    )
    parser_diff.set_defaults(func=handle_resume_diff)
