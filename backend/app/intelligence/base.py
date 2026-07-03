"""Base intelligence service.

Encapsulates the shared reasoning lifecycle (docs/08 §5): build the prompt,
invoke the model, parse JSON, validate against a schema, and return a proposal.
Services never persist data, mutate graph state, call repositories, or call one
another.

Retry handling here is *mechanical* only — transport failures and malformed /
schema-invalid responses are retried up to the prompt's ``retry_limit``
(docs/08 §18). Quality-based retries (the Evaluation loop) are a separate concern
owned by the graph.
"""

from __future__ import annotations

import json
from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel, ValidationError

from app.config.logging import get_logger
from app.intelligence.errors import InvalidLLMResponseError, LLMError
from app.intelligence.llm_client import LLMClient
from app.prompts import PromptBuilder

ProposalT = TypeVar("ProposalT", bound=BaseModel)

# Failures worth retrying: transport errors and unparseable/invalid responses.
_RETRYABLE = (LLMError, InvalidLLMResponseError, ValidationError, json.JSONDecodeError)

_INSUFFICIENT = "insufficient_context"


def to_prompt_value(value: Any) -> str:
    """Serialize a context value into a compact string for prompt injection."""
    if value is None:
        return "none"
    if isinstance(value, str):
        return value
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    if isinstance(value, (list, tuple)):
        items = [v.model_dump(mode="json") if isinstance(v, BaseModel) else v for v in value]
        return json.dumps(items, default=str)
    if isinstance(value, dict):
        return json.dumps(value, default=str)
    return str(value)


class IntelligenceService:
    """Shared machinery for prompt-driven reasoning services."""

    prompt_name: ClassVar[str]

    def __init__(self, client: LLMClient, builder: PromptBuilder | None = None) -> None:
        self.client = client
        self.builder = builder or PromptBuilder()
        self._logger = get_logger(f"app.intelligence.{self.prompt_name}")

    async def _reason_json(
        self, variables: dict[str, Any], schema: type[ProposalT]
    ) -> ProposalT | None:
        """Render, call the model, and validate the JSON response.

        Returns ``None`` when the model reports insufficient context. Raises
        :class:`InvalidLLMResponseError` after exhausting retries.
        """
        rendered = self.builder.build(self.prompt_name, variables)
        attempts = max(1, rendered.retry_limit)
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                raw = await self.client.complete(
                    rendered.text,
                    model=rendered.model,
                    temperature=rendered.temperature,
                    max_tokens=rendered.max_tokens,
                    timeout=float(rendered.timeout_seconds),
                    json_mode=True,
                )
                data = self._extract_json(raw)
                if isinstance(data, dict) and data.get("status") == _INSUFFICIENT:
                    self._logger.info("insufficient_context", extra={"prompt": self.prompt_name})
                    return None
                return schema.model_validate(data)
            except _RETRYABLE as exc:
                last_error = exc
                self._logger.warning(
                    "intelligence_retry",
                    extra={"prompt": self.prompt_name, "attempt": attempt, "error": str(exc)},
                )

        raise InvalidLLMResponseError(
            f"{self.prompt_name} failed after {attempts} attempt(s)"
        ) from last_error

    async def _reason_text(self, variables: dict[str, Any]) -> str:
        """Render and call the model, returning raw text (e.g. Markdown summary)."""
        rendered = self.builder.build(self.prompt_name, variables)
        attempts = max(1, rendered.retry_limit)
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                raw = await self.client.complete(
                    rendered.text,
                    model=rendered.model,
                    temperature=rendered.temperature,
                    max_tokens=rendered.max_tokens,
                    timeout=float(rendered.timeout_seconds),
                    json_mode=False,
                )
                if not raw.strip():
                    raise InvalidLLMResponseError("empty response")
                return raw.strip()
            except (LLMError, InvalidLLMResponseError) as exc:
                last_error = exc
                self._logger.warning(
                    "intelligence_retry",
                    extra={"prompt": self.prompt_name, "attempt": attempt, "error": str(exc)},
                )

        raise InvalidLLMResponseError(
            f"{self.prompt_name} failed after {attempts} attempt(s)"
        ) from last_error

    @staticmethod
    def _extract_json(raw: str) -> Any:
        """Parse a JSON object from a model response, tolerating code fences/prose."""
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lstrip().lower().startswith("json"):
                text = text.lstrip()[4:]
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise InvalidLLMResponseError("no JSON object found in response")
        return json.loads(text[start : end + 1])
