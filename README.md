# LifeGraph

**AI-Powered Personal Intelligence Engine.**

LifeGraph transforms natural-language activity logs into an evolving, evidence-backed
understanding of how a user works, learns, and decides — producing explainable
insights and personalized recommendations rather than raw activity statistics.

> The LLM reasons. The application decides.

See [`docs/`](docs/) for the full engineering specification. `docs/13_MASTER_IMPLEMENTATION_SPEC.md`
is the source of truth; `docs/12_IMPLEMENTATION_PHASES.md` defines the build order.

## Tech stack

| Layer         | Technology                                   |
| ------------- | -------------------------------------------- |
| Frontend      | Next.js (App Router), Tailwind CSS, shadcn/ui |
| API           | FastAPI                                       |
| Orchestration | LangGraph                                     |
| Reasoning     | Groq (provider-independent)                   |
| Validation    | Pydantic v2                                   |
| Persistence   | SQLModel · Neon Postgres + pgvector (SQLite for local/tests) |

## Repository layout

```
backend/
├── app/
│   ├── api/            # REST routers (thin)
│   ├── config/         # settings, logging, constants
│   ├── graph/          # LangGraph engine: state, nodes, edges, builder, checkpointer
│   ├── intelligence/   # AI reasoning services (one task each)
│   ├── prompts/        # versioned prompt definitions, templates, tests
│   ├── repositories/   # persistence (CRUD)
│   ├── database/       # SQLModel entities, session
│   ├── schemas/        # API request/response DTOs
│   ├── models/         # domain models
│   ├── validators/     # business validation & proposal approval
│   ├── services/       # deterministic (non-AI) services
│   ├── observability/  # logging, metrics, telemetry
│   ├── utils/          # generic helpers
│   └── main.py         # FastAPI entrypoint
├── tests/              # pytest suite
├── pyproject.toml
└── requirements.txt
frontend/               # Next.js app
docs/                   # engineering specification
docker/  scripts/  deployment/
```

Dependencies flow downward only: `api → graph → intelligence → validators → repositories → database`.

## Getting started

### Backend

Requires Python 3.12+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # fill in values (GROQ_API_KEY optional in Phase 1)
uvicorn app.main:app --reload   # http://localhost:8000
```

Verify: `curl http://localhost:8000/health` → `{"status":"ok",...}`.
Interactive docs: http://localhost:8000/docs.

### Frontend

Requires Node.js 18+.

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                     # http://localhost:3000
```

### Tests

```bash
cd backend && pytest
```

## Implementation status

| Phase | Objective          | Status         |
| ----- | ------------------ | -------------- |
| 1     | Project Foundation | ✅ Complete     |
| 2     | Domain Models      | ✅ Complete     |
| 3     | Persistence Layer  | ✅ Complete     |
| 4     | Prompt System      | ✅ Complete     |
| 5     | AI Layer           | ✅ Complete     |
| 6     | Graph Engine       | ✅ Complete     |
| 7     | API Layer          | ✅ Complete     |
| 8     | Frontend           | ✅ Complete     |
| 9     | Testing            | ⬜ Not started  |
| 10    | Deployment         | ⬜ Not started  |
