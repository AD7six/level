"""
Apply command module.

Responsible for registering and handling `level apply` subcommands.
"""

import argparse


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_apply_new(args: argparse.Namespace) -> None:
    print("[level] Creating new application (not yet implemented)")


def handle_apply_list(args: argparse.Namespace) -> None:
    print("[level] Listing applications (not yet implemented)")


def handle_apply_show(args: argparse.Namespace) -> None:
    print("[level] Showing application details (not yet implemented)")


def handle_apply_status(args: argparse.Namespace) -> None:
    print("[level] Updating application status (not yet implemented)")


def handle_apply_archive(args: argparse.Namespace) -> None:
    print("[level] Archiving application (not yet implemented)")


def handle_apply_timeline(args: argparse.Namespace) -> None:
    print("[level] Showing application timeline (not yet implemented)")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction) -> None:
    apply_parser = subparsers.add_parser(
        "apply",
        help="Application tracking commands",
    )

    apply_subparsers = apply_parser.add_subparsers(dest="apply_command")

    # apply new
    apply_new_parser = apply_subparsers.add_parser(
        "new",
        help="Create new application entry",
    )
    apply_new_parser.set_defaults(func=handle_apply_new)

    # apply list
    apply_list_parser = apply_subparsers.add_parser(
        "list",
        help="List applications",
    )
    apply_list_parser.set_defaults(func=handle_apply_list)

    # apply show
    apply_show_parser = apply_subparsers.add_parser(
        "show",
        help="Show application details",
    )
    apply_show_parser.set_defaults(func=handle_apply_show)

    # apply status
    apply_status_parser = apply_subparsers.add_parser(
        "status",
        help="Move between pipeline stages",
    )
    apply_status_parser.set_defaults(func=handle_apply_status)

    # apply archive
    apply_archive_parser = apply_subparsers.add_parser(
        "archive",
        help="Archive completed / rejected",
    )
    apply_archive_parser.set_defaults(func=handle_apply_archive)

    # apply timeline
    apply_timeline_parser = apply_subparsers.add_parser(
        "timeline",
        help="Show application history",
    )
    apply_timeline_parser.set_defaults(func=handle_apply_timeline)
