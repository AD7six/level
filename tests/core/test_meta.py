from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from level.core.meta import write_meta_toml


def test_write_meta_from_mapping(tmp_path: Path):
    path = tmp_path / "meta.toml"

    data = {
        "name": "Test",
        "count": 3,
        "when": date(2026, 1, 1),
        "tags": ["a", "b"],
        "optional": None,
    }

    write_meta_toml(path, data)

    content = path.read_text()

    assert 'name = "Test"' in content
    assert "count = 3" in content
    assert 'when = "2026-01-01"' in content
    assert 'tags = ["a", "b"]' in content
    assert "optional" not in content


@dataclass
class ExampleMeta:
    name: str
    value: int


def test_write_meta_from_dataclass(tmp_path: Path):
    path = tmp_path / "meta.toml"

    obj = ExampleMeta(name="Example", value=42)

    write_meta_toml(path, obj)

    content = path.read_text()

    assert 'name = "Example"' in content
    assert "value = 42" in content


def test_write_meta_rejects_invalid_type(tmp_path: Path):
    path = tmp_path / "meta.toml"

    with pytest.raises(TypeError):
        write_meta_toml(path, 123)


def test_write_meta_orders_keys_deterministically(tmp_path: Path):
    path = tmp_path / "meta.toml"

    data = {
        "b": 2,
        "a": 1,
        "c": 3,
    }

    write_meta_toml(path, data)

    lines = path.read_text().strip().split("\n")

    assert lines == [
        "a = 1",
        "b = 2",
        "c = 3",
    ]
