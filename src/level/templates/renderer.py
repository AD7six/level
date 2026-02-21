from __future__ import annotations

from pathlib import Path
from typing import Any

from .loader import load_template


class TemplateRenderError(ValueError):
    """Raised when template rendering fails due to missing variables."""


def render_template_to_string(template_name: str, context: dict[str, Any]) -> str:
    """
    Render a named template using the provided context.

    Uses Python's built-in str.format().

    Raises:
        TemplateRenderError if required template variables are missing.
    """
    template = load_template(template_name)

    try:
        return template.format(**context)
    except KeyError as exc:
        missing = exc.args[0]
        raise TemplateRenderError(f"Missing template variable: {missing}") from exc


def render_template_to_path(
    template_name: str,
    context: dict[str, Any],
    output_path: Path,
    overwrite: bool = False,
) -> Path:
    """
    Render a template and write it to disk.

    Args:
        template_name: Relative template path (e.g. "review/weekly.md.tmpl")
        context: Variables used in template formatting
        output_path: Destination file path
        overwrite: If False and file exists, raises FileExistsError

    Returns:
        The path written to.
    """
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {output_path}")

    rendered = render_template_to_string(template_name, context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")

    return output_path
