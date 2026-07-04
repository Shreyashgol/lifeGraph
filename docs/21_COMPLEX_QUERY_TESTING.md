# Complex Query Testing Guide

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

**Status:** Manual / QA Testing Playbook

---

# 1. Purpose

This guide helps you exercise the **whole reasoning pipeline** with realistic,
complex natural-language inputs and verify the system behaves correctly.

It targets the **backend API directly** (curl), because that is deterministic and
needs no Google login. Every `POST /activity` runs the full graph:

```
Activity → Evaluation → Context → Memory → Timeline →
Behaviour → Insight → Recommendation → Summary → Reflection → Persist
```

so a single well-crafted activity touches every layer. The read endpoints then
let you inspect what was learned.

---

# 2. Prerequisites

1. Backend running and reachable:
   ```bash
   cd backend
   pip install -r requirements-dev.txt
   cp .env.example .env         # set GROQ_API_KEY (required for reasoning)
   uvicorn app.main:app --reload
   ```
2. A database configured via `DATABASE_URL` (SQLite is fine for testing; Neon
   Postgres for a production-like run).
3. `curl` and `jq` installed (`jq` just pretty-prints — optional).
4. Base URL (adjust if deployed):
   ```bash
   export API=http://localhost:8000
   ```

> **Note:** `POST /activity` requires a valid `GROQ_API_KEY`. Without it the
> endpoint returns **503** (`reasoning engine unavailable`). Read endpoints work
> without a key.

---

# 3. What each observable means

| Endpoint | Reflects |
| --- | --- |
| `POST /activity` → `activity` | The Activity node's structured parse + the Evaluation judge's `validated` flag |
| `POST /activity` → `errors` | Any node that degraded gracefully (e.g. `activity: insufficient_context`) |
| `GET /timeline` | Deterministic chronology (Timeline node) |
| `GET /memory` | Candidate/active memories (Memory node) |
| `GET /insights` / `/recommendations` | Read from the **latest** daily summary |
| `GET /summary` | The Summary node's Markdown narrative |

**Version 1 behaviours to keep in mind while testing** (by design, not bugs):

- **Memory stays `candidate`.** Memory is earned — a single observation usually
  yields `action: ignore`. Repeated evidence is needed before a memory appears,
  and candidate→active promotion across days is a deferred feature.
- **Summary runs on every activity.** `GET /summary` returns the *most recent*
  one; `insights`/`recommendations` read from it.
- **Single-tenant.** All data belongs to one profile (`GET /profile`).
- **Activity confidence floor is 0.6** (`MIN_ACTIVITY_CONFIDENCE`). Low-confidence
  parses may be retried by the Evaluation node (max 2) and can end `validated:false`.
- LLM output varies run-to-run — treat "expected" fields as *approximate*.

---

# 4. Conventions

Reusable helpers:

```bash
export API=http://localhost:8000

log() {  # log() "<activity text>"  [optional ISO timestamp]
  curl -s -X POST "$API/activity" -H "Content-Type: application/json" \
    -d "$(jq -n --arg a "$1" --arg t "${2:-}" \
          'if $t == "" then {activity:$a} else {activity:$a, timestamp:$t} end')" | jq
}
```

If you don't have `jq`, use the raw form:

```bash
curl -s -X POST "$API/activity" -H "Content-Type: application/json" \
  -d '{"activity":"Worked on the auth module for two hours"}'
```

---

# 5. Step 0 — Onboarding

Create the single-user profile first (personalizes reasoning):

```bash
curl -s -X POST "$API/onboarding" -H "Content-Type: application/json" -d '{
  "name": "Shreyash",
  "occupation": "AI Engineer",
  "timezone": "Asia/Kolkata",
  "goals": ["Build an AI startup", "Master agentic systems", "Ship LifeGraph v1"],
  "interests": ["Agentic AI", "Distributed systems"],
  "active_projects": ["LifeGraph", "G-Pilot"]
}' | jq
```

**Check:** `201`, and `GET /profile` returns the same profile.

**Negative:** an invalid IANA timezone must be rejected with **422**:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$API/onboarding" \
  -H "Content-Type: application/json" \
  -d '{"name":"A","occupation":"Eng","timezone":"Mars/Phobos","goals":["g"]}'
