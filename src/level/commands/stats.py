
"""
Stats command module.

Responsible for registering and handling `level stats` subcommands.
"""

import argparse


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_stats_applications(args: argparse.Namespace) -> None:
    print("[level] Showing application metrics (not yet implemented)")


def handle_stats_interviews(args: argparse.Namespace) -> None:
    print("[level] Showing interview metrics (not yet implemented)")


def handle_stats_practice(args: argparse.Namespace) -> None:
    print("[level] Showing practice metrics (not yet implemented)")


def handle_stats_progression(args: argparse.Namespace) -> None:
    print("[level] Showing level progression over time (not yet implemented)")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction) -> None:
    stats_parser = subparsers.add_parser(
        "stats",
        help="Career statistics and metrics",
    )

    stats_subparsers = stats_parser.add_subparsers(dest="stats_command")

    # stats applications
    parser_applications = stats_subparsers.add_parser(
        "applications",
        help="Application metrics",
    )
    parser_applications.set_defaults(func=handle_stats_applications)

    # stats interviews
    parser_interviews = stats_subparsers.add_parser(
        "interviews",
        help="Interview metrics",
    )
    parser_interviews.set_defaults(func=handle_stats_interviews)

    # stats practice
    parser_practice = stats_subparsers.add_parser(
        "practice",
        help="Practice metrics",
    )
    parser_practice.set_defaults(func=handle_stats_practice)

    # stats progression
    parser_progression = stats_subparsers.add_parser(
        "progression",
        help="Level progression over time",
    )
    parser_progression.set_defaults(func=handle_stats_progression)
