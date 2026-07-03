# System Flow

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Runtime Workflow Specification

---

# Purpose

This document describes how LifeGraph behaves during runtime.

Unlike the architecture document, which explains *what* the system is composed of, this document explains *how* information flows through the system.

Every workflow defined here is intended to be deterministic, modular, and easy to extend.

---

# Runtime Philosophy

LifeGraph does not execute one large AI prompt.

Instead, it executes a sequence of specialized reasoning stages coordinated by LangGraph.

Every stage has:

* A single responsibility
* Defined input
* Defined output
* Shared graph state
* Validation before continuing

---

# High-Level Runtime Flow

```text
User
 │
 ▼
Natural Language Activity
 │
 ▼
FastAPI Endpoint
 │
 ▼
Graph Initialization
 │
 ▼
LangGraph Workflow
 │
 ▼
Activity Understanding
 │
 ▼
Context Retrieval
 │
 ▼
Memory Evaluation
 │
 ▼
Timeline Update
 │
 ▼
Behaviour Analysis
 │
 ▼
Insight Generation
 │
 ▼
Recommendation Generation
 │
 ▼
Summary Generation (when requested)
 │
 ▼
Persist State
 │
 ▼
API Response
```

---

# Workflow 1 — User Onboarding

## Objective

Create the initial user profile.

### Input

User provides:

* Name
* Occupation
* Timezone
* Primary goals
* Current projects
* Interests

### Processing

* Validate input
* Create User Profile
* Initialize memory buckets
* Store profile in database

### Output

* User successfully onboarded
* Empty timeline
* Initialized memory

---

# Workflow 2 — Activity Logging

## Objective

Accept activities naturally.

Example

> Worked on authentication module for two hours.

### Processing

1. Receive request
2. Validate payload
3. Create graph state
4. Invoke LangGraph

### Output

Graph execution begins.

---

# Workflow 3 — Graph Execution

The graph executes sequentially.

```text
START
 │
 ▼
Activity Node
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
Reflection Node
 │
 ▼
Persist
 │
 ▼
END
```

---

# Workflow 4 — Activity Understanding

## Goal

Transform raw language into structured data.

### Input

Raw activity.

### Processing

* Intent extraction
* Category classification
* Duration extraction
* Entity extraction
* Project identification

### Validation

* Pydantic schema validation
* Confidence validation
* Retry if malformed

### Output

Structured Activity Model

---

# Workflow 5 — Context Retrieval

## Goal

Retrieve only relevant context.

### Context Sources

* Goals
* Projects
* Behaviour
* Interests
* Previous memories

### Rules

Never retrieve unrelated memories.

Example

Coding activity should not retrieve food preferences.

---

# Workflow 6 — Memory Evaluation

## Goal

Determine whether new evidence changes long-term understanding.

### Input

* Structured Activity
* Retrieved Context

### Processing

* Evaluate novelty
* Compare with existing memory
* Generate memory proposal
* Calculate confidence

### Decision

If evidence threshold reached

↓

Update memory

Otherwise

↓

Store as observation only

---

# Workflow 7 — Timeline Update

## Goal

Maintain chronological history.

### Steps

* Save activity
* Assign timestamp
* Insert into today's timeline
* Merge adjacent sessions when appropriate

### Output

Updated timeline.

---

# Workflow 8 — Behaviour Analysis

## Goal

Identify meaningful behavioural trends.

Examples

* Deep work frequency
* Learning consistency
* Preferred work hours
* Context switching
* Meeting interruptions

Behaviour analysis operates on accumulated history rather than a single activity.

---

# Workflow 9 — Insight Generation

## Goal

Produce explainable observations.

Example

Insight

> Morning focus improved this week.

Supporting Evidence

* 12 deep work sessions
* Average focus duration increased
* Fewer interruptions

Every insight must reference evidence.

---

# Workflow 10 — Recommendation Generation

## Goal

Generate personalized actions.

Recommendations are based on:

* Goals
* Behaviour
* Memory
* Insights

Example

Recommendation

Schedule coding before lunch.

Reason

Morning productivity has consistently exceeded afternoon productivity over the past two weeks.

---

# Workflow 11 — Daily Summary

Triggered on user request.

### Input

* Timeline
* Behaviour
* Memory
* Insights
* Recommendations

### Output

Markdown report containing:

* Overview
* Timeline
* Productivity metrics
* Behaviour analysis
* Insights
* Recommendations
* Reflection
* Tomorrow's focus

---

# Workflow 12 — Reflection

Final quality check.

Questions

* Was confidence acceptable?
* Were unsupported assumptions made?
* Should clarification be requested?
* Was memory updated correctly?

Reflection can:

* Lower confidence
* Reject a memory update
* Request clarification
* Approve execution

---

# Workflow 13 — Persistence

Persist the following:

SQLite

* User
* Activities
* Timeline
* Memories
* Insights
* Recommendations
* Daily summaries

Optional JSON

* Prompt logs
* Debug traces
* Execution metadata

---

# Workflow 14 — Error Handling

## AI Failure

If Groq request fails

↓

Retry

↓

Fallback

↓

Return meaningful error

---

## Invalid JSON

Retry prompt.

If still invalid

↓

Reject response

↓

Do not corrupt application state.

---

## Low Confidence

If confidence is below threshold

↓

Do not update memory.

↓

Request clarification if necessary.

---

## Database Failure

* Log error
* Preserve graph state
* Return safe response
* Prevent data corruption

---

# Workflow 15 — API Lifecycle

```text
Client Request
      │
      ▼
FastAPI Validation
      │
      ▼
Graph Execution
      │
      ▼
Database Update
      │
      ▼
Response Serialization
      │
      ▼
Client Response
```

The API remains thin.

Business logic belongs to the graph.

---

# Workflow 16 — Deployment Lifecycle

Developer

↓

Local Testing

↓

Unit Tests

↓

Integration Tests

↓

Git Push

↓

Render Deployment

↓

Health Check

↓

Vercel Deployment

↓

End-to-End Verification

---

# Runtime State Evolution

Graph State evolves continuously.

Example

```text
Raw Activity
      │
      ▼
Structured Activity
      │
      ▼
Updated Timeline
      │
      ▼
Updated Memory
      │
      ▼
Behaviour Patterns
      │
      ▼
Insights
      │
      ▼
Recommendations
```

The state becomes progressively richer during execution.

---

# Performance Targets

| Operation              | Target   |
| ---------------------- | -------- |
| Activity Understanding | < 3 s    |
| Graph Execution        | < 5 s    |
| Timeline Retrieval     | < 500 ms |
| Summary Generation     | < 8 s    |
| Health Check           | < 100 ms |

---

# Engineering Principles

Every workflow must satisfy:

* Deterministic execution
* Clear responsibilities
* Schema validation
* Structured logging
* Explainable AI
* Recoverable failures

No workflow should silently fail or mutate unrelated state.

---

# Flow Summary

LifeGraph follows a simple philosophy:

1. Capture user activity.
2. Understand it.
3. Retrieve relevant context.
4. Learn from evidence.
5. Detect behavioural patterns.
6. Generate explainable insights.
7. Recommend meaningful improvements.
8. Continuously evolve the user's intelligence profile.

The runtime is intentionally modular so that each stage can be improved independently without changing the overall architecture.