# expect: 422
```

---

# 6. Section A — Single complex activity parses

Each of these is one rich sentence. Verify the Activity node extracts the right
**category, project, duration, intent, people**, and that the Evaluation node
sets `validated`.

### A1 — Multi-clause deep work with a named entity

```bash
log "Spent about two hours this morning implementing the OAuth callback and token refresh for LifeGraph, mostly pairing with Aisha."
```

**Expect:** `category` ≈ Deep Work; `project` = `LifeGraph`; `duration` ≈ 120;
`intent` ≈ implementation; `people` includes `Aisha`; `validated: true`;
`confidence` ≥ 0.6.

### A2 — Learning / research, fuzzy duration

```bash
log "Read the LangGraph docs and two papers on agentic memory, then sketched our evaluation-service design — lost track of time, maybe 90 minutes."
```

**Expect:** `category` ≈ Learning (or Research); `duration` ≈ 90; project possibly
null or `LifeGraph`.

### A3 — Meeting with impact

```bash
log "Got pulled into a 45-minute incident bridge about the checkout outage, then debriefed with the platform team."
```

**Expect:** `category` ≈ Meeting; `duration` ≈ 45; `people`/entities may include
the team; intent ≈ incident/coordination.

### A4 — Personal / non-work

```bash
log "Went for a 30 minute run after lunch to reset."
```

**Expect:** `category` ≈ Personal/Health; `duration` ≈ 30; `project: null`.

### A5 — Compound input (multiple activities in one sentence)

```bash
log "Reviewed three pull requests, answered Slack for a bit, then spent the rest of the afternoon writing the memory-evaluation prompt."
```

**Expect:** the system still returns **one** structured activity (V1 stores one
observation per request) — usually the dominant one (prompt writing / Deep Work).
This documents current behaviour; multi-activity splitting is a future feature.

---

# 7. Section B — Ambiguity, edge cases & the Evaluation loop

### B1 — Empty input → request validation

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$API/activity" \
  -H "Content-Type: application/json" -d '{"activity":""}'
# expect: 422  (min_length on the request body, before the graph runs)
```

### B2 — Gibberish → insufficient context

```bash
log "asdkfj 12321 ;;;; ...."
```

**Expect:** `activity: null` and `errors` contains `activity: insufficient_context`.
The graph degrades gracefully rather than inventing data.

### B3 — Very low signal (ambiguous)

```bash
log "ugh, meetings all day"
```

**Expect:** either a low-confidence Meeting parse or `insufficient_context`. If
confidence is low, watch the backend logs for an **Evaluation retry** (see §11).

### B4 — Deliberately misleading category (exercises the judge)

```bash
log "Studied the codebase by rewriting the entire caching layer from scratch."
```

