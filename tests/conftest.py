from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _isolated_environment(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep tests off the real study log and the network."""
    from pathlib import Path

    root = tmp_path if isinstance(tmp_path, Path) else Path(str(tmp_path))
    monkeypatch.setenv("DSA_SENSEI_DB", str(root / "sensei.db"))
    monkeypatch.setenv("DSA_SENSEI_TODAY", "2026-04-01")
    for name in (
        "DSA_SENSEI_LLM_BASE_URL",
        "DSA_SENSEI_LLM_MODEL",
        "DSA_SENSEI_LLM_API_KEY",
        "DSA_SENSEI_LLM_TIMEOUT",
    ):
        monkeypatch.delenv(name, raising=False)
    yield
