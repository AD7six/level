"""
Practice command module.

Responsible for registering and handling `level practice` subcommands.
"""

from __future__ import annotations

import argparse
from datetime import date
from typing import Any
import random

from level.config import Context
from level.practice.practice import (
    create_practice,
    list_practice,
)

# ---------------------------------------------------------------------------
# Drill list (v0.5)
# ---------------------------------------------------------------------------

DRILLS = [
    # Logs 
    "log-parse-count-by-user",
    "log-parse-top-ip",
    "log-parse-error-rate",
    "log-parse-latency-percentile",
    "group-by-status-code",
    "deduplicate-log-entries",
    "sliding-window-error-spike",

    # General 
    "counter",
    "defaultdict-grouping",
    "heap-top-k",
    "dict-iteration",
    "log-parse-basic",
    "rolling-average",
    "deduplicate-preserve-order",
]

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_practice_new(context: Context, args: argparse.Namespace) -> None:
    practice_date = date.fromisoformat(args.date) if args.date else None

    practice_type = args.type or "code"

    if args.random:
        selected = random.choice(DRILLS)
    else:
        if not args.name:
            # Show help instead of raising
            if hasattr(args, "parser"):
                args.parser.print_help()
            return
        selected = args.name

    name_component = f"{practice_type}-{selected}"

    practice = create_practice(context, practice_date, name=name_component)
    print(f"Created practice session: {practice.slug}")


def handle_practice_list(context: Context, args: argparse.Namespace) -> None:
    sessions = list(list_practice(context))
    if not sessions:
        print("No practice sessions found.")
        return

    for session in sessions:
        print(session.slug)


def handle_practice_open(context: Context, args: argparse.Namespace) -> None:
    print("Not implemented yet.")


def handle_practice_review(context: Context, args: argparse.Namespace) -> None:
    print("Not implemented yet.")


def handle_practice_stats(context: Context, args: argparse.Namespace) -> None:
    print("Not implemented yet.")


def handle_practice_archive(context: Context, args: argparse.Namespace) -> None:
    print("Not implemented yet.")


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
    parser_new.add_argument(
        "name",
        nargs="?",
        help="Name of the exercise (e.g. two-sum, log-parse)",
    )
    parser_new.add_argument(
        "--random",
        action="store_true",
        help="Select a random drill",
    )
    parser_new.add_argument(
        "--type",
        default="code",
        help="Exercise type (default: code)",
    )
    parser_new.add_argument(
        "--date",
        help="Optional ISO date (YYYY-MM-DD)",
    )
    parser_new.set_defaults(func=handle_practice_new, parser=parser_new)

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

    # Default help if no subcommand provided
    practice_parser.set_defaults(
        func=lambda context, args, p=practice_parser: p.print_help()
    )
