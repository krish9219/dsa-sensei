from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from dsa_sensei.errors import LLMError, LLMNotConfigured, SenseiError
from dsa_sensei.llm import generate_ladder, load_settings, sanitize_hint
from dsa_sensei.service import get_hint


class _Response:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self, n: int = -1) -> bytes:
        del n
        return self._payload

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def _payload(content: str) -> bytes:
    body = {"choices": [{"message": {"content": content}}]}
    return json.dumps(body).encode()


def test_custom_hints_are_off_by_default(tmp_path: Path) -> None:
    assert load_settings() is None
    with pytest.raises(LLMNotConfigured):
        get_hint(custom_prompt="Count the islands in a grid of land and water.", db=tmp_path / "s.db")


def test_settings_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DSA_SENSEI_LLM_MODEL", "local")
    with pytest.raises(LLMError, match="both"):
        load_settings()
    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "ftp://example.test/v1")
    with pytest.raises(LLMError, match="http"):
        load_settings()
    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("DSA_SENSEI_LLM_TIMEOUT", "0")
    with pytest.raises(LLMError, match="positive"):
        load_settings()


def test_generate_and_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = {"n": 0}

    def fake_urlopen(request: object, timeout: float = 0) -> _Response:
        calls["n"] += 1
        assert timeout == 5
        content = json.dumps(
            {
                "nudge": "What are you recomputing?",
                "approach": "Store answers you have already earned.",
                "pseudocode": "if the state was seen:\n    reuse it\nelse:\n    compute and store it",
            }
        )
        return _Response(_payload(content))

    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "http://127.0.0.1:9/v1")
    monkeypatch.setenv("DSA_SENSEI_LLM_MODEL", "test-model")
    monkeypatch.setenv("DSA_SENSEI_LLM_API_KEY", "secret")
    monkeypatch.setenv("DSA_SENSEI_LLM_TIMEOUT", "5")
    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", fake_urlopen)
    prompt = "How many ways can I climb n stairs taking 1 or 2 at a time?"
    first = get_hint(custom_prompt=prompt, db=tmp_path / "s.db")
    second = get_hint(custom_prompt=prompt, level=2, db=tmp_path / "s.db")
    assert first.source == "llm"
    assert first.level == 1
    assert "recomputing" in first.text
    assert second.level_name == "approach"
    assert calls["n"] == 1
    with pytest.raises(SenseiError, match="not both"):
        get_hint("stair-ways", custom_prompt=prompt, db=tmp_path / "s.db")


def test_model_failures_and_sanitizer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("DSA_SENSEI_LLM_MODEL", "test-model")

    def http_error(request: object, timeout: float = 0) -> _Response:
        raise HTTPError("http://example.test", 401, "nope", hdrs=None, fp=None)  # type: ignore[arg-type]

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", http_error)
    with pytest.raises(LLMError, match="HTTP 401"):
        generate_ladder("Explain an original scheduling problem with constraints.")

    def bad_json(request: object, timeout: float = 0) -> _Response:
        return _Response(b"not-json")

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", bad_json)
    with pytest.raises(LLMError, match="not JSON"):
        generate_ladder("Explain an original scheduling problem with constraints.")

    def missing_field(request: object, timeout: float = 0) -> _Response:
        return _Response(_payload('{"nudge": "think"}'))

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", missing_field)
    with pytest.raises(LLMError, match="missing"):
        generate_ladder("Explain an original scheduling problem with constraints.")

    def offline(request: object, timeout: float = 0) -> _Response:
        raise URLError("connection refused")

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", offline)
    with pytest.raises(LLMError, match="reach"):
        generate_ladder("Explain an original scheduling problem with constraints.")

    withheld = sanitize_hint(
        "class Solution:\n    def solve(self):\n        return 1\n",
        allow_pseudocode=True,
    )
    assert "withheld" in withheld
    cleaned = sanitize_hint(
        "Look at the ends. ```python\nprint(1)\n``` Then move inward.",
        allow_pseudocode=False,
    )
    assert "```" not in cleaned
    assert "ends" in cleaned


