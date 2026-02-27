"""
Review command module.

Responsible for registering and handling `level review` subcommands.
"""

import argparse
from collections.abc import Callable

# --- Domain imports ---
from datetime import date
from typing import Any

from level.commands._doctor import make_doctor_handler
from level.commands._format import render_objects
from level.config import Context
from level.domains.reviews import (
    Review,
    fix_reviews,
    get_review_metrics,
    lint_reviews,
    list_reviews,
    save_review,
)

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _make_period_handler(period: str) -> Callable[[Context, argparse.Namespace], None]:
    def handler(context: Context, args: argparse.Namespace) -> None:
        today = date.today()

        review = Review(
            date=today,
            period=period,
        )

        save_review(context, review)
        print(f"Created {period} review for {today.isoformat()}")

    return handler


handle_review_weekly = _make_period_handler("weekly")
handle_review_monthly = _make_period_handler("monthly")
handle_review_quarterly = _make_period_handler("quarterly")
handle_review_annual = _make_period_handler("annual")


def handle_review_metrics(context: Context, args: argparse.Namespace) -> None:
    metrics = get_review_metrics(context)

    print(f"Weekly reviews: {metrics['weekly']}")
    print(f"Monthly reviews: {metrics['monthly']}")
    print(f"Quarterly reviews: {metrics['quarterly']}")
    print(f"Annual reviews: {metrics['annual']}")


def handle_review_history(context: Context, args: argparse.Namespace) -> None:
    reviews = list_reviews(context)

    if not reviews:
        print("No reviews found.")
        return

    print(
        render_objects(
            reviews,
            lambda r: f"{r.date.isoformat()}  {r.period}",
        )
    )


# ---------------------------------------------------------------------------
# Doctor Handler
# ---------------------------------------------------------------------------


def handle_review_doctor(context: Context, args: argparse.Namespace) -> None:
    handler = make_doctor_handler(lint_reviews, fix_reviews)
    handler(context, args)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction[Any]) -> None:
    review_parser = subparsers.add_parser(
        "review",
        help="Career review commands",
    )

    review_subparsers = review_parser.add_subparsers(dest="review_command")

    # review weekly
    parser_weekly = review_subparsers.add_parser(
        "weekly",
        help="Weekly reflection",
    )
    parser_weekly.set_defaults(func=handle_review_weekly)

    # review monthly
    parser_monthly = review_subparsers.add_parser(
        "monthly",
        help="Monthly review",
    )
    parser_monthly.set_defaults(func=handle_review_monthly)

    # review quarterly
    parser_quarterly = review_subparsers.add_parser(
        "quarterly",
        help="Quarterly review",
    )
    parser_quarterly.set_defaults(func=handle_review_quarterly)

    # review annual
    parser_annual = review_subparsers.add_parser(
        "annual",
        help="Annual review",
    )
    parser_annual.set_defaults(func=handle_review_annual)

    # review metrics
    parser_metrics = review_subparsers.add_parser(
        "metrics",
        help="Show career metrics",
    )
    parser_metrics.set_defaults(func=handle_review_metrics)

    # review doctor
    parser_doctor = review_subparsers.add_parser(
        "doctor",
        help="Validate and fix review structure",
    )
    parser_doctor.add_argument("--fix", action="store_true", help="Apply fixes")

    parser_doctor.set_defaults(func=handle_review_doctor)

    # review history
    parser_history = review_subparsers.add_parser(
        "history",
        help="Show past reviews",
    )
    parser_history.set_defaults(func=handle_review_history)
