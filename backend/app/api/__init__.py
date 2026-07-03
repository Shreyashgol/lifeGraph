"""API layer.

Owns REST routers, request parsing, and response serialization. Routers stay
thin: they validate input, invoke the appropriate layer, and serialize the
result. They contain no business logic, no LLM calls, and no SQL.
"""
