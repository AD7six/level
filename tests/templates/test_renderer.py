from pathlib import Path

import pytest

from level.config import Config, Context
from level.templates.renderer import (
    TemplateRenderError,
    render_template_directory,
    render_template_to_path,
    render_template_to_string,
)


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def _write_template(tmp_path: Path, rel: str, content: str) -> None:
    path = tmp_path / "templates" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_render_template_to_string_lax(tmp_path):
    context = _context(tmp_path)

    _write_template(tmp_path, "example.txt.tmpl", "Hello {name} {missing}")

    result = render_template_to_string(
        context,
        "example.txt.tmpl",
        {"name": "World"},
        strict=False,
    )

    assert result == "Hello World {missing}"


def test_render_template_to_string_strict_missing(tmp_path):
    context = _context(tmp_path)

    _write_template(tmp_path, "example.txt.tmpl", "Hello {name}")

    with pytest.raises(TemplateRenderError):
        render_template_to_string(
            context,
            "example.txt.tmpl",
            {},
            strict=True,
        )


def test_render_template_to_path_writes_file(tmp_path):
    context = _context(tmp_path)

    _write_template(tmp_path, "example.txt.tmpl", "Value: {x}")

    output = tmp_path / "out.txt"

    path = render_template_to_path(
        context,
        "example.txt.tmpl",
        {"x": 42},
        output,
        overwrite=False,
        strict=True,
    )

    assert path == output
    assert output.read_text(encoding="utf-8") == "Value: 42"


def test_render_template_to_path_respects_overwrite(tmp_path):
    context = _context(tmp_path)

    _write_template(tmp_path, "example.txt.tmpl", "X")

    output = tmp_path / "out.txt"
    output.write_text("existing")

    with pytest.raises(FileExistsError):
        render_template_to_path(
            context,
            "example.txt.tmpl",
            {},
            output,
            overwrite=False,
        )


def test_render_template_directory(tmp_path):
    context = _context(tmp_path)

    _write_template(tmp_path, "dir/a.txt.tmpl", "A {v}")
    _write_template(tmp_path, "dir/sub/b.txt.tmpl", "B {v}")

    output_dir = tmp_path / "rendered"

    render_template_directory(
        context,
        "dir",
        {"v": "ok"},
        output_dir,
        strict=True,
    )

    assert (output_dir / "a.txt").read_text() == "A ok"
    assert (output_dir / "sub" / "b.txt").read_text() == "B ok"
