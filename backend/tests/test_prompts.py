"""Prompt system tests (Phase 4 acceptance: rendering, validation, versioning)."""

from __future__ import annotations

import pytest

from app.prompts import (
    MissingPromptVariableError,
    PromptBuilder,
    PromptNotFoundError,
    PromptRegistry,
    extract_variables,
)

ALL_PROMPTS = [
    "activity",
    "memory",
    "behaviour",
    "insight",
    "recommendation",
    "summary",
    "reflection",
    "evaluation",
]


@pytest.fixture
def registry() -> PromptRegistry:
    return PromptRegistry()


@pytest.fixture
def builder(registry: PromptRegistry) -> PromptBuilder:
    return PromptBuilder(registry)


# --------------------------------------------------------------------------- #
# Registry / definitions
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", ALL_PROMPTS)
def test_every_prompt_loads(registry: PromptRegistry, name: str) -> None:
    prompt = registry.get(name)
    assert prompt.definition.name == name
    assert prompt.definition.version == "v1"
    assert prompt.template.strip()


def test_list_definitions_returns_all(registry: PromptRegistry) -> None:
    names = {d.name for d in registry.list_definitions()}
    assert names == set(ALL_PROMPTS)


def test_unknown_prompt_raises(registry: PromptRegistry) -> None:
    with pytest.raises(PromptNotFoundError):
        registry.get("does_not_exist")


def test_unknown_version_raises(registry: PromptRegistry) -> None:
    with pytest.raises(PromptNotFoundError):
        registry.get("activity", "v99")


def test_summary_is_markdown_others_json(registry: PromptRegistry) -> None:
    assert registry.get("summary").definition.output_format == "markdown"
    assert registry.get("activity").definition.output_format == "json"


# --------------------------------------------------------------------------- #
# Builder / rendering
# --------------------------------------------------------------------------- #
def test_extract_variables() -> None:
    assert extract_variables("a {{ x }} b {{y}} {{ x }}") == {"x", "y"}


@pytest.mark.parametrize("name", ALL_PROMPTS)
def test_every_prompt_renders_with_its_variables(
    builder: PromptBuilder, name: str
) -> None:
    template = builder.registry.get(name).template
    required = extract_variables(template)
    variables = {var: f"<{var}>" for var in required}

    rendered = builder.build(name, variables)

    assert "{{" not in rendered.text
    for var in required:
        assert f"<{var}>" in rendered.text
    # Prompt version is recorded on the rendered result.
    assert rendered.name == name
    assert rendered.version == "v1"
    assert rendered.model


def test_missing_variable_raises(builder: PromptBuilder) -> None:
    with pytest.raises(MissingPromptVariableError):
        builder.build("activity", {})


def test_extra_variables_are_ignored(builder: PromptBuilder) -> None:
    required = extract_variables(builder.registry.get("activity").template)
    variables = {var: "value" for var in required}
    variables["unused_extra"] = "ignored"

    rendered = builder.build("activity", variables)
    assert "ignored" not in rendered.text


def test_rendered_prompt_carries_execution_metadata(builder: PromptBuilder) -> None:
    required = extract_variables(builder.registry.get("summary").template)
    rendered = builder.build("summary", {var: "x" for var in required})

    assert rendered.output_format == "markdown"
    assert rendered.max_tokens > 0
    assert rendered.retry_limit >= 0
    assert 0.0 <= rendered.temperature <= 2.0
