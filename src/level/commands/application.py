"""
Apply command module.

Responsible for registering and handling `level application` subcommands.
"""

import argparse
from datetime import date, datetime

from level.commands._doctor import make_doctor_handler
from level.commands._format import render_grouped_rows
from level.config import Context
from level.domains.applications import (
    create_application,
    fix_applications,
    get_application,
    lint_applications,
    list_application_rows,
    move_application,
)
from level.domains.applications.schema import SORTED_STATES

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_application_new(context: Context, args: argparse.Namespace) -> None:

    company = args.company
    role = args.role

    interactive = company is None or role is None

    try:
        while not company:
            company = input("Company: ").strip()
    except EOFError:
        raise SystemExit("Aborted.") from None

    try:
        while not role:
            role = input("Role: ").strip()
    except EOFError:
        raise SystemExit("Aborted.") from None

    if interactive:
        default_date = args.date
        try:
            date_input = input(
                f"Application date (YYYY-MM-DD) [{default_date}]: "
            ).strip()
        except EOFError:
            raise SystemExit("Aborted.") from None
        if date_input:
            args.date = date_input

    try:
        validated_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit("Invalid date format. Use YYYY-MM-DD.") from None

    app = create_application(context, company, role, validated_date.isoformat())
    print(f"✔ Created {app.slug}")
    print(f"  Company: {app.company}")
    print(f"  Role:    {app.role}")
    print(f"  State:   {app.state}")


def handle_application_list(context: Context, args: argparse.Namespace) -> None:
    rows = list_application_rows(
        context,
        state=args.state,
        include_terminal=getattr(args, "all", False),
    )

    if not rows:
        return

    print(
        render_grouped_rows(
            rows,
            group_key="state",
            group_header_formatter=lambda s: s.upper(),
            row_formatter=lambda row: (
                f"  {row['date']:12}  {row['company']:<22} "
                f"{row['role']:<40} ({row['slug']})"
            ),
        )
    )


def handle_application_show(context: Context, args: argparse.Namespace) -> None:
    app = get_application(context, args.slug)

    print(f"Slug:       {app.slug}")
    print(f"State:      {app.state}")
    print(f"Company:    {app.company}")
    print(f"Role:       {app.role}")
    print(f"Created At: {app.created_at}")
    print(f"Path:       {app.path}")


def handle_application_move(context: Context, args: argparse.Namespace) -> None:
    app = move_application(context, args.slug, args.state)
    print(f"✔ Moved '{app.slug}' to '{app.state}'")


def handle_application_timeline(context: Context, args: argparse.Namespace) -> None:
    # Timeline not yet implemented – placeholder for future domain expansion
    print("Timeline not yet implemented.")


# ---------------------------------------------------------------------------
# Doctor Handler
# ---------------------------------------------------------------------------

handle_application_doctor = make_doctor_handler(
    lint_applications,
    fix_applications,
)

# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    application_parser = subparsers.add_parser(
        "application",
        help="Application tracking commands",
    )

    application_subparsers = application_parser.add_subparsers(
        dest="application_command"
    )

    # application new
    application_new_parser = application_subparsers.add_parser(
        "new",
        help="Create new application entry",
    )
    application_new_parser.add_argument(
        "--date", help="Application date", default=date.today().strftime("%Y-%m-%d")
    )
    application_new_parser.add_argument("--company", help="Company name")
    application_new_parser.add_argument("--role", help="Role title")
    application_new_parser.set_defaults(func=handle_application_new)

    # application list
    application_list_parser = application_subparsers.add_parser(
        "list",
        help="List applications",
    )
    application_list_parser.add_argument(
        "--state",
        choices=SORTED_STATES,
        help="Filter by state",
    )
    application_list_parser.add_argument(
        "--all",
        action="store_true",
        help="Include terminal states",
    )
    application_list_parser.set_defaults(func=handle_application_list)

    # application show
    application_show_parser = application_subparsers.add_parser(
        "show",
        help="Show application details",
    )
    application_show_parser.add_argument("slug", help="Application slug")
    application_show_parser.set_defaults(func=handle_application_show)

    # application move
    application_move_parser = application_subparsers.add_parser(
        "move",
        help="Move between pipeline stages",
    )
    application_move_parser.add_argument("slug", help="Application slug")
    application_move_parser.add_argument(
        "state",
        choices=SORTED_STATES,
        help="New state",
    )
    application_move_parser.set_defaults(func=handle_application_move)

    # application doctor
    application_doctor_parser = application_subparsers.add_parser(
        "doctor",
        help="Lint and optionally fix application structure",
    )
    application_doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixes",
    )
    application_doctor_parser.set_defaults(func=handle_application_doctor)

    # application timeline
    application_timeline_parser = application_subparsers.add_parser(
        "timeline",
        help="Show application timeline",
    )
    application_timeline_parser.add_argument("slug", help="Application slug")
    application_timeline_parser.set_defaults(func=handle_application_timeline)
