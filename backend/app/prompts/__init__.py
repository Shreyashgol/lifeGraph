"""Prompt system.

Prompts are versioned software artifacts, never strings embedded in code. This
package holds prompt ``definitions`` (metadata), ``templates`` (markdown), and
``tests`` (evaluation cases), plus the registry and builder.
"""

from app.prompts.builder import PromptBuilder, RenderedPrompt, extract_variables
from app.prompts.definition import Prompt, PromptDefinition
from app.prompts.errors import (
    MissingPromptVariableError,
    PromptError,
    PromptNotFoundError,
)
from app.prompts.registry import PromptRegistry, get_prompt_registry

__all__ = [
    "MissingPromptVariableError",
    "Prompt",
    "PromptBuilder",
    "PromptDefinition",
    "PromptError",
    "PromptNotFoundError",
    "PromptRegistry",
    "RenderedPrompt",
    "extract_variables",
    "get_prompt_registry",
]
