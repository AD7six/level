# src/level/commands/_doctor.py

import argparse
from collections.abc import Callable

from level.checks.base import Finding, FixResult
from level.config import Context


def make_doctor_handler(
    lint_fn: Callable[[Context], list[Finding]],
    fix_fn: Callable[[Context], list[FixResult]],
) -> Callable[[Context, argparse.Namespace], None]:
    def handler(context: Context, args: argparse.Namespace) -> None:

        if args.fix:
            results = fix_fn(context)
            if results:
                print("Actions performed:")
                for r in results:
                    print(f"  - {r.message}")
            else:
                print("No changes required.")
        else:
            findings = lint_fn(context)
            if findings:
                print("Issues detected:")
                for f in findings:
                    print(f"  - {f.message}")

                if any(f.fixable for f in findings):
                    print("\nSome issues are fixable. Run with --fix to apply changes.")
            else:
                print("No issues found.")

    return handler
