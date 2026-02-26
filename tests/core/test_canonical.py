from datetime import date
from pathlib import Path

import pytest

from level.core.canonical import (
    build_slug,
    is_canonical_location,
    is_valid_suffixed_slug,
    rename_to_canonical,
    resolve_collision,
    slugify,
)


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


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Acme Corp", "acme-corp"),
        ("  Senior  Engineer  ", "senior-engineer"),
        ("Foo__Bar!!", "foo-bar"),
    ],
)
def test_slugify_normalizes_string(raw, expected):
    assert slugify(raw) == expected


def test_build_slug():
    d = date(2026, 2, 24)
    slug = build_slug(d, "Acme Corp")

    assert slug == "2026-02-24-acme-corp"


@pytest.mark.parametrize(
    "base,name,expected",
    [
        ("2026-02-24-foo", "2026-02-24-foo", True),
        ("2026-02-24-foo", "2026-02-24-foo-1", True),
        ("2026-02-24-foo", "2026-02-24-foo-12", True),
        ("2026-02-24-foo", "2026-02-24-foo-bar", False),
        ("2026-02-24-foo", "2026-02-24-bar", False),
    ],
)
def test_is_valid_suffixed_slug(base, name, expected):
    assert is_valid_suffixed_slug(base, name) is expected


def test_resolve_collision_no_existing(tmp_path):
    root = tmp_path
    canonical_rel = Path("2026-02-24-foo")

    result = resolve_collision(root, canonical_rel)

    assert result == root / canonical_rel


def test_resolve_collision_with_existing(tmp_path):
    root = tmp_path
    canonical_rel = Path("2026-02-24-foo")

    # Create base directory to force collision
    (root / canonical_rel).mkdir()

    result = resolve_collision(root, canonical_rel)

    assert result == root / Path("2026-02-24-foo-1")


def test_resolve_collision_multiple(tmp_path):
    root = tmp_path
    canonical_rel = Path("2026-02-24-foo")

    (root / canonical_rel).mkdir()
    (root / "2026-02-24-foo-1").mkdir()

    result = resolve_collision(root, canonical_rel)

    assert result == root / Path("2026-02-24-foo-2")


def test_resolve_collision_ignores_current_path(tmp_path):
    root = tmp_path
    canonical_rel = Path("2026-02-24-foo")

    current = root / canonical_rel
    current.mkdir()

    result = resolve_collision(root, canonical_rel, current_path=current)

    # Should not suffix when current_path matches base
    assert result == current
