"""Structured logging configuration.

LifeGraph emits machine-readable JSON logs so that node execution, prompt
versions, latency, and errors can be traced in production (see
``docs/03_ARCHITECTURE.md`` §16). This module only configures logging; richer
execution telemetry lives in ``app/observability`` in later phases.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

_RESERVED = frozenset(logging.makeLogRecord({}).__dict__.keys()) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON objects.

    Any non-reserved attributes attached to a record (via ``logger.info(...,
    extra={...})``) are included, which lets nodes and services log structured
    context such as ``execution_id`` or ``prompt_version``.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger for structured JSON output to stdout.

    Idempotent: repeated calls replace existing handlers rather than stacking
    them, which keeps test runs and hot reloads clean.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Thin wrapper for consistent import sites."""
    return logging.getLogger(name)
