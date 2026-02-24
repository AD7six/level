from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date
from pathlib import Path
from typing import Any


def write_meta_toml(path: Path, data: Mapping[str, Any] | object) -> None:
    """
    Write a TOML meta file in a consistent, minimal format.

    Accepts either:
    - a Mapping[str, Any]
    - a dataclass instance
    """

    # Convert dataclass instances (but not dataclass types)
    if is_dataclass(data) and not isinstance(data, type):
        data = asdict(data)

    if not isinstance(data, Mapping):
        raise TypeError("write_meta_toml expects a mapping or dataclass")

    lines: list[str] = []

    for key, value in data.items():
        if value is None:
            continue

        if isinstance(value, str):
            lines.append(f"{key} = {json.dumps(value)}")
        elif isinstance(value, date):
            lines.append(f'{key} = "{value.isoformat()}"')
        elif isinstance(value, list):
            items = ", ".join(json.dumps(v) for v in value)
            lines.append(f"{key} = [{items}]")
        else:
            lines.append(f"{key} = {value}")

    path.write_text("\n".join(lines) + "\n")
