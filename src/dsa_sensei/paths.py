"""Where the local study log lives."""

from __future__ import annotations

import os
from pathlib import Path


def default_db_path() -> Path:
    """Resolve the SQLite file.

    ``DSA_SENSEI_DB`` wins. Otherwise the file is
    ``$XDG_DATA_HOME/dsa-sensei/sensei.db``, or
    ``~/.local/share/dsa-sensei/sensei.db``.
    """
    override = os.environ.get("DSA_SENSEI_DB", "").strip()
    if override:
        return Path(override).expanduser()
    xdg = os.environ.get("XDG_DATA_HOME", "").strip()
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "share"
    return base / "dsa-sensei" / "sensei.db"
