# Memory Architecture

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Canonical Memory Specification

---

# 1. Purpose

Memory is the defining capability of LifeGraph.

Without memory, the application is simply another AI assistant.

With memory, it becomes a continuously evolving Personal Intelligence Engine.

This document defines:

* What memory is
* How memory is created
* How memory evolves
* How memory is retrieved
* How memory influences reasoning
* How memory remains trustworthy

---

# 2. Memory Philosophy

LifeGraph does **not** store conversations.

It stores **knowledge**.

Conversations are temporary.

Knowledge persists.

Every memory must answer one question:

> **"What has the system genuinely learned about this user?"**

---

# 3. Core Principle

Activities are **not** memories.

Activities are observations.

Observations become evidence.

Evidence becomes patterns.

Patterns become memories.

The complete lifecycle is:

```text
Activity

↓

Observation

↓

Evidence

↓

Behaviour Pattern

↓

Memory
```

Skipping any stage is prohibited.

---

# 4. Why Traditional Memory Fails

Most AI assistants store either:

* Chat history
* Vector embeddings
* Previous prompts

This creates several issues:

* Duplicate information
* Weak personalization
* Poor explainability
* Retrieval noise
* Hallucinated assumptions

LifeGraph instead stores validated, structured knowledge.

---

# 5. Definition of Memory

A memory is:

> A structured, evidence-backed representation of stable knowledge about the user.

Every memory must satisfy:

* Explainable
* Traceable
* Versionable
* Evidence-backed
* Confidence-scored

---

# 6. Memory Categories

LifeGraph organizes memory into domains.

```text
Identity

Goals

Projects

Interests

Preferences

Routine

Behaviour

Skills

Decision History

Relationships

Health (future)

Finance (future)
```

Each category evolves independently.

---

# 7. Memory Hierarchy

```mermaid
flowchart TD

Activity

↓

Observation

↓

Evidence

↓

Knowledge Candidate

↓

Validated Memory

↓

Long-Term Memory
```

Every transition requires validation.

---

# 8. Memory Lifecycle

A memory follows the lifecycle below.

```text
Create Candidate

↓

Collect Evidence

↓

Increase Confidence

↓

Validate

↓

Persist

↓

Retrieve

↓

Update

↓

Archive
```

Deletion should be rare.

Evolution is preferred.

---

# 9. Memory Object

Every memory contains:

| Field                   | Description                   |
| ----------------------- | ----------------------------- |
| id                      | Unique identifier             |
| type                    | Memory category               |
| statement               | Learned fact                  |
| confidence              | Confidence score              |
| evidence_count          | Supporting observations       |
| supporting_activity_ids | Evidence references           |
| source                  | Origin of memory              |
| created_at              | Creation time                 |
| updated_at              | Last modification             |
| status                  | Candidate / Active / Archived |

---

# 10. Memory States

Every memory belongs to one state.

```text
Candidate

↓

Validated

↓

Active

↓

Archived
```

Candidate memories never influence recommendations.

Only Active memories participate in reasoning.

---

# 11. Confidence Model

Confidence is cumulative.

Example

Observation 1

↓

0.42

Observation 2

↓

0.61

Observation 5

↓

0.83

Observation 12

↓

0.96

Confidence should grow through repeated evidence rather than large jumps.

---

# 12. Evidence Model

Evidence links memories to observations.

Example

Memory

```text
User prefers morning coding.
```

Evidence

```text
Activity #14

Activity #28

Activity #36

Activity #41
```

Every memory should be explainable through evidence.

---

# 13. Memory Evolution

Existing memories evolve instead of being replaced.

Example

Initial

```text
User is interested in AI.
Confidence 0.64
```

↓

Later

```text
User actively builds AI products.
Confidence 0.92
```

The statement becomes richer as confidence increases.

---

# 14. Memory Validation

Before activation:

The proposal must satisfy:

* Schema validation
* Business validation
* Evidence threshold
* Confidence threshold

Only then may it become an Active memory.

---

# 15. Engineering Principles

Memory must never be:

* Guessed
* Hallucinated
* Hardcoded
* Created from one observation
* Modified without evidence

The memory layer exists to preserve trustworthy personalization over time.

# 16. Three-Layer Memory Architecture

LifeGraph organizes memory into three distinct layers.

Each layer has a different responsibility.

```mermaid
flowchart TD

WorkingMemory

↓

EpisodicMemory

↓

SemanticMemory
```

Separating memory by responsibility dramatically improves retrieval quality, explainability, and scalability.

---

# 17. Working Memory

## Purpose

Working Memory represents the information required during the current graph execution.

It is temporary.

It exists only while the graph is running.

Once execution completes, Working Memory disappears.

---

## Implementation

Working Memory is implemented as:

```text
LifeGraphState
```

Every LangGraph node reads from and writes to this state.

---

## Contents

Working Memory may contain:

* Current activity
* Structured activity
* Retrieved context
* Timeline snapshot
* Memory proposals
* Behaviour patterns
* Insights
* Recommendations
* Summary draft
* Execution metadata

---

## Lifetime

```text
Graph Starts

↓

Initialize

↓

Node Updates

↓

Reflection

↓

Persist

↓

Destroyed
```

Working Memory is never persisted directly.

---

# 18. Episodic Memory

## Purpose

