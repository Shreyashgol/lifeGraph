# LifeGraph Frontend

React + Vite + TypeScript + Tailwind CSS + shadcn/ui, with **light/dark theming**
(custom context) and **Google OAuth** (`@react-oauth/google`).

A single-page app that talks to the FastAPI backend over REST.

## Setup

```bash
cd frontend
npm install
cp .env.example .env        # fill in the values below
npm run dev                 # http://localhost:5173
```

### Environment (`VITE_`-prefixed — client-exposed)

| Variable                | Purpose                                              |
| ----------------------- | ---------------------------------------------------- |
| `VITE_API_URL`          | Base URL of the FastAPI backend                      |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth 2.0 Web client ID                       |
| `VITE_ALLOWED_EMAILS`   | Optional comma-separated allowlist (single-tenant)   |

**Google Cloud setup:** create an OAuth 2.0 Client (type: Web) and add this app's
origin `http://localhost:5173` as an **Authorized JavaScript origin** (client-side
Google Identity Services — no redirect URI needed).

## Auth & theming

- **Auth**: `@react-oauth/google` performs the client-side Google sign-in on
  `/login`. The returned ID token is decoded (`jwt-decode`) into a session stored
  in `localStorage` (`contexts/auth-context.tsx`). `components/protected-route.tsx`
  gates every app route; unauthenticated users are redirected to `/login`. Version
  1 is **login-gated single-tenant** — any Google account (or an allowlist)
  accesses the one dataset.
- **Theme**: `contexts/theme-context.tsx` toggles the `dark` class on `<html>`,
  persists to `localStorage`, and respects the system preference on first load.
  The toggle lives in the header (`components/theme-toggle.tsx`).

## Structure

```
index.html
vite.config.ts
src/
├── main.tsx                # entry: Google + Theme + Auth providers, router
├── App.tsx                 # routes
├── index.css               # Tailwind + theme CSS variables
├── contexts/               # theme-context, auth-context
├── components/             # app-shell, theme-toggle, protected-route, states, ui/
├── pages/                  # login, dashboard, activity, timeline,
│                           # memory, insights, summary, onboarding
└── lib/                    # api client, types, useApi hook, utils
```

## Scripts

| Command           | Description                     |
| ----------------- | ------------------------------- |
| `npm run dev`     | Vite dev server (port 5173)     |
| `npm run build`   | Type-check + production build   |
| `npm run preview` | Serve the production build      |
