# Product Requirements Document (PRD)

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Approved for Implementation

---

# 1. Purpose

This document defines the functional, non-functional, and engineering requirements for Version 1 of LifeGraph.

It serves as the contract between Product, Engineering, and AI Architecture.

Any implementation should satisfy these requirements before being considered complete.

---

# 2. Product Goal

Create an AI-powered Personal Intelligence Engine capable of:

* Understanding natural language activities.
* Building an evolving user profile.
* Detecting behavioral patterns.
* Generating explainable insights.
* Producing personalized recommendations.
* Creating an end-of-day intelligence report.

---

# 3. Target Users

Version 1 targets knowledge workers.

Examples:

* Software Engineers
* AI Engineers
* Students
* Researchers
* Startup Founders
* Product Managers

---

# 4. User Journey

## Step 1

User launches LifeGraph.

↓

## Step 2

Completes onboarding.

↓

## Step 3

Logs activities naturally.

Example:

> Worked on authentication for two hours.

↓

## Step 4

AI understands the activity.

↓

## Step 5

Timeline updates.

↓

## Step 6

Memory evaluates whether new knowledge should be stored.

↓

## Step 7

Behavioral patterns evolve.

↓

## Step 8

User requests a daily report.

↓

## Step 9

LifeGraph generates:

* Summary
* Insights
* Recommendations

---

# 5. Functional Requirements

## FR-1 User Onboarding

The system shall allow users to initialize a personal profile.

Information may include:

* Name
* Occupation
* Timezone
* Primary goals
* Current projects
* Interests

Acceptance Criteria

* Profile successfully created.
* Information persisted.
* Profile retrievable.

---

## FR-2 Activity Logging

The system shall accept activities in natural language.

Examples:

* Worked on backend API.
* Read AI research paper.
* Exercised for one hour.
* Attended sprint meeting.

Acceptance Criteria

* Activity stored successfully.
* Timestamp automatically generated.
* Activity linked to the current day.

---

## FR-3 Activity Understanding

The AI shall convert natural language into structured information.

Required outputs include:

* Activity Type
* Category
* Intent
* Duration
* Project
* Confidence

Acceptance Criteria

* Valid structured response.
* Schema validation passes.
* Confidence score generated.

---

## FR-4 Context Retrieval

Before reasoning, the system shall retrieve only relevant user context.

Examples:

* Goals
* Active projects
* Recent activities
* Stable preferences

Acceptance Criteria

* No unrelated memories retrieved.
* Context limited to the current activity.

---

## FR-5 Timeline Management

Maintain a chronological history of user activities.

Capabilities:

* Store activities.
* Sort chronologically.
* Group activities into sessions.
* Calculate durations.

Acceptance Criteria

* Timeline reconstructs the user's day accurately.

---

## FR-6 Memory Intelligence

The system shall determine whether an activity contributes to long-term memory.

Memory Categories:

* Identity
* Goals
* Projects
* Behavior
* Routine
* Interests
* Preferences

Rules

* One activity does not create permanent memory.
* Repeated evidence strengthens confidence.

Acceptance Criteria

* Memory updates include evidence and confidence.

---

## FR-7 Behaviour Intelligence

The system shall analyze accumulated activities and identify behavioral patterns.

Examples:

* Deep work frequency
* Preferred work hours
* Context switching
* Learning consistency

Acceptance Criteria

* Patterns supported by historical evidence.

---

## FR-8 Insight Generation

Generate explainable observations.

Examples:

* Coding time increased.
* Focus sessions became longer.
* Meetings interrupted deep work.

Acceptance Criteria

* Every insight references evidence.

---

## FR-9 Recommendation Generation

Generate personalized recommendations.

Each recommendation shall include:

* Recommendation
* Reason
* Priority
* Expected Impact

Acceptance Criteria

* Recommendations derived from user-specific data.
* No generic productivity advice.

---

## FR-10 Daily Summary

Generate an end-of-day report containing:

