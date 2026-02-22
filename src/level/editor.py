from __future__ import annotations

import subprocess
from pathlib import Path


def open_in_editor(path: Path, *, auto_open: bool, editor: str | None) -> None:
    if not auto_open:
        return

    if not editor:
        return

    subprocess.run([editor, str(path)], check=False)
