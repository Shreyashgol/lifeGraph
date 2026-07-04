"""Prompt builder.

Injects variables into a template and produces a :class:`RenderedPrompt` that
carries both the final text and the execution metadata (model, sampling, prompt
version) the intelligence layer needs. Responsibilities (docs/09 §8): load the
template, inject variables, validate required variables, render, record version.

Template variables use ``{{ name }}`` syntax. Required variables are derived
from the template itself, so the template is the single source of truth.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.config.logging import get_logger
from app.prompts.errors import MissingPromptVariableError
from app.prompts.registry import PromptRegistry, get_prompt_registry

_VARIABLE_PATTERN = re.compile(r"{{\s*(\w+)\s*}}")
_logger = get_logger("app.prompts.builder")


def extract_variables(template: str) -> set[str]:
    """Return the set of ``{{ variable }}`` names referenced by a template."""
    return set(_VARIABLE_PATTERN.findall(template))


class RenderedPrompt(BaseModel):
    """A fully rendered prompt plus the metadata needed to execute it."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    name: str
    version: str
    model: str
    temperature: float
    max_tokens: int
    timeout_seconds: int
    retry_limit: int
    output_format: str
    text: str
    variables: list[str]


class PromptBuilder:
    """Renders versioned prompts with validated variable injection."""

    def __init__(self, registry: PromptRegistry | None = None) -> None:
        self.registry = registry or get_prompt_registry()

    def build(self, name: str, variables: dict[str, Any], version: str = "v1") -> RenderedPrompt:
        """Render ``name``/``version`` with ``variables``.

        Raises :class:`MissingPromptVariableError` if the template requires a
        variable that was not supplied. Extra variables are ignored.
        """
        prompt = self.registry.get(name, version)
        required = extract_variables(prompt.template)

        missing = required - set(variables)
        if missing:
            raise MissingPromptVariableError(
                f"Prompt {name}/{version} missing variables: {sorted(missing)}"
            )

        text = _VARIABLE_PATTERN.sub(lambda match: str(variables[match.group(1)]), prompt.template)

        definition = prompt.definition
        _logger.info(
            "prompt_rendered",
            extra={"prompt_name": name, "prompt_version": version, "model": definition.model},
        )
        return RenderedPrompt(
            name=definition.name,
            version=definition.version,
            model=definition.model,
            temperature=definition.temperature,
            max_tokens=definition.max_tokens,
            timeout_seconds=definition.timeout_seconds,
            retry_limit=definition.retry_limit,
            output_format=definition.output_format,
            text=text,
            variables=sorted(required),
        )
