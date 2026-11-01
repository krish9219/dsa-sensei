"""Optional hints for problems that are not in the catalog.

Nothing is sent anywhere unless both ``DSA_SENSEI_LLM_BASE_URL`` and
``DSA_SENSEI_LLM_MODEL`` are set. ``DSA_SENSEI_LLM_API_KEY`` is added as a
bearer token when it is present. The endpoint must speak the OpenAI chat
completions API.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from dsa_sensei.errors import LLMError, LLMNotConfigured

_SYSTEM = (
    "You are a Socratic tutor for data-structures and algorithms interviews. "
    "The student will describe a problem. Reply with a JSON object and nothing else, "
    "with exactly these string fields: "
    "nudge (a short question that points at the bottleneck without naming the whole algorithm), "
    "approach (the pattern and why it fits, still without a finished implementation), "
    "pseudocode (at most 12 lines of high-level pseudocode, no tests, no language boilerplate). "
    "Never include a finished solution, a class named Solution, or the concrete answer "
    "for the student's example. Do not wrap the JSON in markdown."
)
_FENCE = re.compile(r"```.*?```", re.DOTALL)
_DEF = re.compile(r"^\s*def\s+\w+\s*\(", re.MULTILINE)
_CLASS = re.compile(r"^\s*class\s+\w+", re.MULTILINE)
_WITHHELD = (
    "That response looked like a full implementation, so it was withheld. "
    "Try again, or study a built-in problem."
)


@dataclass(frozen=True, slots=True)
class LLMSettings:
    base_url: str
    model: str
    api_key: str | None
    timeout: float


def load_settings() -> LLMSettings | None:
    base = os.environ.get("DSA_SENSEI_LLM_BASE_URL", "").strip()
    model = os.environ.get("DSA_SENSEI_LLM_MODEL", "").strip()
    if not base and not model:
        return None
    if not base or not model:
        raise LLMError("Set both DSA_SENSEI_LLM_BASE_URL and DSA_SENSEI_LLM_MODEL, or leave both unset.")
    if not base.startswith(("http://", "https://")):
        raise LLMError("DSA_SENSEI_LLM_BASE_URL must start with http:// or https://.")
    raw_timeout = os.environ.get("DSA_SENSEI_LLM_TIMEOUT", "30").strip() or "30"
    try:
        timeout = float(raw_timeout)
    except ValueError as exc:
        raise LLMError("DSA_SENSEI_LLM_TIMEOUT must be a number of seconds.") from exc
    if timeout <= 0:
        raise LLMError("DSA_SENSEI_LLM_TIMEOUT must be positive.")
    api_key = os.environ.get("DSA_SENSEI_LLM_API_KEY", "").strip() or None
    return LLMSettings(base_url=base, model=model, api_key=api_key, timeout=timeout)


def require_settings() -> LLMSettings:
    settings = load_settings()
    if settings is None:
        raise LLMNotConfigured()
    return settings


def generate_ladder(prompt: str, settings: LLMSettings | None = None) -> tuple[str, str, str]:
    active = settings if settings is not None else require_settings()
    payload = {
        "model": active.model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt.strip()},
        ],
    }
    content = _chat(active, payload)
    data = _extract_json(content)
    return (
        sanitize_hint(str(data["nudge"]), allow_pseudocode=False),
        sanitize_hint(str(data["approach"]), allow_pseudocode=False),
        sanitize_hint(str(data["pseudocode"]), allow_pseudocode=True),
    )


def sanitize_hint(text: str, *, allow_pseudocode: bool) -> str:
    cleaned = text.strip()
    if not allow_pseudocode and "```" in cleaned:
        cleaned = _FENCE.sub("a sketch was removed from this rung", cleaned).strip()
    too_much_code = bool(_CLASS.search(cleaned)) or (
        bool(_DEF.search(cleaned)) and (not allow_pseudocode or cleaned.count("\n") > 18)
    )
    if too_much_code or not cleaned:
        return _WITHHELD
    return cleaned


def _chat(settings: LLMSettings, payload: dict[str, object]) -> str:
    url = settings.base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    if settings.api_key:
        request.add_header("Authorization", f"Bearer {settings.api_key}")
    try:
        with urllib.request.urlopen(request, timeout=settings.timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise LLMError(f"The hint model returned HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"Could not reach the hint model: {exc.reason}") from exc
    except TimeoutError as exc:
        raise LLMError("The hint model timed out.") from exc
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise LLMError("The hint model returned a response that was not JSON.") from exc
    if not isinstance(parsed, dict):
        raise LLMError("The hint model returned a response that was not a JSON object.")
    try:
        content = parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("The hint model response did not include a message.") from exc
    if not isinstance(content, str) or not content.strip():
        raise LLMError("The hint model returned an empty message.")
    return content


def _extract_json(content: str) -> dict[str, str]:
    candidate = content.strip()
    if candidate.startswith("```"):
        candidate = _FENCE.sub(lambda match: match.group(0).strip("`"), candidate, count=1).strip()
        # Fall through to brace extraction if the fence strip left prose.
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end <= start:
        raise LLMError("The hint model did not return a JSON object.")
    try:
        parsed = json.loads(candidate[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError("The hint model returned JSON that could not be parsed.") from exc
    if not isinstance(parsed, dict):
        raise LLMError("The hint model returned JSON that was not an object.")
    ladder: dict[str, str] = {}
    for key in ("nudge", "approach", "pseudocode"):
        value = parsed.get(key)
        if not isinstance(value, str) or not value.strip():
            raise LLMError(f"The hint model response was missing {key}.")
        ladder[key] = value.strip()
    return ladder
