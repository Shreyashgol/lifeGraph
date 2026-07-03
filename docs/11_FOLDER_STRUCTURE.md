# Repository Structure

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Canonical Repository Architecture

---

# 1. Purpose

This document defines the repository organization of LifeGraph.

The repository is organized around **business capabilities**, not technologies.

Every directory represents a responsibility.

No directory should have overlapping ownership.

---

# 2. Repository Philosophy

The repository should answer one question:

> "Where does this responsibility belong?"

Instead of

```text
models/

services/

utils/
```

We organize around the architecture.

The repository should mirror the system.

---

# 3. High-Level Repository

```text
lifegraph/

│

├── backend/

│   ├── app/

│   ├── tests/

│   ├── pyproject.toml

│   └── requirements.txt

├── frontend/

├── docs/

├── scripts/

├── deployment/

├── .github/

├── docker/

└── README.md
```

The backend (Python/FastAPI) is wrapped in `backend/`, sibling to `frontend/`,
`docs/`, and the operational directories. All `app/...` paths in the sections
below are relative to `backend/`.

---

# 4. Backend Layout

```text
backend/app/

├── api/

├── config/

├── graph/

├── intelligence/

├── prompts/

├── repositories/

├── database/

├── schemas/

├── models/

├── validators/

├── services/

├── utils/

├── observability/

└── main.py
```

Every folder has one owner.

---

# 5. app/api/

## Responsibility

Expose REST endpoints.

Contains:

* Routers
* Dependencies
* Request parsing
* Response serialization

Must NOT contain:

* Business logic
* LLM calls
* SQL queries

---

# Example

```text
api/

activity.py

summary.py

memory.py

health.py
```

---

# 6. app/config/

Contains

* Environment loading
* Settings
* Constants
* Feature flags

Example

```text
config/

settings.py

logging.py

constants.py
```

Only configuration belongs here.

---

# 7. app/graph/

The heart of LifeGraph.

Contains

```text
graph/

builder.py

state.py

nodes/

edges.py

checkpointer.py
```

Responsibilities

* Build graph
* Define StateGraph
* Register nodes
* Register edges
* Checkpoint execution

No AI prompts.

No SQL.

---

# 8. app/graph/nodes/

One file

↓

One node.

```text
nodes/

activity.py

evaluation.py

context.py

memory.py

timeline.py

behaviour.py

insight.py

recommendation.py

summary.py

reflection.py
```

Every node

* Reads GraphState
* Updates owned fields
* Returns GraphState

Nothing else.

---

# 9. app/intelligence/

Contains AI reasoning services.

```text
intelligence/

activity_service.py

memory_service.py

behaviour_service.py

insight_service.py

recommendation_service.py

summary_service.py

reflection_service.py

evaluation_service.py
```

Responsibilities

* Build prompt
* Call model
* Parse response
* Return proposal

Never

* Save database
* Update graph
* Call API

---

# 10. app/prompts/

Contains prompt assets.

Recommended structure

```text
prompts/

definitions/

templates/

tests/
```

Definitions

↓

Metadata

Templates

↓

Markdown

Tests

↓

Prompt evaluation cases

---

# 11. app/repositories/

Repositories own persistence.

```text
repositories/

activity_repository.py

memory_repository.py

summary_repository.py

user_repository.py
```

Responsibilities

* Save
* Retrieve
* Update
* Query

Repositories never perform AI reasoning.

---

# 12. app/database/

Contains persistence models.

```text
database/

models.py

session.py

base.py

migrations/
```

Responsibilities

* SQLModel entities
* Session management
* Database initialization

No business logic.

---

# 13. app/schemas/

Contains API DTOs.

Examples

```text
schemas/

activity.py

memory.py

summary.py

user.py
```

These models define request and response contracts.

They should never contain persistence details.

---

# 14. app/models/

Contains domain models.

Examples

```text
models/

activity.py

memory.py

timeline.py

behaviour.py

summary.py
```

These represent business concepts.

They are independent of FastAPI and SQLModel.

---

# 15. app/validators/

Validation layer.

Examples

```text
validators/

activity_validator.py

memory_validator.py

proposal_validator.py
```

Responsibilities

* Business validation
* Proposal approval
* Rule enforcement

Validation occurs after schema parsing and before persistence.

---

# 16. app/services/

Contains deterministic application services.

Examples

```text
services/

timeline_service.py

statistics_service.py

summary_service.py
```

These services perform calculations and orchestration that do not require AI.

---

# 17. app/observability/

Contains logging and monitoring.

```text
observability/

logging.py

metrics.py

telemetry.py
```

Responsibilities

* Structured logs
* Execution metrics
* Node timing
* Prompt metrics

Observability is treated as a first-class concern.

---

# 18. app/utils/

Contains truly generic helpers.

Examples

* Time formatting
* UUID helpers
* JSON utilities

Rule:

If a utility becomes domain-specific, move it into the appropriate module.

---

# 19. Engineering Rules

Every folder has one responsibility.

Folders should never depend cyclically on each other.

Example dependency flow:

```text
API

↓

Graph

↓

Intelligence

↓

Validators

↓

Repositories

↓

Database
```

The dependency direction should always point downward.

---

# 20. Repository Summary

The repository mirrors the architecture.

Each layer has clear ownership.

This organization improves:

* Discoverability
* Testability
* Scalability
* Onboarding
* Maintainability

A new engineer should be able to locate any responsibility within minutes simply by following the architectural boundaries defined in this document.
