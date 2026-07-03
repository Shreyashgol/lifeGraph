# System Architecture

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Architecture Approved

---

# 1. Architecture Philosophy

LifeGraph is **not** designed as a chatbot.

It is designed as a **Personal Intelligence System**.

The system continuously transforms user activities into structured knowledge, behavioral understanding, and personalized recommendations.

The architecture follows five principles:

* Modular Intelligence
* Shared State
* Explainable AI
* Evidence-Based Memory
* Separation of Concerns

---

# 2. Architectural Goals

The architecture must be:

* Modular
* Extensible
* Explainable
* Testable
* Production-ready
* Easy to deploy
* Easy to evolve

Every component should have a single responsibility.

---

# 3. High-Level Architecture

```text
                           ┌──────────────────────┐
                           │      Next.js UI      │
                           │   (Vercel Free Tier) │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │       FastAPI        │
                           │   REST Endpoints     │
                           └──────────┬───────────┘
                                      │
                                      ▼
                    ┌────────────────────────────────┐
                    │  Personal Intelligence Engine   │
                    │      (LangGraph StateGraph)     │
                    └──────────┬──────────────────────┘
                               │
                               ▼
                      Shared Graph State
                               │
        ┌────────────┬─────────┼─────────┬────────────┐
        ▼            ▼         ▼         ▼            ▼
 Activity      Context     Memory    Behaviour    Timeline
    Node         Node        Node        Node        Node
        └────────────┬─────────┬──────────────┘
                     ▼
              Insight Node
                     ▼
          Recommendation Node
                     ▼
              Summary Node
                     ▼
             Reflection Node
                     ▼
                Persist State
                     ▼
                  SQLite DB
```

---

# 4. Layered Architecture

The application is organized into layers.

```text
Presentation Layer
        │
API Layer
        │
Orchestration Layer
        │
Reasoning Layer
        │
Persistence Layer
        │
Infrastructure Layer
```

Each layer depends only on the layer beneath it.

---

# 5. Presentation Layer

Responsibilities

* User Interface
* Activity Logging
* Timeline View
* Daily Summary
* Insights
* Memory Dashboard

Technology

* Next.js
* Tailwind CSS
* shadcn/ui

No business logic exists here.

---

# 6. API Layer

Responsibilities

* Receive requests
* Validate payloads
* Call orchestration engine
* Return responses

Technology

* FastAPI

The API never communicates directly with the LLM.

It communicates only with the orchestration layer.

---

# 7. Orchestration Layer

The orchestration layer is the heart of the application.

Technology

* LangGraph

Responsibilities

* Execute workflow
* Manage graph state
* Route execution
* Trigger reasoning nodes
* Handle retries
* Manage checkpoints

Business rules are coordinated here—not implemented here.

---

# 8. Shared Graph State

Every node receives the same state object.

Example fields:

```text
current_activity

structured_activity

user_profile

timeline

memories

behaviour_patterns

insights

recommendations

daily_summary

execution_metadata

confidence

errors
```

Each node updates only the fields it owns.

---

# 9. Graph Workflow

```text
START
   │
   ▼
Activity Node
   │
   ▼
Evaluation Node   (LLM-as-judge; conditional retry → Activity, max 2)
   │
   ▼
Context Node
   │
   ▼
Memory Node
   │
   ▼
Timeline Node
   │
   ▼
Behaviour Node
   │
   ▼
Insight Node
   │
   ▼
Recommendation Node
   │
   ▼
Summary Node
   │
   ▼
Reflection Node
   │
   ▼
Persist State
   │
   ▼
END
```

The Evaluation Node judges the Activity proposal and drives a conditional retry
edge (see docs/06 §14a, docs/08 §14a). Reflection remains the holistic
end-of-graph QA step.

---

# 10. Node Responsibilities

## Activity Node

Purpose

Transform raw natural language into structured activity.

Input

* Raw activity
* Timestamp

Output

* Structured activity
* Confidence score

---

## Context Node

Purpose

Retrieve only relevant user context.

Examples

* Active projects
* Goals
* Stable routines
* Behaviour history

No reasoning occurs here.

---

## Memory Node

Purpose

Evaluate whether the activity contributes to long-term memory.

Responsibilities

* Build memory proposal
* Update confidence
* Attach supporting evidence

Never create permanent memory from a single event.

---

## Timeline Node

Purpose

