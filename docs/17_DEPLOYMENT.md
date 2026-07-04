# Deployment

## Project

**LifeGraph — AI-Powered Personal Intelligence Engine**

Backend → **Render**  ·  Frontend → **Vercel**  ·  Database → **Neon Postgres + pgvector**

---

# 1. Prerequisites

- A **Neon** Postgres database (free tier) — copy its connection string.
- A **Groq** API key.
- A **Google Cloud** OAuth 2.0 Web client (for frontend sign-in).
- The repository pushed to GitHub.

---

# 2. Database (Neon)

1. Create a Neon project; copy the connection string
   (`postgresql://user:pass@host/db?sslmode=require`).
2. No manual migration is needed — on first backend start, `init_db()` enables
   the `vector` extension and creates the tables. The URL scheme is normalized to
   the psycopg v3 driver automatically.

---

# 3. Backend (Render)

Using the included **`render.yaml`** Blueprint (repo root):

1. Render → **New → Blueprint** → select the repo. Render reads `render.yaml`
   (service `lifegraph-backend`, root `backend/`, health check `/health`).
2. Set the secret env vars in the dashboard (they are `sync: false`):
   - `GROQ_API_KEY`
   - `DATABASE_URL` — the Neon string
   - `CORS_ORIGINS` — JSON array incl. the Vercel URL, e.g.
     `["https://your-app.vercel.app"]`
3. Deploy. Verify: `curl https://<backend>.onrender.com/health` → `{"status":"ok"}`.

**Manual (no Blueprint):** New Web Service → root `backend` →
build `pip install -r requirements.txt` →
start `uvicorn app.main:app --host 0.0.0.0 --port $PORT` → health path `/health` →
same env vars. A **`backend/Dockerfile`** is also provided if you prefer a
container deploy.

> Free-tier note: SQLite would be ephemeral on Render, but LifeGraph uses Neon,
> so data persists across restarts/sleeps.

---

# 4. Frontend (Vercel)

Included **`frontend/vercel.json`** sets the Vite framework, `dist` output, and
SPA rewrites (so client-side routes resolve to `index.html`).

1. Vercel → **New Project** → import the repo → set **Root Directory = `frontend`**.
2. Environment variables:
   - `VITE_API_URL` — the Render backend URL (`https://<backend>.onrender.com`)
   - `VITE_GOOGLE_CLIENT_ID` — the Google OAuth Web client ID
   - `VITE_ALLOWED_EMAILS` — optional single-tenant allowlist
3. Deploy.

---

# 5. Google OAuth (production origins)

In the Google Cloud OAuth client, add the Vercel URL as an **Authorized
JavaScript origin** (client-side Google Identity Services needs the origin, not a
redirect URI):

```
https://your-app.vercel.app
```

---

# 6. Wire the two together

1. Set the frontend's `VITE_API_URL` to the backend URL and redeploy.
2. Set the backend's `CORS_ORIGINS` to include the Vercel URL and redeploy.
3. If they mismatch, the browser blocks requests with a CORS error.

---

# 7. Post-deploy verification

- `GET /health` on the backend → `200`.
- Frontend loads, Google sign-in succeeds, and onboarding saves a profile.
- `POST /activity` returns a structured activity (confirms Groq + DB).
- `POST /summary` generates a report (confirms the on-demand analysis graph).
- See `docs/21_COMPLEX_QUERY_TESTING.md` for a fuller end-to-end pass.

---

# 8. Environment variable reference

| Service  | Variable | Purpose |
| -------- | -------- | ------- |
| Backend  | `GROQ_API_KEY` | LLM reasoning |
| Backend  | `DATABASE_URL` | Neon Postgres connection string |
| Backend  | `CORS_ORIGINS` | JSON array of allowed frontend origins |
| Backend  | `ENVIRONMENT` | `production` |
| Backend  | `MODEL_NAME` | Default Groq model |
| Frontend | `VITE_API_URL` | Backend base URL |
| Frontend | `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |
| Frontend | `VITE_ALLOWED_EMAILS` | Optional single-tenant allowlist |

Secrets are configured in the Render/Vercel dashboards and are never committed.
