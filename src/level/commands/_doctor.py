# src/level/commands/_doctor.py

import argparse
from collections.abc import Callable

from level.checks.base import Finding, FixResult
from level.config import Context
from level.commands._format import render_list


def make_doctor_handler(
    lint_fn: Callable[[Context], list[Finding]],
    fix_fn: Callable[[Context], list[FixResult]],
) -> Callable[[Context, argparse.Namespace], None]:
    def handler(context: Context, args: argparse.Namespace) -> None:

        if args.fix:
            results = fix_fn(context)
            if results:
                print("Actions performed:")
                print(render_list([r.message for r in results]))
            else:
                print("No changes required.")
        else:
            findings = lint_fn(context)
            if findings:
                print("Issues detected:")
                print(render_list([f.message for f in findings]))

                if any(f.fixable for f in findings):
                    print("\nSome issues are fixable. Run with --fix to apply changes.")
            else:
                print("No issues found.")

    return handler
