"""
level CLI

A minimal no-op CLI stub for the `level` project.
"""

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
