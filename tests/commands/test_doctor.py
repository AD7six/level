import argparse
from pathlib import Path

from level.checks.base import Finding, FixResult
from level.commands._doctor import make_doctor_handler
from level.config import Config, Context


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_lint_no_issues(tmp_path, capsys):
    context = _context(tmp_path)

    def lint_fn(ctx):
        return []

    def fix_fn(ctx):
        return []

    handler = make_doctor_handler(lint_fn, fix_fn)

    args = argparse.Namespace(fix=False)
    handler(context, args)

    out = capsys.readouterr().out.strip()
    assert out == "No issues found."


def test_lint_with_fixable_issue(tmp_path, capsys):
    context = _context(tmp_path)

    def lint_fn(ctx):
        return [Finding("problem", fixable=True)]

    def fix_fn(ctx):
        return []

    handler = make_doctor_handler(lint_fn, fix_fn)

    args = argparse.Namespace(fix=False)
    handler(context, args)

    out = capsys.readouterr().out

    assert "Issues detected:" in out
    assert "problem" in out
    assert "Some issues are fixable" in out


def test_fix_with_actions(tmp_path, capsys):
    context = _context(tmp_path)

    def lint_fn(ctx):
        return []

    def fix_fn(ctx):
        return [FixResult(entity=Path("x"), check_name="c", message="fixed")]

    handler = make_doctor_handler(lint_fn, fix_fn)

    args = argparse.Namespace(fix=True)
    handler(context, args)

    out = capsys.readouterr().out

    assert "Actions performed:" in out
    assert "fixed" in out


def test_fix_no_actions(tmp_path, capsys):
    context = _context(tmp_path)

    def lint_fn(ctx):
        return []

    def fix_fn(ctx):
        return []

    handler = make_doctor_handler(lint_fn, fix_fn)

    args = argparse.Namespace(fix=True)
    handler(context, args)

    out = capsys.readouterr().out.strip()
    assert out == "No changes required."
