# Database

**Engine:** Neon Postgres + pgvector (production) / SQLite (local & tests).
The engine is dialect-agnostic and selected via `DATABASE_URL`. On Postgres the
`vector` extension is enabled at startup for semantic-memory embeddings.

Tables (Version 1):

- users
- activities
- memories
- timelines
- summaries

Insights and recommendations are persisted embedded within `summaries` (JSON),
not as standalone tables in Version 1.