def test_more_model_payloads(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("DSA_SENSEI_LLM_MODEL", "test-model")

    def timeout(request: object, timeout: float = 0) -> _Response:
        raise TimeoutError("slow")

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", timeout)
    with pytest.raises(LLMError, match="timed out"):
        generate_ladder("Describe a scheduling problem with several constraints.")

    def array(request: object, timeout: float = 0) -> _Response:
        return _Response(b"[1, 2, 3]")

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", array)
    with pytest.raises(LLMError, match="JSON object"):
        generate_ladder("Describe a scheduling problem with several constraints.")

    def empty(request: object, timeout: float = 0) -> _Response:
        return _Response(_payload("   "))

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", empty)
    with pytest.raises(LLMError, match="empty"):
        generate_ladder("Describe a scheduling problem with several constraints.")

    def fenced(request: object, timeout: float = 0) -> _Response:
        content = (
            "```json\n"
            '{"nudge": "Look at the boundary.", '
            '"approach": "Shrink the side that limits you.", '
            '"pseudocode": "move the shorter side inward"}\n'
            "```"
        )
        return _Response(_payload(content))

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", fenced)
    ladder = generate_ladder("How should two pointers move on a list of wall heights?")
    assert ladder[0].startswith("Look")
    with pytest.raises(SenseiError, match="4000"):
        get_hint(custom_prompt="x" * 4001, db=tmp_path / "s.db")


def test_fenced_solution_is_withheld_and_not_cached(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import http.client

    calls = {"n": 0}

    def fake_urlopen(request: object, timeout: float = 0) -> _Response:
        calls["n"] += 1
        content = json.dumps(
            {
                "nudge": "```python\ndef solve(nums):\n    return nums[0]\n```",
                "approach": "Use one pass.",
                "pseudocode": "scan once",
            }
        )
        return _Response(_payload(content))

    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "http://127.0.0.1:9/v1")
    monkeypatch.setenv("DSA_SENSEI_LLM_MODEL", "test-model")
    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", fake_urlopen)
    prompt = "Find a pair of values that add up to a target in a list."
    first = get_hint(custom_prompt=prompt, db=tmp_path / "s.db")
    second = get_hint(custom_prompt=prompt, db=tmp_path / "s.db")
    assert "withheld" in first.text
    assert "def solve" not in first.text
    assert calls["n"] == 2
    assert second.text == first.text

    long_pseudo = "\n".join(f"step {i}" for i in range(13))
    assert "withheld" in sanitize_hint(long_pseudo, allow_pseudocode=True)

    def dropped(request: object, timeout: float = 0) -> _Response:
        raise http.client.RemoteDisconnected("closed")

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", dropped)
    with pytest.raises(LLMError, match="connection"):
        generate_ladder("Describe a scheduling problem with several constraints and a limit.")

    class Huge:
        def read(self, n: int = -1) -> bytes:
            return b"x" * (n if n > 0 else 10)

        def __enter__(self) -> Huge:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", lambda request, timeout=0: Huge())
    with pytest.raises(LLMError, match="too large"):
        generate_ladder("Describe a scheduling problem with several constraints and a limit.")

    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "http://example.test/v1")
    monkeypatch.setenv("DSA_SENSEI_LLM_API_KEY", "secret")
    monkeypatch.setattr("dsa_sensei.llm.urllib.request.urlopen", fake_urlopen)
    with pytest.warns(UserWarning, match="plain HTTP"):
        generate_ladder("Describe a scheduling problem with several constraints and a limit.")


def test_timeout_setting(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DSA_SENSEI_LLM_BASE_URL", "http://127.0.0.1:9/v1")
    monkeypatch.setenv("DSA_SENSEI_LLM_MODEL", "test-model")
    monkeypatch.setenv("DSA_SENSEI_LLM_TIMEOUT", "fast")
    with pytest.raises(LLMError, match="number"):
        load_settings()
