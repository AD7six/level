"""
Review command module.

Responsible for registering and handling `level review` subcommands.
"""

import argparse

# --- Domain imports ---
from datetime import date
from typing import Any

from level.config import build_context
from level.reviews.reviews import (
    Review,
    fix_reviews,
    list_reviews,
    save_review,
)

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_review_weekly(args: argparse.Namespace) -> None:
    context = build_context()
    today = date.today()

    review = Review(
        date=today,
        period="weekly",
    )

    save_review(context, review)
    print(f"Created weekly review for {today.isoformat()}")


def handle_review_monthly(args: argparse.Namespace) -> None:
    context = build_context()
    today = date.today()

    review = Review(
        date=today,
        period="monthly",
    )

    save_review(context, review)
    print(f"Created monthly review for {today.isoformat()}")


def handle_review_annual(args: argparse.Namespace) -> None:
    context = build_context()
    today = date.today()

    review = Review(
        date=today,
        period="annual",
    )

    save_review(context, review)
    print(f"Created annual review for {today.isoformat()}")


def handle_review_quarterly(args: argparse.Namespace) -> None:
    context = build_context()
    today = date.today()

    review = Review(
        date=today,
        period="quarterly",
    )

    save_review(context, review)
    print(f"Created quarterly review for {today.isoformat()}")


def handle_review_metrics(args: argparse.Namespace) -> None:
    context = build_context()
    reviews = list_reviews(context)

    weekly = sum(1 for r in reviews if r.period == "weekly")
    monthly = sum(1 for r in reviews if r.period == "monthly")
    quarterly = sum(1 for r in reviews if r.period == "quarterly")
    annual = sum(1 for r in reviews if r.period == "annual")

    print(f"Weekly reviews: {weekly}")
    print(f"Monthly reviews: {monthly}")
    print(f"Quarterly reviews: {quarterly}")
    print(f"Annual reviews: {annual}")


def handle_review_history(args: argparse.Namespace) -> None:
    context = build_context()
    reviews = list_reviews(context)

    if not reviews:
        print("No reviews found.")
        return

    for r in reviews:
        print(f"{r.date.isoformat()}  {r.period}")


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

    def handle_review_doctor(args: argparse.Namespace) -> None:
        context = build_context()
        if args.fix:
            actions = fix_reviews(context)
            if actions:
                print("Actions performed:")
                for a in actions:
                    print(f"  - {a}")
            else:
                print("No changes required.")
        else:
            issues = []
            issues.extend(fix_reviews(context))
            if issues:
                print("Issues detected:")
                for i in issues:
                    print(f"  - {i}")
            else:
                print("No issues found.")

    parser_doctor.set_defaults(func=handle_review_doctor)

    # review history
    parser_history = review_subparsers.add_parser(
        "history",
        help="Show past reviews",
    )
    parser_history.set_defaults(func=handle_review_history)
