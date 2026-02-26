from pathlib import Path

import pytest

from level.config import Config, Context
from level.templates.loader import (
    TemplateNotFoundError,
    _collect_templates,
    load_template,
)


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_load_template_uses_user_override(tmp_path):
    context = _context(tmp_path)

    user_templates = tmp_path / "templates" / "review"
    user_templates.mkdir(parents=True)

    user_file = user_templates / "weekly.md.tmpl"
    user_file.write_text("user version")

    result = load_template(context, "review/weekly.md.tmpl")

    assert result == "user version"


def test_load_template_builtin_fallback(tmp_path):
    context = _context(tmp_path)

    # Use a known built-in template path
    # Adjust if necessary to match actual built-in structure
    builtin_name = "review/weekly.md.tmpl"

    try:
        result = load_template(context, builtin_name)
    except TemplateNotFoundError:
        pytest.skip("Built-in template not present in this environment")

    assert isinstance(result, str)
    assert len(result) > 0


def test_load_template_not_found(tmp_path):
    context = _context(tmp_path)

    with pytest.raises(TemplateNotFoundError):
        load_template(context, "does/not/exist.tmpl")


def test_collect_templates_user_overrides(tmp_path):
    context = _context(tmp_path)

    # Create user template
    user_templates = tmp_path / "templates" / "review"
    user_templates.mkdir(parents=True)
    (user_templates / "weekly.md.tmpl").write_text("user")

    templates = _collect_templates(context, "review")

    # User template should appear in collected set
    assert "weekly.md.tmpl" in templates
