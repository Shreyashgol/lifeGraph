"""Prompt registry.

Discovers and loads versioned prompts from disk. A prompt named ``activity``
version ``v1`` is defined by two files:

    prompts/definitions/activity_v1.yaml   (metadata)
    prompts/templates/activity_v1.md       (template text)

Loaded prompts are cached. The registry performs no variable injection — that is
the builder's job.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from app.prompts.definition import Prompt, PromptDefinition
from app.prompts.errors import PromptNotFoundError

_PACKAGE_DIR = Path(__file__).resolve().parent


class PromptRegistry:
    """Loads prompt definitions and templates by (name, version)."""

    def __init__(self, base_dir: Path | None = None) -> None:
        base = base_dir or _PACKAGE_DIR
        self._definitions_dir = base / "definitions"
        self._templates_dir = base / "templates"
        self._cache: dict[tuple[str, str], Prompt] = {}

    def get(self, name: str, version: str = "v1") -> Prompt:
        """Return the prompt for ``name``/``version``, loading and caching it."""
        key = (name, version)
        if key in self._cache:
            return self._cache[key]

        definition = self._load_definition(name, version)
        template = self._load_template(name, version)
        prompt = Prompt(definition=definition, template=template)
        self._cache[key] = prompt
        return prompt

    def list_definitions(self) -> list[PromptDefinition]:
        """Load every definition on disk (for validation and observability)."""
        definitions: list[PromptDefinition] = []
        for path in sorted(self._definitions_dir.glob("*.yaml")):
            definitions.append(self._parse_definition(path))
        return definitions

    def _load_definition(self, name: str, version: str) -> PromptDefinition:
        path = self._definitions_dir / f"{name}_{version}.yaml"
        if not path.is_file():
            raise PromptNotFoundError(f"No prompt definition: {path.name}")
        definition = self._parse_definition(path)
        if definition.name != name or definition.version != version:
            raise PromptNotFoundError(
                f"Definition {path.name} declares "
                f"{definition.name}/{definition.version}, expected {name}/{version}"
            )
        return definition

    def _load_template(self, name: str, version: str) -> str:
        path = self._templates_dir / f"{name}_{version}.md"
        if not path.is_file():
            raise PromptNotFoundError(f"No prompt template: {path.name}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _parse_definition(path: Path) -> PromptDefinition:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return PromptDefinition.model_validate(data)


@lru_cache
def get_prompt_registry() -> PromptRegistry:
    """Return a process-wide cached registry."""
    return PromptRegistry()
