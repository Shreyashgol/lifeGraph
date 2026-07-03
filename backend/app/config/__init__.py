"""Configuration layer.

Owns environment loading, application settings, logging configuration, and
constants. Nothing else belongs here — no business logic, persistence, or
reasoning.
"""

from app.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
