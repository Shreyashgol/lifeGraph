"""LLM client abstraction.

The intelligence layer depends on this interface, never on a concrete provider
SDK (docs/08 §16). Swapping Groq for another provider means implementing one new
client — nothing in the services or prompts changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Provider-agnostic chat completion interface."""

    @abstractmethod
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
        """Return the model's completion text for ``prompt``.

        ``json_mode`` requests a JSON-object response when the provider supports
        it. Implementations raise :class:`~app.intelligence.errors.LLMError`
        subclasses for recoverable transport failures.
        """
