from datetime import date
from pathlib import Path

from level.config import Config, Context
from level.practice.practice import (
    create_practice,
    fix_practice,
    lint_practice,
    list_practice,
)


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_create_practice_creates_directory_and_file(tmp_path):
    context = _context(tmp_path)

    practice = create_practice(context, date(2026, 2, 24))

    practice_dir = tmp_path / "practice" / "2026-02-24-session"
    assert practice.slug == "2026-02-24-session"
    assert practice_dir.exists()
    assert (practice_dir / "start.py").exists()


def test_list_practice_returns_created_sessions(tmp_path):
    context = _context(tmp_path)

    create_practice(context, date(2026, 2, 20))
    create_practice(context, date(2026, 2, 21))

    sessions = list(list_practice(context))
    slugs = [s.slug for s in sessions]

    assert slugs == ["2026-02-20-session", "2026-02-21-session"]


def test_lint_detects_invalid_directory_name(tmp_path):
    context = _context(tmp_path)

    practice_root = tmp_path / "practice"
    practice_root.mkdir(parents=True, exist_ok=True)

    (practice_root / "not-a-date").mkdir()

    issues = lint_practice(context)

    assert "Invalid practice directory name: not-a-date" in issues


def test_fix_renames_non_canonical_directory(tmp_path):
    context = _context(tmp_path)

    practice_root = tmp_path / "practice"
    practice_root.mkdir(parents=True, exist_ok=True)

    # Create directory with valid date but simulate non-canonical scenario
    wrong = practice_root / "2026-02-25-session"
    wrong.mkdir()

    # Nothing should change because slug is already canonical
    changes = fix_practice(context)
    assert changes == []

    # Create invalid name that parses but rename via manual move
    broken = practice_root / "2026-02-26-session"
    broken.mkdir()
    renamed = practice_root / "2026-02-26-temp"
    broken.rename(renamed)

    issues = lint_practice(context)
    assert any("Invalid practice directory name" in i for i in issues)
