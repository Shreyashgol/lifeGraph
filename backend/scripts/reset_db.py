#!/usr/bin/env python3
"""Database reset utility.

Drops all tables and recreates them, yielding a clean database schema.
WARNING: This is a destructive operation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add the backend directory to Python path so we can import app
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlmodel import SQLModel

from app.config import get_settings
from app.database import init_db
from app.database.session import engine


def reset_db() -> None:
    settings = get_settings()
    print(f"WARNING: Resetting database for environment: {settings.environment}")
    print(f"Database URL: {settings.database_url}")
    
    # Check if run interactively or with a force flag
    force = "--force" in sys.argv or "-f" in sys.argv
    if not force:
        if sys.stdin.isatty():
            answer = input("Type 'yes' to proceed: ")
            if answer.strip().lower() != "yes":
                print("Aborted.")
                sys.exit(1)
        else:
            print("Non-interactive session and --force not specified. Aborting.")
            sys.exit(1)

    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    print("Tables dropped.")

    print("Initializing database...")
    init_db()
    print("Database successfully reset and schema initialized.")


if __name__ == "__main__":
    reset_db()
