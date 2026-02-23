from pathlib import Path

from level.core.canonical import is_canonical_location, rename_to_canonical


def test_is_canonical_location_true(tmp_path):
    root = tmp_path
    expected_rel = Path("2026-W08")
    actual = root / expected_rel
    actual.mkdir()

    assert is_canonical_location(root, actual, expected_rel) is True


def test_is_canonical_location_false(tmp_path):
    root = tmp_path
    actual = root / "wrong-name"
    actual.mkdir()

    expected_rel = Path("2026-W08")

    assert is_canonical_location(root, actual, expected_rel) is False


def test_rename_to_canonical_moves_directory(tmp_path):
    root = tmp_path
    actual = root / "wrong-name"
    actual.mkdir()

    expected_rel = Path("2026-W08")

    new_path = rename_to_canonical(root, actual, expected_rel)

    assert new_path == root / expected_rel
    assert new_path.exists()
    assert not (root / "wrong-name").exists()
