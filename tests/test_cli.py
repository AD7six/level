import sys
from contextlib import redirect_stdout
from io import StringIO


def test_build_parser():
    from level.cli import build_parser

    parser = build_parser(prog_name="level")
    assert parser is not None


def test_group_command_prints_help(monkeypatch):
    """
    Ensure invoking a command group without a subcommand
    prints help and exits cleanly.
    """

    from level.cli import main

    # Simulate: level application
    monkeypatch.setattr(sys, "argv", ["level", "application"])

    stdout = StringIO()
    with redirect_stdout(stdout):
        try:
            main()
        except SystemExit as e:
            # argparse typically exits with code 0 for help
            assert e.code == 0

    output = stdout.getvalue()
    assert "usage:" in output
    assert "application" in output
