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


def is_valid_suffixed_slug(base: str, name: str) -> bool:
    """
    Return True if `name` is either exactly `base` or
    `base-<number>` where <number> is a positive integer.
    """
    if name == base:
        return True

    if not name.startswith(base + "-"):
        return False

    suffix = name[len(base) + 1 :]
    return suffix.isdigit()


def resolve_collision(
    root: Path,
    canonical_rel: Path,
    current_path: Path | None = None,
) -> Path:
    """
    Resolve a canonical relative path under root, adding a numeric
    suffix (-1, -2, ...) if necessary to avoid collisions.

    If `current_path` is provided and already matches the resolved
    path, it will be ignored for collision purposes.
    """
    target = root / canonical_rel

    if not target.exists() or (current_path and target == current_path):
        return target

    base_name = canonical_rel.name
    parent = canonical_rel.parent

    counter = 1
    while True:
        candidate_name = f"{base_name}-{counter}"
        candidate_rel = parent / candidate_name
        candidate = root / candidate_rel

        if not candidate.exists() or (current_path and candidate == current_path):
            return candidate

        counter += 1
