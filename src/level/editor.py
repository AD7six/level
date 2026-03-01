from __future__ import annotations

import subprocess
from pathlib import Path


def open_in_editor(path: Path, *, auto_open: bool, editor: str | None) -> bool:
    if not auto_open or not editor:
        return False

    result = subprocess.run([editor, str(path)], check=False)
    return result.returncode == 0
