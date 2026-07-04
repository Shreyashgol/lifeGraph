# Technology Stack

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Version:** 1.0

**Status:** Engineering Decision Record (ADR)

---

# Purpose

This document explains the technology choices for Version 1 of LifeGraph.

The objective is not to choose the "most powerful" technologies.

The objective is to choose technologies that maximize:

* Development speed
* Engineering quality
* AI capabilities
* Maintainability
* Free-tier deployment
* Future scalability

Every technology in this document has been selected intentionally.

---

# Technology Selection Principles

The stack should satisfy the following principles:

* AI-first
* Modular
* Easy to deploy
* Low operational overhead
* Production-friendly
* Replaceable components
* Excellent developer experience

---

# High-Level Stack

```text
Frontend
Next.js + Tailwind + shadcn/ui

↓

Backend API
FastAPI

↓

AI Orchestration
LangGraph

↓

Reasoning Services

↓

Groq API

↓

Persistence
SQLite + SQLModel

↓

Deployment
Render + Vercel
```

---

# Backend

## Python 3.12+

### Why

Python provides the strongest AI ecosystem.

Advantages:

* Mature AI libraries
* Excellent typing support
* Fast development
* Large community
* Easy integration with LangGraph

---

## Why not Node.js?

Node.js is excellent for APIs.

However, LifeGraph is fundamentally an AI system.

Python offers significantly better support for:

* LangGraph
* LLM tooling
* Pydantic
* Scientific libraries
* AI workflows

---

# API Framework

## FastAPI

Purpose

Expose backend services.

Responsibilities

* Activity endpoint
* Timeline endpoint
* Summary endpoint
* Memory endpoint
* Health endpoint

---

## Advantages

* High performance
* Automatic OpenAPI documentation
* Native async support
* Excellent Pydantic integration
* Strong typing

---

## Why not Flask?

Flask requires additional tooling for:

* Validation
* Documentation
* Type safety

FastAPI includes these capabilities by default.

---

# AI Orchestration

## LangGraph

Purpose

Acts as the execution engine of LifeGraph.

LangGraph is not used because it is popular.

It is used because the product naturally follows a graph.

---

## Responsibilities

* Workflow orchestration
* Shared state
* Conditional routing
* Checkpointing
* Retry handling
* Future human-in-the-loop support

---

## Graph Structure

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

END
```

---

## Why LangGraph?

Without LangGraph

```text
User

↓

Huge Prompt

↓

Response
```

With LangGraph

```text
State

↓

Specialized Nodes

↓

Shared Reasoning

↓

Structured Output
```

The second approach is:

* More maintainable
* Easier to test
* Easier to extend
* Easier to debug

---

# LLM Provider

## Groq API

Purpose

Perform all AI reasoning.

Recommended Models

* llama-3.3-70b-versatile
* qwen/qwen3-32b
* openai/gpt-oss-120b (when available)

---

## Responsibilities

* Activity understanding
* Memory proposal
* Behaviour reasoning
* Insight generation
* Recommendation generation
* Summary generation

---

## Why Groq?

Advantages

* Extremely low latency
* Excellent structured output
* OpenAI-compatible API
* Free developer tier
* Fast iteration during development

---

## Why not OpenAI?

OpenAI is excellent.

However:

* Higher cost
* More restrictive free usage
* Groq provides faster inference for this prototype

The architecture keeps the provider replaceable.

---

# AI Client Architecture

Nodes never call Groq directly.

Instead:

```text
Node

↓

Intelligence Service

↓

Groq Client

↓

Validated Response

↓

