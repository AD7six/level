from datetime import date
from pathlib import Path

import pytest

from level.core.canonical import (
    build_slug,
    is_canonical_location,
    rename_to_canonical,
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
