import re
from datetime import date
from pathlib import Path


def is_canonical_location(root: Path, actual_dir: Path, expected_rel: Path) -> bool:
    """
    Return True if actual_dir matches expected_rel under root.
    """
    try:
        return actual_dir.relative_to(root) == expected_rel
    except ValueError:
        return False


def rename_to_canonical(root: Path, actual_dir: Path, expected_rel: Path) -> Path:
    """
    Rename actual_dir to expected_rel under root.
    Returns the new Path.
    """
    target = root / expected_rel

    if actual_dir == target:
        return actual_dir

    target.parent.mkdir(parents=True, exist_ok=True)
    actual_dir.rename(target)
    return target


def slugify(name: str) -> str:
    """
    Convert a name into a filesystem-safe slug component.
    Lowercase, alphanumeric and hyphen only.
    """
    value = name.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def build_slug(d: date, name: str) -> str:
    """
    Build a canonical slug using the opinionated format:
    YYYY-MM-DD-{name}
    """
    return f"{d.strftime('%Y-%m-%d')}-{slugify(name)}"
