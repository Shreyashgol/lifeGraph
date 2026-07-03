"""Application-wide constants.

Only values that are genuinely fixed and cross-cutting belong here. Tunable
configuration lives in ``settings.py``; domain-specific constants (confidence
thresholds, memory rules, etc.) are introduced with their owning layers in
later phases.
"""

from __future__ import annotations

# Health status literals returned by the /health endpoint.
STATUS_OK = "ok"

# --- Reasoning thresholds (chosen defaults; see design review §6 #9) ---------
# Activity proposals below this confidence fail business validation.
MIN_ACTIVITY_CONFIDENCE = 0.6
# A memory only becomes ACTIVE after this many corroborating observations...
MEMORY_EVIDENCE_THRESHOLD = 3
# ...and once its confidence reaches this level.
MEMORY_ACTIVATION_CONFIDENCE = 0.75
# Maximum Evaluation-driven quality retries before accepting best-effort.
MAX_QUALITY_RETRIES = 2
