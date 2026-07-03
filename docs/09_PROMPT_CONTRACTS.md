# Prompt Contracts

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Canonical Prompt Engineering Specification

---

# 1. Purpose

This document defines the engineering standards for every prompt used within LifeGraph.

Prompts are treated as **versioned software artifacts**, not strings embedded inside application code.

Every prompt should be:

* Version controlled
* Independently testable
* Provider independent
* Deterministic where possible
* Structured
* Maintainable

Prompt engineering is considered an engineering discipline rather than an implementation detail.

---

# 2. Prompt Philosophy

A prompt should never attempt to solve multiple reasoning problems.

Instead:

One Prompt

↓

One Responsibility

Examples

✓ Activity Understanding

✓ Memory Proposal

✓ Behaviour Analysis

✓ Recommendation Generation

✗ Understand activity + update memory + generate recommendation

---

# 3. Prompt Architecture

Every prompt follows exactly the same structure.

```text
Role

↓

Objective

↓

Background

↓

Available Context

↓

Input

↓

Instructions

↓

Output Schema

↓

Validation Rules

↓

Examples

↓

Failure Behaviour
```

No prompt should omit these sections.

---

# 4. Prompt Lifecycle

Every prompt follows this lifecycle.

```text
Design

↓

Review

↓

Version

↓

Testing

↓

Deployment

↓

Monitoring

↓

Improvement
```

Prompt changes should follow the same review process as code changes.

---

# 5. Prompt Repository

Recommended structure

```text
app/

prompts/

activity/

v1.md

memory/

v1.md

behaviour/

v1.md

insight/

v1.md

recommendation/

v1.md

summary/

v1.md
```

Every prompt folder should contain:

* Current version
* Archived versions
* Test cases

---

# 6. Prompt Template

Every prompt should follow the template below.

```text
ROLE

You are ...

OBJECTIVE

Your responsibility is ...

BACKGROUND

The application ...

AVAILABLE CONTEXT

{{context}}

USER INPUT

{{input}}

TASK

...

OUTPUT FORMAT

...

RULES

...

FAILURE

...
```

This structure improves consistency and readability.

---

# 7. Prompt Variables

Prompts must never contain hardcoded business data.

Instead, use variables.

Examples:

```text
{{user_profile}}

{{timeline}}

{{activity}}

{{memories}}

{{behaviour}}

{{goals}}

{{preferences}}

{{today}}

{{context}}
```

Variables should be injected by the Prompt Builder.

---

# 8. Prompt Builder

Prompts should not be concatenated manually.

Instead:

```text
Template

↓

Variable Injection

↓

Rendered Prompt

↓

LLM
```

Responsibilities of the Prompt Builder:

* Load template
* Inject variables
* Validate required variables
* Render final prompt
* Record prompt version

---

# 9. Context Injection Strategy

Only inject information required for the reasoning task.

Poor example:

Entire user history.

Better example:

* Active project
* Relevant memories
* Current activity
* User goals

Reducing irrelevant context improves reasoning quality and reduces token usage.

---

# 10. Prompt Rules

Every prompt must satisfy the following rules.

### Rule 1

One prompt.

One reasoning task.

---

### Rule 2

Output must match a predefined schema.

---

### Rule 3

Avoid unnecessary natural language.

Prefer structured outputs.

---

### Rule 4

Never request information already available in GraphState.

---

### Rule 5

Never reference implementation details.

The LLM should reason about business concepts, not APIs or databases.

---

# 11. Output Contracts

Most prompts should return JSON.

Example

```json
{
  "category": "...",
  "confidence": 0.95
}
```

Only the Summary prompt may return Markdown.

All outputs must be validated before use.

---

# 12. Prompt Versioning

Every prompt should be versioned.

Examples

```text
activity_v1

activity_v2

activity_v3
```

Execution metadata should record:

* Prompt name
* Prompt version
* Model
* Timestamp

This enables reproducibility and regression analysis.

---

# 13. Prompt Independence

Prompts must not depend on one another.

Example

Activity Prompt

↓

Output

↓

Application

↓

Memory Prompt

The application orchestrates prompts.

Prompts never chain themselves.

---

# 14. Prompt Engineering Principles

Prompt design follows these principles:

* Clarity over cleverness.
* Explicit instructions over implicit assumptions.
* Structured outputs over prose.
* Context minimization.
* Deterministic formatting.
* Version everything.
* Test every prompt.

Prompt quality is measured by reliability, not length.

# 15. Prompt Definition

Every prompt in LifeGraph is defined by two artifacts:

1. **Prompt Template** — the actual reasoning instructions.
2. **Prompt Definition** — metadata that describes how the prompt should be executed.

This separation allows prompts to evolve independently from execution logic.

---

## Prompt Definition Schema

Every prompt should define:

| Field           | Description                      |
| --------------- | -------------------------------- |
| name            | Unique prompt name               |
| version         | Prompt version                   |
| owner           | Intelligence service responsible |
| purpose         | Business objective               |
| input_schema    | Expected input model             |
| output_schema   | Expected output model            |
| model           | Default LLM                      |
| temperature     | Sampling configuration           |
| max_tokens      | Maximum output tokens            |
| timeout_seconds | Execution timeout                |
| retry_limit     | Maximum retries                  |

