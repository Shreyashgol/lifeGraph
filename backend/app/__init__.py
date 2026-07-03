"""LifeGraph — AI-Powered Personal Intelligence Engine.

Backend application package. The codebase is organized around business
capabilities (see ``docs/11_FOLDER_STRUCTURE.md``) rather than technologies.
Dependencies always flow downward:

    api -> graph -> intelligence -> validators -> repositories -> database

Phase 1 (Project Foundation) establishes the runnable skeleton: configuration,
structured logging, the health endpoint, and the folder structure. Domain
models, persistence, prompts, intelligence services, the graph engine, and the
remaining API surface are introduced in later phases.
"""

__version__ = "0.1.0"