Node
```

Examples

* ActivityIntelligenceService
* MemoryIntelligenceService
* BehaviourIntelligenceService
* SummaryIntelligenceService

This isolates provider-specific logic.

---

# Validation

## Pydantic v2

Purpose

Ensure every AI response is valid before entering the application.

Responsibilities

* JSON validation
* Type validation
* Schema validation
* Configuration models

---

## Why?

LLMs are probabilistic.

The application should be deterministic.

Pydantic bridges this gap.

---

# Database

> **Update:** Version 1 targets **Neon Postgres + pgvector** (pulled forward from
> the original V2 plan) for durable, serverless persistence and semantic-memory
> embeddings. The engine is dialect-agnostic (`DATABASE_URL`), so **SQLite** is
> retained for local development and the test suite. Sections below describe the
> original SQLite rationale, which still applies to the local/test path.

## SQLite

Stores

* Users
* Activities
* Timeline
* Memories
* Insights
* Recommendations
* Daily Summaries

---

## Why SQLite?

Advantages

* Zero configuration
* Portable
* Lightweight
* Free
* Render compatible
* Perfect for MVP

---

## Future Upgrade

Version 2

↓

PostgreSQL

No architecture changes required.

---

# ORM

## SQLModel

Purpose

Database abstraction.

Advantages

* SQLAlchemy based
* Pydantic compatible
* Strong typing
* Clean syntax

---

# Frontend

> **Update:** The frontend is a **React + Vite** single-page app (not Next.js).
> Routing uses `react-router-dom`; authentication uses Google OAuth via
> `@react-oauth/google` (client-side, login-gated single-tenant); theming uses a
> small custom context. Tailwind CSS + shadcn/ui are unchanged. The
> responsibilities below still apply.

## React + Vite

Responsibilities

* Dashboard
* Activity logging
* Timeline
* Memory
* Summary
* Insights

---

## Why Next.js?

Advantages

* React ecosystem
* Server Components
* Excellent deployment
* Vercel integration
* TypeScript support

---

# UI

## Tailwind CSS

Advantages

* Rapid development
* Utility-first
* Easy consistency
* Small bundle

---

## shadcn/ui

Advantages

* Accessible
* Modern
* Customizable
* Excellent developer experience

---

# Configuration

## python-dotenv

Purpose

Manage:

* GROQ_API_KEY
* DATABASE_URL
* ENVIRONMENT
* MODEL_NAME

Secrets are never committed.

---

# Logging

Python logging

Log

* Node execution
* Prompt version
* Latency
* Confidence
* Errors

Structured logs simplify debugging.

---

# Testing

## pytest

Responsibilities

* Unit testing
* Integration testing
* Graph testing
* Prompt validation

---

# Version Control

## Git

Repository hosted on GitHub.

Recommended branching strategy:

* main
* feature/*
* fix/*
* docs/*

---

# Deployment

## Backend

Platform

Render Free Tier

Runs

* FastAPI
* LangGraph
* SQLite

---

## Frontend

Platform

Vercel Free Tier

Runs

* Next.js
* Tailwind
* shadcn/ui

---

# CI/CD (Future)

Recommended

GitHub Actions

Pipeline

* Install
* Lint
* Test
* Build
* Deploy

Not required for Version 1.

---

# Repository Layout

```text
backend/
├── app/
│   ├── api/
│   ├── config/
│   ├── graph/
│   ├── intelligence/
│   ├── prompts/
│   ├── models/
│   ├── database/
│   ├── services/
│   └── utils/
└── tests/

frontend/

docs/
```

The Python backend lives under `backend/`, sibling to `frontend/`. Within the
backend, organize by business capability, not by technology.

---

# Future Evolution

## Version 2

* PostgreSQL
* Authentication
* Background jobs

---

## Version 3

* Redis
* Calendar integration
* Browser extension
* Voice logging

---

## Version 4

* AI Coach
* Predictive planning
* Autonomous scheduling
* Team intelligence

The architecture is intentionally designed so these upgrades require minimal structural change.

---

# Technology Decision Summary

| Layer           | Technology   | Reason                            |
| --------------- | ------------ | --------------------------------- |
| Language        | Python 3.12+ | AI ecosystem                      |
| API             | FastAPI      | Typed, async, OpenAPI             |
| Orchestration   | LangGraph    | Shared state & workflows          |
| LLM             | Groq API     | Low latency, structured reasoning |
| Validation      | Pydantic v2  | Deterministic schemas             |
| ORM             | SQLModel     | Typed persistence                 |
| Database        | SQLite       | Lightweight MVP                   |
| Frontend        | Next.js      | Modern React framework            |
| Styling         | Tailwind CSS | Fast UI development               |
| Components      | shadcn/ui    | Accessible, reusable UI           |
| Testing         | pytest       | Standard Python testing           |
| Backend Deploy  | Render       | Free-tier hosting                 |
| Frontend Deploy | Vercel       | Free-tier hosting                 |

---

# Final Decision

The chosen stack optimizes for rapid development without sacrificing engineering quality.

It demonstrates:

* Modern AI architecture
* Clean software engineering
* Low operational complexity
* Free-tier deployment
* Straightforward migration to production

The technologies are tools.

The architecture is the product.