Example

```yaml id="0v1zdc"
name: activity
version: v1

owner:
ActivityIntelligenceService

input_schema:
ActivityContext

output_schema:
StructuredActivity

model:
llama-3.3-70b-versatile

temperature:
0.1

max_tokens:
400

retry_limit:
3
```

---

# 16. JSON Output Contract

The application should never parse free-form responses.

Every reasoning prompt should return JSON matching its schema.

Example

```json id="jlwmkk"
{
    "category":"Deep Work",
    "project":"LifeGraph",
    "confidence":0.95
}
```

Markdown is reserved exclusively for the Summary prompt.

---

# 17. Schema Enforcement

Every AI response passes through:

```text id="msfwgi"
LLM

↓

JSON Parser

↓

Pydantic Validation

↓

Business Validation

↓

Approved Proposal
```

Failures never bypass validation.

---

# 18. Few-Shot Example Policy

Few-shot examples should be used sparingly.

Include examples only when they materially improve consistency.

Guidelines:

* Maximum 3 examples.
* Prefer diverse examples.
* Avoid overfitting to a single wording style.
* Keep examples representative of real user input.

Example

Input

> Read research paper on LangGraph.

↓

Output

```json id="yjxjlwm"
{
    "category":"Learning",
    "project":null,
    "confidence":0.94
}
```

---

# 19. Hallucination Mitigation

The AI should prefer uncertainty over fabrication.

Rules:

* Never invent projects.
* Never invent memories.
* Never infer goals without evidence.
* Never create recommendations without supporting observations.

If information is missing:

Return

```json id="t8b0qk"
{
    "status":"insufficient_context"
}
```

rather than guessing.

---

# 20. Prompt Testing Strategy

Prompts are tested like software.

Every prompt should include:

* Positive test cases
* Edge cases
* Invalid inputs
* Empty inputs
* Ambiguous inputs

Example

| Input         | Expected Result  |
| ------------- | ---------------- |
| Worked on API | Deep Work        |
| Read paper    | Learning         |
| Lunch         | Personal         |
| ""            | Validation Error |

---

# 21. Prompt Evaluation Metrics

Each prompt should be evaluated using objective metrics.

Recommended metrics:

| Metric                  | Target     |
| ----------------------- | ---------- |
| JSON Validity           | 100%       |
| Schema Compliance       | >99%       |
| Confidence Availability | 100%       |
| Retry Rate              | <5%        |
| Average Latency         | <2 seconds |
| Hallucination Rate      | Near 0%    |

Prompt quality should be measurable.

---

# 22. Token Optimization

Prompt engineering should minimize unnecessary tokens.

Strategies:

* Retrieve only relevant context.
* Remove duplicated information.
* Avoid verbose instructions.
* Keep schemas concise.
* Trim historical context.

Lower token usage reduces latency and cost.

---

# 23. Model Routing

Different reasoning tasks may benefit from different models.

Recommended abstraction:

```text id="8k0f9y"
Reasoning Task

↓

Model Router

↓

Groq Provider

↓

Selected Model
```

Example policy:

| Task                   | Preferred Model             |
| ---------------------- | --------------------------- |
| Activity Understanding | Llama 3.3 70B               |
| Memory Proposal        | Llama 3.3 70B               |
| Behaviour Analysis     | Llama 3.3 70B               |
| Summary                | GPT-OSS 120B (if available) |

Routing logic should remain configurable.

---

# 24. Prompt Observability

Every prompt execution should emit telemetry.

Capture:

* Prompt name
* Version
* Model
* Latency
* Token usage
* Retry count
* Validation status
* Confidence
* Execution ID

This information enables prompt optimization over time.

---

# 25. Prompt Review Checklist

Before a prompt is approved:

* One responsibility?
* Clear objective?
* Minimal context?
* Structured output?
* Schema defined?
* Failure behavior defined?
* Version assigned?
* Test cases written?
* Validation implemented?

Prompts should undergo review just like production code.

---

# 26. Prompt Governance

Prompt changes must be intentional.

Every modification should include:

* Version increment
* Change summary
* Reason for change
* Expected impact

Avoid silent prompt edits.

---

# 27. Prompt Security

Prompts must never:

* Contain API keys.
* Leak internal architecture.
* Expose hidden system prompts.
* Request unnecessary personal data.

Sensitive values should always be injected through secure configuration.

---

# 28. Prompt Engineering Principles

LifeGraph treats prompts as engineering assets.

Every prompt should be:

* Small
* Focused
* Deterministic
* Explainable
* Versioned
* Observable
* Testable
* Provider independent

Prompt quality is achieved through disciplined engineering rather than increasingly complex instructions.

---

# 29. Prompt Contract Summary

The prompt layer exists to transform structured business context into structured reasoning proposals.

Its responsibilities end there.

The application remains responsible for:

* Validation
* Business rules
* Persistence
* Orchestration
* User-facing behavior

This separation keeps the AI layer reliable, maintainable, and easy to evolve as models and prompting techniques improve.
