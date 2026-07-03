"""Intelligence layer exceptions.

Transport failures (:class:`LLMError` and subclasses) and malformed responses
(:class:`InvalidLLMResponseError`) are retryable; everything else is not.
"""

from __future__ import annotations


class IntelligenceError(Exception):
    """Base class for intelligence-layer failures."""


class LLMError(IntelligenceError):
    """Base class for recoverable model-provider transport failures."""


class LLMTimeoutError(LLMError):
    """The model request timed out."""


class LLMRateLimitError(LLMError):
    """The provider rate-limited the request."""


class LLMResponseError(LLMError):
    """The provider returned an error or an empty response."""


class InvalidLLMResponseError(IntelligenceError):
    """The response could not be parsed/validated after all retries."""
