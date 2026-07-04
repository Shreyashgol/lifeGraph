# Testing Strategy

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

---

# 1. Principles

- **Deterministic tests.** No test ever calls a live LLM or a real database. AI
  is exercised through a mocked ``LLMClient``; persistence through in-memory
  SQLite. Tests run offline, fast, and reproducibly.
- **Test the system, not the model.** We assert the pipeline's behaviour
  (validation, retries, state transitions, graceful degradation), not the exact
  wording an LLM returns.

---

# 2. Test pyramid (backend, `pytest`)

Run: `cd backend && pytest -q` (add `--cov=app --cov-report=term-missing` for coverage).

| Suite | File | Covers |
| --- | --- | --- |
| Domain models | `tests/test_models.py` | Validation rules, serialization for every model |
| Graph state | `tests/test_state.py` | `LifeGraphState`, `model_copy` updates, ownership |
| Repositories | `tests/test_repositories.py` | CRUD, filters, the memory accumulator (candidate→active) |
| Prompt system | `tests/test_prompts.py` | Registry load, rendering, variable validation, versioning |
| Intelligence | `tests/test_intelligence.py` | Proposal parsing, JSON extraction, **retry logic**, insufficient-context |
| Graph | `tests/test_graph.py` | Node behaviour, evaluation retry routing, both compiled graphs end-to-end |
| API | `tests/test_api.py` | Endpoint validation, status codes, wiring (via a fake graph) |

- **Async** tests use `pytest-asyncio` (`asyncio_mode = "auto"`).
- **Graph** tests build the compiled graphs with a keyword-routing fake client and
  an in-memory database; the full-graph tests are skipped if `langgraph` is absent
  (`pytest.importorskip`).

---

# 3. What is intentionally mocked

- **LLM provider** — a fake `LLMClient` returns canned JSON/text (and can queue
  exceptions to exercise retries). Never Groq.
- **Database** — in-memory SQLite (`StaticPool`), schema created per test.
- **Compiled graph** (in API tests) — a `FakeGraph` returns an enriched state, so
  API tests validate wiring without langgraph/Groq.

---

# 4. Manual / integration testing

`docs/21_COMPLEX_QUERY_TESTING.md` is the runnable playbook for exercising the
**live** system (real Groq + database) with complex natural-language queries:
onboarding, complex parses, the evaluation judge, memory accumulation, on-demand
summary generation, and the endpoint matrix.

---

# 5. Continuous integration

`.github/workflows/ci.yml` runs on push/PR to `main`:

- **backend** — `ruff check` + `pytest --cov` (no secrets; SQLite + mocked LLM).
- **frontend** — `npm ci` + `npm run build`.

---

# 6. Coverage

Coverage is measured over `app/` (prompt templates/definitions excluded). Target:
keep the core layers — models, validators, repositories, intelligence services,
graph nodes — well covered; UI-glue and provider I/O (the Groq client) are
exercised by the manual playbook rather than unit tests.
