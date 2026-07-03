# Master Implementation Specification

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Engineering Source of Truth

---

# 1. Purpose

This document is the canonical implementation specification for LifeGraph.

It consolidates the architecture, engineering standards, AI contracts, data contracts, repository organization, and implementation roadmap into a single engineering specification.

When implementation decisions conflict with generated code, **this document takes precedence**.

---

# 2. Vision

LifeGraph is not an activity tracker.

LifeGraph is not a chatbot.

LifeGraph is a **Personal Intelligence Engine**.

Its objective is to continuously transform user activities into trustworthy knowledge, behavioural understanding, actionable recommendations, and long-term decision support.

---

# 3. Product Principles

Every implementation decision should reinforce the following principles.

* AI-first
* Explainable
* Personalized
* Modular
* Deterministic integration
* Production-ready
* Easy to extend
* Observable by default

---

# 4. Core Engineering Philosophy

The application follows one simple rule.

> The LLM reasons.

> The application decides.

AI never owns business logic.

AI never writes to the database.

AI never mutates application state directly.

---

# 5. High-Level Architecture

```text
Frontend (Next.js)

↓

FastAPI

↓

LangGraph

↓

Intelligence Services

↓

Validators

↓

Repositories

↓

SQLite

↓

Render / Vercel
```

Every layer has one responsibility.

---

# 6. Repository Structure

The implementation must follow the documented repository layout.

```text
lifegraph/

backend/
    app/
        api/
        config/
        graph/
        intelligence/
        prompts/
        repositories/
        database/
        schemas/
        models/
        validators/
        services/
        observability/
        utils/
    tests/
    pyproject.toml
    requirements.txt

frontend/

docs/

docker/
scripts/
deployment/
```

The Python backend is wrapped in `backend/` (sibling to `frontend/`), following
the standard full-stack monorepo convention. No additional top-level
architectural folders should be introduced without justification.

---

# 7. Graph Execution Contract

Every activity follows the same execution pipeline.

```text
START

↓

Activity Node

↓

Context Node

↓

Memory Node

↓

Timeline Node

↓

Behaviour Node

↓

Insight Node

↓

Recommendation Node

↓

Summary Node

↓

Reflection Node

↓

Persist

↓

END
```

Nodes communicate exclusively through `LifeGraphState`.

---

# 8. LifeGraphState

The graph state is the single shared execution object.

It contains:

* User profile
* Current activity
* Structured activity
* Retrieved context
* Timeline
* Memories
* Behaviour patterns
* Insights
* Recommendations
* Summary
* Execution metadata
* Errors

Every node:

* Reads required fields
* Updates only owned fields
* Returns an updated state

---

# 9. Intelligence Layer

Each intelligence service performs exactly one reasoning task.

Required services:

* Activity Intelligence
* Memory Intelligence
* Behaviour Intelligence
* Insight Intelligence
* Recommendation Intelligence
* Summary Intelligence
* Reflection Intelligence

Every service:

* Builds prompts
* Invokes Groq
* Validates output
* Returns structured proposals

No persistence is allowed.

---

# 10. Memory Architecture

Memory is divided into three layers.

## Working Memory

Current execution.

Implemented by `LifeGraphState`.

---

## Episodic Memory

Historical events.

Examples:

* Activities
* Sessions
* Timelines

---

## Semantic Memory

Long-term knowledge.

Examples:

* Preferences
* Interests
* Behaviour
* Goals

Semantic Memory evolves only through validated evidence.

---

# 11. Prompt System

Prompt infrastructure consists of:

* Prompt Registry
* Prompt Definitions
* Prompt Templates
* Prompt Builder
* Prompt Tests

Prompt requirements:

* Versioned
* Structured
* Provider independent
* One reasoning task
* JSON output (except Summary)

---

# 12. Validation Pipeline

Every AI response must pass:

```text
LLM

↓

JSON Parsing

↓

Pydantic Validation

↓

Business Validation

↓

Proposal Approval

↓

Repository

↓

Database
```

No proposal bypasses validation.

---

# 13. Repository Pattern

Repositories own persistence.

Required repositories:

* UserRepository
* ActivityRepository
* MemoryRepository
* TimelineRepository
* SummaryRepository

Repositories:

* Read
* Write
* Update
* Delete

They never perform reasoning.

---

# 14. Database

Version 1

* SQLite
* SQLModel
* Alembic-ready structure

Future migration:

PostgreSQL

No business-layer changes should be required.

---

# 15. API Contract

Required endpoints:

POST

* /activity

GET

* /timeline
* /memory
* /insights
* /recommendations
* /summary
* /health

API responsibilities:

* Validate requests
* Invoke graph
* Return schemas

No business logic belongs in routers.

---

# 16. Frontend

Technology:

* Next.js
* TypeScript
* Tailwind CSS
* shadcn/ui

Pages:

* Dashboard
* Activity Logger
* Timeline
* Memory
* Insights
* Daily Summary

Frontend communicates exclusively through REST APIs.

---

# 17. Observability

Every graph execution must record:

* Execution ID
* Node timings
* Prompt versions
* Model used
* Retry count
* Confidence
* Errors
* Total runtime

Logging should be structured and machine-readable.

---

# 18. Error Handling

Recoverable:

* Timeout
* Invalid JSON
* Temporary provider failure

Retry policy:

Maximum three retries.

Non-recoverable:

* Invalid schema
* Invalid business state
* Missing required input

Failures should return structured diagnostics.

---

# 19. Coding Standards

Required:

* Python 3.12+
* Type hints
* Pydantic v2
* SQLModel
* Async where appropriate
* Dependency injection
* Small functions
* Single responsibility

Avoid:

* Global mutable state
* Circular dependencies
* Hidden side effects
* Hardcoded prompts

---

# 20. Quality Gates

Every completed feature must satisfy:

Architecture

✓ Layer boundaries respected

Typing

✓ Static typing passes

Validation

✓ Pydantic models validated

Testing

✓ Unit tests added

Documentation

✓ Updated if behavior changes

Observability

✓ Logging included

No implementation is complete until all gates pass.

---

# 21. Implementation Order

Follow the documented roadmap without deviation.

1. Foundation
2. Domain Models
3. Persistence
4. Prompt Infrastructure
5. AI Layer
6. Graph
7. API
8. Frontend
9. Testing
10. Deployment

Do not begin later phases before acceptance criteria for the current phase are met.

---

# 22. Definition of Success

Version 1 is successful when a user can:

1. Log activities in natural language.
2. Receive structured understanding.
3. Build trustworthy long-term memory.
4. Generate behavioural insights.
5. Receive personalized recommendations.
6. View an AI-generated daily summary.
7. Observe consistent reasoning across multiple days.

The implementation should prioritize correctness, explainability, and maintainability over feature quantity.

---

# 23. Final Engineering Principles

The codebase should remain understandable six months after it is written.

Every architectural decision should make the next feature easier to build.

Every AI capability should be explainable.

Every persisted fact should be evidence-backed.

Every layer should have one responsibility.

LifeGraph is not designed to impress through complexity.

It is designed to demonstrate disciplined engineering applied to modern AI systems.
