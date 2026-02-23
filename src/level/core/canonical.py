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
