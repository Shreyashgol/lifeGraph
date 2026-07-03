"""API schema layer (request/response DTOs).

Schemas define the *public* contract of the backend. They never expose internal
graph state or SQL entities. Phase 1 ships only the health schema; activity,
memory, timeline, and summary DTOs arrive with the API layer (Phase 7).
"""
