"""Groq implementation of :class:`LLMClient`.

This is the only module that knows about the Groq SDK. The SDK is imported
lazily so the rest of the intelligence layer imports cleanly without ``groq``
installed (e.g. in tests that use a fake client). Provider errors are mapped to
the intelligence layer's retryable exceptions by class name, which keeps the
mapping robust across SDK versions.
"""

from __future__ import annotations

from app.config import get_settings
from app.intelligence.errors import (
    IntelligenceError,
    LLMError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)
from app.intelligence.llm_client import LLMClient


class GroqClient(LLMClient):
    """Calls Groq's OpenAI-compatible chat completions API."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or get_settings().groq_api_key
        if not key:
            raise IntelligenceError("GROQ_API_KEY is not configured")
        # Lazy import keeps the module importable without the SDK installed.
        from groq import AsyncGroq

        self._client = AsyncGroq(api_key=key)

    async def complete(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
        json_mode: bool = False,
    ) -> str:
        kwargs: dict[str, object] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:  # mapped to retryable errors below
            raise self._map_error(exc) from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMResponseError("empty response content")
        return content

    @staticmethod
    def _map_error(exc: Exception) -> LLMError:
        """Map a provider exception to a retryable intelligence error."""
        name = type(exc).__name__.lower()
        if "timeout" in name:
            return LLMTimeoutError(str(exc))
        if "ratelimit" in name or "rate_limit" in name:
            return LLMRateLimitError(str(exc))
        return LLMResponseError(str(exc))
