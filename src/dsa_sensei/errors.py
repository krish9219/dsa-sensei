"""Errors a person (or an agent) can act on."""

from __future__ import annotations


class SenseiError(Exception):
    """Expected failure whose message is safe to show."""


class ProblemNotFound(SenseiError):
    """No built-in problem matches this id or alias."""

    def __init__(
        self,
        problem_id: str,
        suggestions: list[str],
        *,
        suggest_custom: bool = False,
    ) -> None:
        self.problem_id = problem_id
        self.suggestions = list(suggestions)
        if suggestions:
            listed = ", ".join(suggestions)
            message = f"Unknown problem '{problem_id}'. Did you mean {listed}?"
        else:
            message = f"Unknown problem '{problem_id}'. Run `dsa-sensei list` to see the catalog."
            if suggest_custom:
                message += " Or pass a custom prompt with an OpenAI-compatible endpoint configured."
        super().__init__(message)


class InvalidHintLevel(SenseiError):
    """Hint rung outside the ladder."""

    def __init__(self, level: int) -> None:
        self.level = level
        super().__init__(
            f"Hint level {level} is outside the ladder. Use 1 (nudge), 2 (approach), or 3 (pseudocode)."
        )


class InvalidQuality(SenseiError):
    """Recall grade was not on the 0-5 scale."""

    def __init__(self, value: object) -> None:
        self.value = value
        super().__init__(
            f"Quality {value!r} is not a recall grade. "
            "Use 0-5, or one of: blackout, again, fuzzy, hard, good, easy, perfect."
        )


class CodeRejected(SenseiError):
    """Submitted source could not be analyzed."""


class LLMNotConfigured(SenseiError):
    """A custom problem was requested and no hint model is configured."""

    def __init__(self) -> None:
        super().__init__(
            "Custom hints stay off until you set DSA_SENSEI_LLM_BASE_URL and "
            "DSA_SENSEI_LLM_MODEL. DSA_SENSEI_LLM_API_KEY is optional for local servers. "
            "Built-in problems work fully offline."
        )


class LLMError(SenseiError):
    """The optional hint model failed or returned something unusable."""
