"""LangGraph checkpointer factory.

Checkpointing lets a graph execution resume after interruption (docs/06 §28).
Version 1 defaults to an in-memory saver; a SQLite-backed saver can be selected
for durable checkpoints. The langgraph imports are lazy so this module (and the
builder) import cleanly without langgraph installed.
"""

from __future__ import annotations

from typing import Any


def create_checkpointer(kind: str = "memory", *, sqlite_path: str = "checkpoints.sqlite") -> Any:
    """Return a LangGraph checkpointer.

    ``kind="memory"`` (default) returns an in-process saver; ``kind="sqlite"``
    returns a SQLite-backed saver for durable checkpoints.
    """
    if kind == "memory":
        from langgraph.checkpoint.memory import MemorySaver

        return MemorySaver()
    if kind == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver

        return SqliteSaver.from_conn_string(sqlite_path)
    raise ValueError(f"unknown checkpointer kind: {kind!r}")
