"""Prompt system exceptions."""

from __future__ import annotations


class PromptError(Exception):
    """Base class for prompt-system failures."""


class PromptNotFoundError(PromptError):
    """Raised when a requested prompt name/version has no definition or template."""


class MissingPromptVariableError(PromptError):
    """Raised when a template requires variables that were not supplied."""
