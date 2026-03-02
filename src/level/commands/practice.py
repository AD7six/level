"""
Practice command module.

Responsible for registering and handling `level practice` subcommands.
"""

from __future__ import annotations

import argparse
import random
from collections.abc import Callable
from datetime import date
from functools import lru_cache
from typing import Any

from level.commands._doctor import make_doctor_handler
from level.commands._format import render_list, render_objects
from level.config import Context, build_context
from level.domains.practice import (
    create_practice,
    fix_practice,
    lint_practice,
    list_practice,
    list_practice_types,
    practice_metrics,
    review_latest_attempt,
)
from level.editor import open_in_editor
from level.templates.loader import list_templates


@lru_cache(maxsize=1)
def _context_for_help() -> Context:
    """Build the CLI context once for dynamic help discovery."""
    return build_context()


# ---------------------------------------------------------------------------
# LazyValue helper
# ---------------------------------------------------------------------------


class LazyValue:
    """Defers computation until converted to string (used for argparse help)."""

    def __init__(self, fn: Callable[[], Any]) -> None:
        self.fn = fn
        self._cached: str | None = None

    def __str__(self) -> str:
        if self._cached is None:
            try:
                value = self.fn()
                if isinstance(value, (list, tuple, set)):
                    self._cached = ", ".join(str(v) for v in value)
                else:
                    self._cached = str(value)
            except Exception:
                self._cached = ""
        return self._cached


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


def _practice_slug(exercise: object) -> str:
    return str(getattr(exercise, "slug", exercise))


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_practice_new(context: Context, args: argparse.Namespace) -> None:
    practice_date = date.fromisoformat(args.date) if args.date else None
    practice_type = args.type

    if getattr(args, "random", False):
        name = random.choice(DRILLS)
    else:
        name = getattr(args, "name", "exercise")

    practice = create_practice(
        context,
        practice_date,
        name=name,
        practice_type=practice_type,
    )
    print(f"Created practice exercise: {practice.slug}")

    # Open the initial exercise file if configured
    start_file = practice.start_file()
    if start_file:
        open_in_editor(
            start_file,
            auto_open=context.config.auto_open,
            editor=context.config.editor,
        )


def handle_practice_list(context: Context, args: argparse.Namespace) -> None:
    exercises = list(list_practice(context))
    if not exercises:
        print("No practice exercises found.")
        return

    print(render_objects(exercises, _practice_slug))


def handle_practice_review(context: Context, args: argparse.Namespace) -> None:
    slug = args.slug

    success = review_latest_attempt(
        context,
        slug,
        open_editor=open_in_editor,
        auto_open=context.config.auto_open,
        editor=context.config.editor,
    )

    if success:
        print(f"Reviewed practice exercise: {slug}")
    else:
        print("Review aborted; metadata not updated.")


def handle_practice_stats(context: Context, args: argparse.Namespace) -> None:
    metrics = practice_metrics(context)
    if not metrics:
        print("No practice data available.")
        return

    print(render_list([f"{key}: {value}" for key, value in metrics.items()]))


def handle_practice_archive(context: Context, args: argparse.Namespace) -> None:
    print("Not implemented yet.")


def handle_practice_types(context: Context, args: argparse.Namespace) -> None:
    types = list_practice_types(context)
    if not types:
        print("No practice types available.")
        return

    print(render_list(sorted(types)))


def handle_practice_templates(context: Context, args: argparse.Namespace) -> None:

    templates = list_templates(context, "practice")
    if not templates:
        print("No practice templates available.")
        return

    print(render_list(sorted(templates)))


# ---------------------------------------------------------------------------
# Doctor Handler
# ---------------------------------------------------------------------------

handle_practice_doctor = make_doctor_handler(
    lint_practice,
    fix_practice,
)

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
        help="Exercise type "
        f"({LazyValue(lambda: list_practice_types(_context_for_help()))})",
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

    # practice review
    parser_review = practice_subparsers.add_parser(
        "review",
        help="Review a practice drill",
    )
    parser_review.add_argument(
        "slug",
        help="Practice exercise slug",
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

    # practice templates
    parser_templates = practice_subparsers.add_parser(
        "templates",
        help="List available practice templates",
    )
    parser_templates.set_defaults(func=handle_practice_templates)

    # practice types
    parser_types = practice_subparsers.add_parser(
        "types",
        help="List available practice types",
    )
    parser_types.set_defaults(func=handle_practice_types)

    # practice doctor
    practice_doctor_parser = practice_subparsers.add_parser(
        "doctor",
        help="Lint and optionally fix practice structure",
    )
    practice_doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixes",
    )

    practice_doctor_parser.set_defaults(func=handle_practice_doctor)

    # Default help if no subcommand provided
    def _print_practice_help(context: Context, args: argparse.Namespace) -> None:
        args.parser.print_help()

    practice_parser.set_defaults(func=_print_practice_help, parser=practice_parser)
