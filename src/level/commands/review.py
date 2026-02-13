"""
Review command module.

Responsible for registering and handling `level review` subcommands.
"""

import argparse


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_review_weekly(args: argparse.Namespace) -> None:
    print("[level] Running weekly reflection (not yet implemented)")


def handle_review_quarterly(args: argparse.Namespace) -> None:
    print("[level] Running quarterly review (not yet implemented)")


def handle_review_metrics(args: argparse.Namespace) -> None:
    print("[level] Showing career metrics (not yet implemented)")


def handle_review_history(args: argparse.Namespace) -> None:
    print("[level] Showing past reviews (not yet implemented)")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction) -> None:
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

    # review quarterly
    parser_quarterly = review_subparsers.add_parser(
        "quarterly",
        help="Quarterly review",
    )
    parser_quarterly.set_defaults(func=handle_review_quarterly)

    # review metrics
    parser_metrics = review_subparsers.add_parser(
        "metrics",
        help="Show career metrics",
    )
    parser_metrics.set_defaults(func=handle_review_metrics)

    # review history
    parser_history = review_subparsers.add_parser(
        "history",
        help="Show past reviews",
    )
    parser_history.set_defaults(func=handle_review_history)