**Expect:** a naive parse might say Learning ("studied"), but the Evaluation judge
should push toward Deep Work (it's implementation). Inspect `evaluation_score` and,
in logs, any `retry_reason`. After at most **2** retries the pipeline continues.

### B5 — Very long input (robustness)

Paste a long, rambling paragraph (5–10 sentences). **Expect:** a valid single
structured activity, no crash, response within a few seconds.

---

# 8. Section C — Memory evolution (repeated evidence)

Memory is earned. Log the *same kind* of activity several times, then inspect
memory. Run these back-to-back:

```bash
log "Worked on the LifeGraph backend."
log "More LifeGraph backend work — wired up the graph nodes."
log "Spent the morning on LifeGraph again, mostly the persistence layer."
log "Back on LifeGraph: finished the API endpoints."
```

Then:

```bash
curl -s "$API/memory" | jq
```

**Check:** you may see a **candidate** memory such as a `project` memory for
`LifeGraph` or a `routine`/`behaviour` memory. Each memory shows `status`,
`confidence`, and `evidence_count`. It is **expected** that memory is sparse and
`candidate` — the system refuses to fabricate stable knowledge from thin evidence.

**Identity/preference probe:**

```bash
log "I always prototype in Python before touching anything else."
curl -s "$API/memory" | jq '.memories[] | {type, statement, status}'
```

**Expect:** possibly a `preference` candidate ("prefers Python"). A single strong
statement may or may not cross the bar — that is the point of the test.

---

# 9. Section D — A realistic full day (behaviour, insights, recommendations)

Behaviour patterns, insights and recommendations need **accumulated history**.
Seed a full day with timestamps, then read the analysis. Run this block as-is:

```bash
export API=http://localhost:8000
D=2026-07-04   # the test day

post() { curl -s -X POST "$API/activity" -H "Content-Type: application/json" \
  -d "{\"activity\":\"$1\",\"timestamp\":\"${D}T$2+00:00\"}" >/dev/null; echo "logged $2"; }

post "Deep work on the LifeGraph graph engine, wiring the evaluation node."      "03:30:00"
post "Deep work: implemented the retry edges and tested the routing logic."       "04:30:00"
post "Stand-up with the team, then triaged two bugs."                             "05:30:00"
post "Reviewed four pull requests and left detailed comments."                    "06:15:00"
post "Read a paper on LLM-as-a-judge evaluation."                                 "07:00:00"
post "Lunch and a short walk."                                                    "07:30:00"
post "Long meeting about the Q3 roadmap."                                         "08:30:00"
post "Context-switched a lot: Slack, email, a quick call, back to code."          "09:30:00"
post "Afternoon deep work on the persistence layer and Postgres migration."       "11:00:00"
post "Wrote documentation and the testing playbook."                             "12:30:00"
```

(These UTC times fall in a morning-heavy / afternoon pattern once converted; the
exact wall-clock isn't important — the *distribution* is.)

Now inspect the analysis (all read from the latest run over the accumulated day):

```bash
curl -s "$API/timeline?date=$D"        | jq '{activities: (.activities|length), total_duration, context_switches}'
curl -s "$API/insights"                | jq
curl -s "$API/recommendations"         | jq
curl -s "$API/summary"                 | jq '{date, overview, metrics, tomorrow_focus}'
```

**Check:**
- `timeline`: ~10 activities, non-zero `total_duration`, `context_switches` > 0
  (the "context-switched a lot" entry and category changes should register).
- `insights`: 0+ items; each has a `title`, `description`, `confidence`. It's
  acceptable to get an empty list if the model finds nothing well-supported.
- `recommendations`: 0+ items; each has `reason`, `expected_impact`, `priority`
  (Critical/High/Medium/Low) — and should be **specific**, not generic advice.
- `summary.overview`: a Markdown review referencing the day; `metrics` includes
  `total_duration` and `activities`.

---

# 10. Section E — Endpoint verification matrix

| Request | Expect |
| --- | --- |
| `GET /health` | `200`, `{"status":"ok", ...}` |
| `POST /onboarding` (valid) | `201`, profile echoed |
| `POST /onboarding` (bad timezone) | `422` |
| `GET /profile` (before onboarding) | `404` |
| `GET /profile` (after) | `200` |
| `POST /activity` (valid) | `200`, `activity` populated, `timeline_updated: true` |
| `POST /activity` (empty) | `422` |
| `POST /activity` (no GROQ key) | `503` |
| `GET /timeline` (empty day) | `200`, `activities: []` |
| `GET /timeline?date=YYYY-MM-DD` | `200`, that day's activities |
| `GET /memory` | `200`, `{memories, count}` |
| `GET /insights` / `/recommendations` | `200`, `{..., count}` |
| `GET /summary` (none yet) | `404` |
| `GET /summary` (after activity) | `200`, Markdown `overview` |

Quick status-code sweep:

```bash
for p in /health /profile /timeline /memory /insights /recommendations /summary; do
  printf "%-18s %s\n" "$p" "$(curl -s -o /dev/null -w '%{http_code}' "$API$p")"
done
```

---

# 11. Section F — Observability checks

While running the tests, watch the backend logs (structured JSON). For each
activity you should be able to confirm:

- **Node execution** across the pipeline (`app.graph.nodes.*`).
- **Evaluation retries**: look for `intelligence_retry` or the activity's
  `retry_count` climbing (max 2) and an `evaluation_reason` on retried parses.
- **Prompt rendering**: `prompt_rendered` with `prompt_name` / `prompt_version`.
- **Graceful degradation**: any `errors[]` in the response instead of a 500.

To force a visible retry, use an input whose category is genuinely ambiguous
(B4) and inspect the response:

```bash
log "Studied the codebase by rewriting the entire caching layer from scratch." \
  | jq '.activity | {category, validated, evaluation_score}'
```

---

# 12. Section G — Reset between runs

SQLite: stop the server and delete the DB file referenced by `DATABASE_URL`
(e.g. `rm backend/lifegraph.db`), then restart — `init_db()` recreates the schema.

Postgres/Neon: truncate the tables (`users, activities, memories, timelines,
summaries`) or drop and let `init_db()` recreate them.

---

# 13. Pass / fail summary

A test session **passes** when:

- Complex, multi-clause activities are parsed into sensible structured fields.
- Gibberish and empty inputs are rejected/flagged, never fabricated.
- The Evaluation loop retries ambiguous parses and always terminates (≤ 2).
- Repeated evidence produces (candidate) memories; single observations usually do not.
- A seeded day yields a timeline, and a summary with evidence-backed insights and
  personalized, non-generic recommendations.
- Every endpoint returns the status codes in §10, and no request causes a 500.

The goal is not perfect model output on every run — it is that the **system**
behaves predictably, explains itself, and degrades gracefully under complex and
adversarial input.
