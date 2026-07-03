"""Prompt definitions.

Every prompt is two artifacts (docs/09 §15): a **template** (the reasoning
instructions) and a **definition** (execution metadata). Definitions are stored
as YAML in ``prompts/definitions`` and loaded into :class:`PromptDefinition`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PromptDefinition(BaseModel):
    """Execution metadata for one prompt (docs/09 §15).

    ``output_format`` records the JSON-except-Summary rule (docs/09 §11/§16) so
    downstream services know how to parse the model response.
    """

    # protected_namespaces=() allows the ``model`` field name without warnings.
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    name: str
    version: str
    owner: str = Field(description="Intelligence service that owns the prompt.")
    purpose: str
    input_schema: str
    output_schema: str
    model: str
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, gt=0)
    timeout_seconds: int = Field(default=30, gt=0)
    retry_limit: int = Field(default=3, ge=0)
    output_format: Literal["json", "markdown"] = "json"


class Prompt(BaseModel):
    """A loaded prompt: its definition plus its raw template text."""

    model_config = ConfigDict(extra="forbid")

    definition: PromptDefinition
    template: str
