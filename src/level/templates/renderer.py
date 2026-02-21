from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from level.config import Context

from .loader import _collect_templates, load_template

logger = logging.getLogger("level.templates")


class TemplateRenderError(ValueError):
    """Raised when template rendering fails due to missing variables."""


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def render_template_to_string(
    context: Context,
    template_name: str,
    variables: dict[str, Any],
    strict: bool = False,
) -> str:
    """
    Render a named template using the provided context.

    Uses Python's built-in str.format().

    Raises:
        TemplateRenderError if required template variables are missing.
    """
    logger.debug(f"Rendering template to string: {template_name} (strict={strict})")
    template = load_template(context, template_name)

    logger.debug(f"Loaded template: {template_name}")

    if strict:
        try:
            result = template.format(**variables)
            logger.debug(f"Strict render successful for template: {template_name}")
            return result
        except KeyError as exc:
            missing = exc.args[0]
            raise TemplateRenderError(f"Missing template variable: {missing}") from exc

    # Non-strict mode (default): leave unknown placeholders untouched
    result = template.format_map(_SafeDict(variables))
    logger.debug(f"Lax render completed for template: {template_name}")
    return result


def render_template_to_path(
    context: Context,
    template_name: str,
    variables: dict[str, Any],
    output_path: Path,
    overwrite: bool = False,
    strict: bool = False,
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
    logger.debug(
        f"Rendering template to path: {template_name} -> {output_path} "
        f"(strict={strict}, overwrite={overwrite})"
    )
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {output_path}")

    rendered = render_template_to_string(
        context,
        template_name,
        variables,
        strict=strict,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    logger.debug(f"Wrote rendered template to: {output_path}")

    return output_path


def render_template_directory(
    context: Context,
    template_subdir: str,
    variables: dict[str, Any],
    output_dir: Path,
    strict: bool = False,
) -> None:
    """
    Render all templates in a directory (builtin + user override).

    - Recursively walks subdir
    - User templates override built-in
    - Filenames are preserved (no filename templating)
    - Respects strict/non-strict rendering mode
    """
    logger.debug(
        f"Rendering template directory: {template_subdir} -> {output_dir} "
        f"(strict={strict})"
    )
    templates = _collect_templates(context, template_subdir)

    logger.debug(f"Found {len(templates)} templates in subdir '{template_subdir}'")

    for rel_name, template_path in templates.items():
        # Remove .tmpl suffix
        rel_without_suffix = rel_name.removesuffix(".tmpl")
        target_path = output_dir / rel_without_suffix

        logger.debug(f"Rendering template file: {rel_name} -> {target_path}")

        target_path.parent.mkdir(parents=True, exist_ok=True)

        template_text = template_path.read_text(encoding="utf-8")

        if strict:
            try:
                rendered = template_text.format(**variables)
            except KeyError as exc:
                missing = exc.args[0]
                raise TemplateRenderError(
                    f"Missing template variable: {missing}"
                ) from exc
        else:
            rendered = template_text.format_map(_SafeDict(variables))

        target_path.write_text(rendered, encoding="utf-8")
        logger.debug(f"Wrote rendered file: {target_path}")