Episodic Memory stores experiences.

These are historical events that actually occurred.

Examples

* Activities
* Sessions
* Daily timelines
* Daily summaries

Unlike Working Memory,

Episodic Memory survives across executions.

---

## Examples

```text
Monday

↓

Worked on API

↓

Meeting

↓

Read Paper

↓

Gym
```

These are experiences.

Not knowledge.

---

## Storage

SQLite

Tables

* activities
* sessions
* timelines
* summaries

Future

↓

PostgreSQL

---

## Responsibilities

Provide historical evidence.

Never perform reasoning.

---

# 19. Semantic Memory

## Purpose

Semantic Memory stores learned knowledge.

Examples

```text
User prefers Python.

↓

User works best in mornings.

↓

User enjoys AI research.

↓

User has active interest
in distributed systems.
```

These are not events.

They are conclusions.

---

## Storage

SQLite

Table

```text
memories
```

Future

↓

PostgreSQL

↓

Vector Store

---

## Responsibilities

Semantic Memory influences every reasoning stage.

---

# 20. Memory Interaction

The three layers continuously interact.

```mermaid
flowchart LR

WorkingMemory

--> EpisodicMemory

EpisodicMemory

--> SemanticMemory

SemanticMemory

--> WorkingMemory
```

Example

Current Activity

↓

Working Memory

↓

Store Activity

↓

Episodic Memory

↓

Repeated Evidence

↓

Semantic Memory

↓

Future Recommendations

---

# 21. Memory Retrieval Strategy

LifeGraph never loads all memories.

Instead,

retrieval is selective.

Pipeline

```text
Current Activity

↓

Relevant Categories

↓

Relevant Memories

↓

Graph Context
```

Example

Current Activity

```text
Working on LifeGraph backend.
```

Retrieve

* Active Project
* Programming Preferences
* Backend Skills
* Current Goal

Do NOT retrieve

* Gym Routine
* Reading Habit
* Food Preferences

---

# 22. Context Window Strategy

Every reasoning task has its own retrieval policy.

Example

Activity Understanding

Needs

* User Profile
* Active Project

Memory Proposal

Needs

* Existing Memories
* Evidence

Recommendation

Needs

* Behaviour
* Goals
* Preferences

Summary

Needs

Everything

The Prompt Builder is responsible for selecting the correct context.

---

# 23. Memory Proposal Pipeline

AI never writes memory directly.

Pipeline

```text
Activity

↓

Observation

↓

Memory Proposal

↓

Validator

↓

Business Rules

↓

Repository

↓

Semantic Memory
```

This separation protects the integrity of long-term knowledge.

---

# 24. Evidence Accumulation

Evidence should accumulate over time.

Example

Activity 14

↓

Evidence Count

1

↓

Activity 29

↓

Evidence Count

2

↓

Activity 45

↓

Evidence Count

3

↓

Memory Confidence

0.91

The confidence model should reward consistent observations rather than isolated events.

---

# 25. Memory Conflict Resolution

Contradictory observations are expected.

Example

Existing Memory

```text
Prefers Morning Coding
```

New Evidence

```text
Codes Every Night
```

The system should not immediately overwrite memory.

Instead

* Reduce confidence
* Collect more evidence
* Re-evaluate
* Update only when justified

Memory evolution is gradual.

---

# 26. Memory Retrieval Ranking

Relevant memories should be ranked using multiple signals.

Suggested ranking factors:

| Signal         | Purpose                         |
| -------------- | ------------------------------- |
| Category Match | Highest priority                |
| Confidence     | Higher confidence preferred     |
| Recency        | Recent knowledge weighted       |
| Evidence Count | Stable memories ranked higher   |
| Goal Relevance | Align with user goals           |
| Active Project | Prefer current project memories |

The retrieval strategy should maximize relevance while minimizing unnecessary context.

---

# 27. Memory Decay (Future)

Not all memories remain equally relevant.

Future versions may support gradual confidence decay.

Example

```text
Last Evidence

↓

180 Days

↓

Reduce Confidence

↓

Eventually Archive
```

Stable identity memories should never decay automatically.

Routine and preference memories may.

---

# 28. Memory Indexing

Semantic memories should be indexed for efficient retrieval.

Recommended indexes:

* Memory Type
* Project
* Confidence
* Updated At
* Active Status

Future enhancements may include semantic search using embeddings while preserving the same retrieval contract.

---

# 29. Memory Engineering Rules

Every memory implementation must satisfy:

* Memory is evidence-backed.
* Memory is explainable.
* Memory evolves gradually.
* Memory retrieval is selective.
* Memory proposals require validation.
* Working Memory is transient.
* Episodic Memory stores experiences.
* Semantic Memory stores knowledge.

These rules preserve both accuracy and personalization.

---

# 30. Memory Architecture Summary

LifeGraph treats memory as a hierarchy rather than a single storage mechanism.

```text
Working Memory
(Current Execution)

↓

Episodic Memory
(Historical Experience)

↓

Semantic Memory
(Learned Knowledge)
```

This separation mirrors human cognition while remaining practical for implementation.

It allows the system to reason efficiently, personalize responsibly, and evolve continuously without confusing raw events with learned understanding.

The result is a memory system that is structured, explainable, and scalable—forming the foundation of the Personal Intelligence Engine.
