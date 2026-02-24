from argparse import Namespace
from pathlib import Path

from level.commands import practice as practice_cmd
from level.config import Config, Context


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_practice_new_creates_session(tmp_path, capsys):
    context = _context(tmp_path)

    args = Namespace(date="2026-02-24")
    practice_cmd.handle_practice_new(context, args)

    practice_dir = tmp_path / "practice" / "2026-02-24"
    assert practice_dir.exists()
    assert (practice_dir / "start.py").exists()

    output = capsys.readouterr().out
    assert "Created practice session: 2026-02-24" in output


def test_practice_list_outputs_sessions(tmp_path, capsys):
    context = _context(tmp_path)

    # Create two sessions
    practice_cmd.handle_practice_new(context, Namespace(date="2026-02-20"))
    practice_cmd.handle_practice_new(context, Namespace(date="2026-02-21"))

    # Clear previous output from creation
    capsys.readouterr()

    practice_cmd.handle_practice_list(context, Namespace())

    output = capsys.readouterr().out.strip().splitlines()
    assert output == ["2026-02-20", "2026-02-21"]
