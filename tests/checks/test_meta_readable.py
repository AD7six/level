from pathlib import Path

from level.checks.meta_readable import MetaReadable
from level.config import Config, Context


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_lint_reports_missing_meta(tmp_path):
    context = _context(tmp_path)

    entity = tmp_path / "item"
    entity.mkdir()

    check = MetaReadable()

    findings = check.lint(context, entity)

    assert len(findings) == 1
    assert "meta.toml missing" in findings[0].message
    assert findings[0].fixable is False


def test_lint_reports_invalid_meta(tmp_path):
    context = _context(tmp_path)

    entity = tmp_path / "item"
    entity.mkdir()

    meta = entity / "meta.toml"
    meta.write_text("not = valid = toml")

    check = MetaReadable()

    findings = check.lint(context, entity)

    assert len(findings) == 1
    assert "Invalid meta.toml" in findings[0].message
    assert findings[0].fixable is False


def test_lint_passes_valid_meta(tmp_path):
    context = _context(tmp_path)

    entity = tmp_path / "item"
    entity.mkdir()

    meta = entity / "meta.toml"
    meta.write_text('name = "ok"')

    check = MetaReadable()

    findings = check.lint(context, entity)

    assert findings == []
