"""Validation results.

Business validators answer one question — "is this proposal acceptable?" — and
return a :class:`ValidationResult`. They never decide *what to do next* (that is
the Evaluation service / graph) and never persist.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a business validation check."""

    ok: bool
    reason: str = ""
