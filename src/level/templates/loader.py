from __future__ import annotations

import logging
from importlib import resources
from importlib.resources import as_file
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Iterable

from level.config import Context, get_data_root

logger = logging.getLogger("level.templates")


class TemplateNotFoundError(FileNotFoundError):
    """Raised when a template file cannot be located."""


# ---------------------------------------------------------------------------
# Template roots
# ---------------------------------------------------------------------------


def _builtin_template_root() -> Traversable:
    """
    Built-in templates packaged with level.

    Stored under:
        src/level/templates/files/
    """
    return resources.files("level.templates").joinpath("files")


def _user_template_root(context: Context) -> Path:
    """
    User templates stored inside the career-data repo.

    Expected location:
        <data_dir>/templates/
    """
    return get_data_root(context) / "templates"


# ---------------------------------------------------------------------------
# Template loading (single file)
# ---------------------------------------------------------------------------


def load_template(context: Context, template_name: str) -> str:
    """
    Load a template file by relative name.

    Precedence:
        1. career-data templates
        2. built-in templates

    Example:
        load_template(context, "review/weekly.md.tmpl")

    Raises:
        TemplateNotFoundError if the template does not exist.
    """
    logger.debug(f"Resolving template: {template_name}")
    # Check user templates first
    user_root = _user_template_root(context)
    user_path = user_root / template_name
    logger.debug(f"Checking user template path: {user_path}")
    if user_path.is_file():
        logger.debug(f"Using user template: {user_path}")
        return user_path.read_text(encoding="utf-8")

    # Fallback to built-in
    builtin_root = _builtin_template_root()
    builtin_path = builtin_root.joinpath(template_name)
    logger.debug(f"Checking built-in template path: {builtin_path}")
    if builtin_path.is_file():
        logger.debug(f"Using built-in template: {builtin_path}")
        return builtin_path.read_text(encoding="utf-8")

    logger.debug(f"Template not found in user or built-in roots: {template_name}")
    raise TemplateNotFoundError(f"Template not found: {template_name}")


# ---------------------------------------------------------------------------
# Directory rendering (composite view)
# ---------------------------------------------------------------------------


def _collect_templates(context: Context, subdir: str) -> dict[str, Path]:
    """
    Return mapping of relative template path -> concrete template file.

    User templates override built-in templates if they share the same
    relative path.
    """
    templates: dict[str, Path] = {}
    logger.debug(f"Collecting templates under subdir: {subdir}")

    # 1️⃣ Built-in templates
    builtin_root = _builtin_template_root().joinpath(subdir)
    logger.debug(f"Scanning built-in templates in: {builtin_root}")
    if builtin_root.is_dir():
        with as_file(builtin_root) as builtin_path:
            for path in Path(builtin_path).rglob("*.tmpl"):
                rel = path.relative_to(builtin_path)
                logger.debug(f"Found built-in template: {path} (rel: {rel})")
                templates[str(rel)] = path

    # 2️⃣ User templates override
    user_root = _user_template_root(context) / subdir
    logger.debug(f"Scanning user templates in: {user_root}")
    if user_root.exists():
        for path in user_root.rglob("*.tmpl"):
            rel = path.relative_to(user_root)
            logger.debug(
                f"Found user template (overrides if duplicate): {path} (rel: {rel})"
            )
            templates[str(rel)] = path

    logger.debug(f"Collected {len(templates)} templates for subdir '{subdir}'")
    return templates


def list_templates(context: Context, subdir: str) -> Iterable[str]:
    """
    Return all templates under a given subdirectory (e.g. "practice").

    User templates override built-in templates if the relative path matches.
    """
    templates = _collect_templates(context, subdir)
    return templates.keys()
