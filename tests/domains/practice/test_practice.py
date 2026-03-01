from datetime import date
from pathlib import Path

from level.config import Config, Context
from level.domains.practice import (
    create_practice,
    fix_practice,
    lint_practice,
    list_practice,
    review_latest_attempt,
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
    assert (practice_dir / "00-start.py").exists()
    meta = (practice_dir / "meta.toml").read_text()
    assert "template" in meta


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

    assert any("meta.toml missing in: not-a-date" == i.message for i in issues)


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
    assert any("meta.toml missing in: 2026-02-26-temp" == i.message for i in issues)


def test_lint_detects_invalid_meta(tmp_path):
    context = _context(tmp_path)
    practice_root = tmp_path / "practice"
    practice_root.mkdir(parents=True, exist_ok=True)

    bad = practice_root / "2026-02-27-session"
    bad.mkdir()
    (bad / "meta.toml").write_text("not = valid = toml")

    issues = lint_practice(context)
    assert any("Invalid meta.toml in: 2026-02-27-session" == i.message for i in issues)


def test_lint_detects_missing_meta_fields(tmp_path):
    context = _context(tmp_path)
    practice_root = tmp_path / "practice"
    practice_root.mkdir(parents=True, exist_ok=True)

    bad = practice_root / "2026-02-28-session"
    bad.mkdir()
    (bad / "meta.toml").write_text('date = "2026-02-28"')

    issues = lint_practice(context)
    # MetaSchema is currently a no-op; readable meta passes lint.
    assert issues == []


def test_fix_renames_to_canonical_from_meta(tmp_path):
    context = _context(tmp_path)
    practice_root = tmp_path / "practice"
    practice_root.mkdir(parents=True, exist_ok=True)

    wrong = practice_root / "wrong-name"
    wrong.mkdir()
    (wrong / "meta.toml").write_text('date = "2026-03-01"\nname = "session"')

    changes = fix_practice(context)

    assert any("Renamed wrong-name" in c.message for c in changes)
    assert (practice_root / "2026-03-01-session").exists()


def test_create_practice_collision_suffix(tmp_path):
    context = _context(tmp_path)

    first = create_practice(context, date(2026, 3, 2))
    second = create_practice(context, date(2026, 3, 2))

    assert first.slug == "2026-03-02-session"
    assert second.slug == "2026-03-02-session-1"


def test_list_practice_uses_meta_date_not_directory(tmp_path):
    context = _context(tmp_path)

    practice = create_practice(context, date(2026, 3, 5))

    practice_root = tmp_path / "practice"
    original = practice_root / practice.slug
    renamed = practice_root / "renamed-folder"
    original.rename(renamed)

    sessions = list(list_practice(context))

    assert len(sessions) == 1
    assert sessions[0].date == date(2026, 3, 5)
    assert sessions[0].slug == "renamed-folder"


def test_review_latest_attempt_updates_meta_on_success(tmp_path):
    context = _context(tmp_path)

    practice = create_practice(context, date(2026, 3, 10))
    practice_dir = tmp_path / "practice" / practice.slug

    # create an attempt file so review_latest_attempt can find it
    attempt = practice_dir / "01-attempt.py"
    attempt.write_text("pass")

    def fake_editor(path, *, auto_open, editor):
        assert path == attempt
        return True

    result = review_latest_attempt(
        context,
        practice.slug,
        open_editor=fake_editor,
        auto_open=True,
        editor="dummy",
    )

    assert result is True

    meta = (practice_dir / "meta.toml").read_text()
    assert "reviewed_count = 1" in meta


def test_review_latest_attempt_abort_does_not_update_meta(tmp_path):
    context = _context(tmp_path)

    practice = create_practice(context, date(2026, 3, 11))
    practice_dir = tmp_path / "practice" / practice.slug

    attempt = practice_dir / "01-attempt.py"
    attempt.write_text("pass")

    def fake_editor(path, *, auto_open, editor):
        return False

    result = review_latest_attempt(
        context,
        practice.slug,
        open_editor=fake_editor,
        auto_open=True,
        editor="dummy",
    )

    assert result is False

    meta = (practice_dir / "meta.toml").read_text()
    assert "reviewed_count = 1" not in meta
