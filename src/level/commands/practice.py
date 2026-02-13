"""
Practice command module.

Responsible for registering and handling `level practice` subcommands.
"""

import argparse
from typing import Any

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_practice_new(args: argparse.Namespace) -> None:
    print("[level] Creating new exercise (not yet implemented)")


def handle_practice_list(args: argparse.Namespace) -> None:
    print("[level] Listing exercises (not yet implemented)")


def handle_practice_open(args: argparse.Namespace) -> None:
    print("[level] Opening exercise workspace (not yet implemented)")


def handle_practice_review(args: argparse.Namespace) -> None:
    print("[level] Reviewing completed exercises (not yet implemented)")


def handle_practice_stats(args: argparse.Namespace) -> None:
    print("[level] Showing practice stats (not yet implemented)")


def handle_practice_archive(args: argparse.Namespace) -> None:
    print("[level] Archiving old exercises (not yet implemented)")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction[Any]) -> None:
    practice_parser = subparsers.add_parser(
        "practice",
        help="Interview practice commands",
    )

    practice_subparsers = practice_parser.add_subparsers(dest="practice_command")

    # practice new
    parser_new = practice_subparsers.add_parser(
        "new",
        help="Create new coding/system design exercise",
    )
    parser_new.set_defaults(func=handle_practice_new)

    # practice list
    parser_list = practice_subparsers.add_parser(
        "list",
        help="List exercises",
    )
    parser_list.set_defaults(func=handle_practice_list)

    # practice open
    parser_open = practice_subparsers.add_parser(
        "open",
        help="Open exercise workspace",
    )
    parser_open.set_defaults(func=handle_practice_open)

    # practice review
    parser_review = practice_subparsers.add_parser(
        "review",
        help="Review completed exercises",
    )
    parser_review.set_defaults(func=handle_practice_review)

    # practice stats
    parser_stats = practice_subparsers.add_parser(
        "stats",
        help="Weak areas / frequency tracking",
    )
    parser_stats.set_defaults(func=handle_practice_stats)

    # practice archive
    parser_archive = practice_subparsers.add_parser(
        "archive",
        help="Archive old exercises",
    )
    parser_archive.set_defaults(func=handle_practice_archive)
