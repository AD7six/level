"""
level CLI

A minimal no-op CLI stub for the `level` project.
"""

# ---------------------------------------------------------------------------
# Intended CLI Command Tree (MVP → v1)
#
# level
# ├── apply
# │   ├── new             # Create new application entry
# │   ├── list            # List applications
# │   ├── show            # Show application details
# │   ├── status          # Move between pipeline stages
# │   ├── archive         # Archive completed / rejected
# │   └── timeline        # Show application history
# │
# ├── plan
# │   ├── show            # Show current long-term plan
# │   ├── edit            # Edit goals / target roles
# │   ├── gap             # Show skill gap analysis
# │   ├── goals           # List defined goals
# │   └── review          # Quarterly / periodic review
# │
# ├── practice
# │   ├── new             # Create new coding/system design exercise
# │   ├── list            # List exercises
# │   ├── open            # Open exercise workspace
# │   ├── review          # Review completed exercises
# │   ├── stats           # Weak areas / frequency tracking
# │   └── archive         # Archive old exercises
# │
# ├── resume
# │   ├── list            # List resume versions
# │   ├── new             # Create tailored resume
# │   ├── build           # Generate output (PDF, etc.)
# │   └── diff            # Compare resume versions
# │
# ├── review
# │   ├── weekly          # Weekly reflection
# │   ├── quarterly       # Quarterly review
# │   ├── metrics         # Show career metrics
# │   └── history         # Show past reviews
# │
# ├── stats
# │   ├── applications    # Application metrics
# │   ├── interviews      # Interview metrics
# │   ├── practice        # Practice metrics
# │   └── progression     # Level progression over time
# │
# └── config
#     ├── show            # Show configuration
#     ├── set             # Set config value
#     └── doctor          # Validate setup
#
# This represents the intended long-term shape of the CLI.
# The current implementation is a minimal stub.
# ---------------------------------------------------------------------------

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="level",
        description="A personal career operating system for engineers.",
    )

    subparsers = parser.add_subparsers(dest="command")

    # apply command
    subparsers.add_parser("apply", help="Application tracking commands (stub)")

    # plan command
    subparsers.add_parser("plan", help="Career planning commands (stub)")

    # practice command
    subparsers.add_parser("practice", help="Interview practice commands (stub)")

    # review command
    subparsers.add_parser("review", help="Career review commands (stub)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    print(f"[level] '{args.command}' command not yet implemented.")


if __name__ == "__main__":
    main()