Maintain chronological history.

Responsibilities

* Store activity
* Create sessions
* Compute durations

No AI reasoning.

---

## Behaviour Node

Purpose

Detect behavioural patterns.

Examples

* Deep work frequency
* Preferred work hours
* Context switching
* Learning habits

Produces structured behavioural observations.

---

## Insight Node

Purpose

Generate explainable insights.

Every insight must reference evidence.

Examples

* Coding time increased.
* Afternoon productivity declined.

---

## Recommendation Node

Purpose

Generate personalized recommendations.

Every recommendation includes:

* Recommendation
* Reason
* Expected impact
* Priority

Recommendations are always supported by evidence.

---

## Summary Node

Purpose

Generate a natural-language daily report.

Sections

* Overview
* Timeline
* Metrics
* Insights
* Recommendations
* Reflection

This is the only node allowed to generate long-form text.

---

## Reflection Node

Purpose

Validate reasoning before completion.

Questions

* Was confidence sufficient?
* Were assumptions made?
* Should clarification be requested?
* Was memory updated correctly?

Reflection improves reliability.

---

# 11. Intelligence Services

Nodes never communicate directly with the LLM.

Instead:

```text
Node
   │
   ▼
Intelligence Service
   │
   ▼
Groq Client
   │
   ▼
Validated Response
```

Examples

* ActivityIntelligenceService
* MemoryIntelligenceService
* BehaviourIntelligenceService
* SummaryIntelligenceService

This isolates model-specific code from orchestration.

---

# 12. Prompt Architecture

Every reasoning task has a dedicated prompt.

```text
Activity Prompt

↓

Memory Prompt

↓

Behaviour Prompt

↓

Insight Prompt

↓

Recommendation Prompt

↓

Summary Prompt
```

One prompt.

One responsibility.

---

# 13. Memory Architecture

LifeGraph maintains multiple memory domains.

```text
Identity

Goals

Projects

Routine

Behaviour

Interests

Preferences

Decision History
```

Memory updates require:

* Evidence
* Confidence
* Supporting activities

---

# 14. Persistence Architecture

SQLite stores:

* Users
* Activities
* Memories
* Timeline
* Insights
* Recommendations
* Daily summaries

LangGraph checkpoints preserve execution state.

---

# 15. Error Handling Strategy

Every node should:

* Validate inputs
* Validate outputs
* Handle failures gracefully
* Retry AI requests when appropriate
* Record execution errors

The graph should never fail because of one malformed AI response.

---

# 16. Logging Strategy

Every node logs:

* Start time
* End time
* Duration
* Prompt version
* Confidence
* Validation result
* Errors

This supports debugging and explainability.

---

# 17. Deployment Architecture

```text
User
   │
   ▼
Next.js (Vercel)
   │
   ▼
FastAPI (Render)
   │
   ▼
LangGraph Engine
   │
   ▼
Groq API
   │
   ▼
SQLite
```

The system is fully deployable on free tiers.

---

# 18. Scalability Strategy

Future improvements should not require architectural redesign.

Planned upgrades:

Version 2

* PostgreSQL
* Authentication
* Background workers

Version 3

* Redis caching
* Calendar integration
* Browser extension

Version 4

* AI Coach
* Predictive planning
* Team intelligence

The current architecture already supports these upgrades through modular boundaries.

---

# 19. Design Decisions

## Why LangGraph?

The product is a reasoning pipeline, not a chatbot.

LangGraph provides:

* Deterministic execution
* Shared state
* Conditional routing
* Checkpointing
* Extensible workflows

---

## Why Groq?

* Very low latency
* Excellent structured output
* OpenAI-compatible APIs
* Suitable for iterative reasoning
* Great developer experience

---

## Why SQLite?

* Zero configuration
* Free
* Portable
* Easy deployment
* Sufficient for Version 1

---

## Why FastAPI?

* High performance
* Excellent typing
* Automatic OpenAPI documentation
* Easy frontend integration

---

# 20. Architecture Summary

LifeGraph is built around one central concept:

> **The intelligence does not live inside the language model.**

The intelligence emerges from:

* Structured workflows
* Shared graph state
* Evidence-based memory
* Behaviour analysis
* Explainable reasoning
* Modular architecture

The LLM performs reasoning.

The system performs intelligence.

This separation enables maintainability, extensibility, and trustworthy personalization over time.