* Overview
* Time Allocation
* Timeline
* Behavioral Analysis
* Insights
* Recommendations
* Reflection
* Tomorrow's Focus

Acceptance Criteria

* Summary references validated information only.

---

# 6. AI Requirements

The AI system shall:

* Produce structured outputs.
* Report confidence.
* Avoid hallucinations.
* Never invent user data.
* Support retries.
* Validate responses before use.

Every AI module should have exactly one responsibility.

---

# 7. Memory Requirements

Memory shall:

* Persist across sessions.
* Be evidence-based.
* Store confidence.
* Track supporting activities.
* Record timestamps.

Memory should never be updated solely from a single observation.

---

# 8. Graph Requirements

LangGraph shall orchestrate execution.

Required nodes:

* ActivityNode
* ContextNode
* MemoryNode
* TimelineNode
* BehaviourNode
* InsightNode
* RecommendationNode
* SummaryNode
* ReflectionNode

Each node receives Graph State and returns updated Graph State.

---

# 9. Storage Requirements

SQLite stores:

* Users
* Activities
* Timeline
* Memories
* Insights
* Recommendations
* Daily Summaries

Prompt logs and execution metadata may be stored as JSON.

---

# 10. API Requirements

Minimum endpoints:

POST /activity

GET /timeline

GET /memory

GET /summary

GET /insights

GET /recommendations

GET /health

---

# 11. Frontend Requirements

Version 1 interface shall provide:

* Dashboard
* Activity Logging
* Timeline View
* Memory View
* Summary View
* Insights View

The interface should prioritize clarity over feature density.

---

# 12. Security Requirements

Version 1 should:

* Use environment variables for secrets.
* Never expose API keys.
* Validate all incoming requests.
* Sanitize user input.

**Update:** Authentication is now in scope for Version 1 as **login-gated
single-tenant** — Google OAuth (NextAuth / Auth.js) gates the frontend. The
backend stays single-user; per-user data isolation (multi-tenant) is deferred.

---

# 13. Performance Requirements

Target metrics:

* Activity understanding: < 3 seconds
* Summary generation: < 8 seconds
* Timeline retrieval: < 500 ms
* API startup: < 10 seconds

These are development targets rather than strict production SLAs.

---

# 14. Reliability Requirements

The application should:

* Handle malformed AI responses.
* Retry failed AI requests.
* Continue execution where possible.
* Avoid application crashes.
* Produce meaningful error messages.

---

# 15. Maintainability Requirements

Code should:

* Follow SOLID principles.
* Use dependency injection where appropriate.
* Include type hints.
* Include docstrings for public interfaces.
* Avoid duplicated logic.
* Keep modules focused.

---

# 16. Deployment Requirements

Backend:

* FastAPI
* Render Free Tier

Frontend:

* Next.js
* Vercel Free Tier

Configuration through environment variables.

---

# 17. Out of Scope

The following are intentionally excluded from Version 1:

* Authentication
* Multi-user support
* Calendar synchronization
* Browser extension
* Email integration
* Voice assistant
* Mobile application
* Autonomous task execution
* Team collaboration

These remain candidates for future versions.

---

# 18. Acceptance Criteria

Version 1 is complete when:

* User onboarding works.
* Natural language activities are understood.
* Timeline updates correctly.
* Memory evolves using evidence.
* Behavioral patterns are generated.
* Personalized insights are produced.
* Recommendations include reasons.
* Daily summaries are generated.
* Backend deploys successfully on Render.
* Frontend deploys successfully on Vercel.
* Documentation is complete.
* Tests pass.

---

# 19. Definition of Success

LifeGraph succeeds if a new user can spend an entire day logging activities and receive a personalized report that demonstrates:

* Accurate activity understanding.
* Persistent learning.
* Explainable reasoning.
* Actionable recommendations.
* A noticeably deeper understanding of their work than a traditional activity tracker.

The primary success metric is not the number of implemented features.

The primary success metric is the quality of the personalized intelligence produced by the system.
