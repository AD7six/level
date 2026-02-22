from __future__ import annotations

import subprocess
from pathlib import Path

from level.config import Context


def open_in_editor(path: Path, context: Context) -> None:
    if not context.config.auto_open:
        return

    editor = context.config.editor
    if not editor:
        return

    subprocess.run([editor, str(path)], check=False)
