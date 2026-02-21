from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable


class TemplateNotFoundError(FileNotFoundError):
    """Raised when a template file cannot be located."""


def _template_base() -> Traversable:
    """
    Return the base Traversable for built-in template files.

    Templates are stored under:
        src/level/templates/files/
    """
    return resources.files("level.templates").joinpath("files")


def load_template(template_name: str) -> str:
    """
    Load a template file by relative name.

    Example:
        load_template("review/weekly.md.tmpl")

    Raises:
        TemplateNotFoundError if the template does not exist.
    """
    base = _template_base()
    template_path = base.joinpath(template_name)

    if not template_path.is_file():
        raise TemplateNotFoundError(f"Template not found: {template_name}")

    return template_path.read_text(encoding="utf-8")
