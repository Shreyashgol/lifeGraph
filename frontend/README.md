# LifeGraph Frontend

Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui, with **light/dark
theming** (`next-themes`) and **Google OAuth** (NextAuth / Auth.js v5).

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local   # fill in the values below
npm run dev                         # http://localhost:3000
```

### Environment

| Variable                | Purpose                                             |
| ----------------------- | --------------------------------------------------- |
| `NEXT_PUBLIC_API_URL`   | Base URL of the FastAPI backend                     |
| `NEXTAUTH_SECRET`       | `openssl rand -base64 32`                           |
| `NEXTAUTH_URL`          | This app's base URL (e.g. `http://localhost:3000`)  |
| `GOOGLE_CLIENT_ID`      | Google Cloud OAuth 2.0 client ID                    |
| `GOOGLE_CLIENT_SECRET`  | Google Cloud OAuth 2.0 client secret                |
| `AUTH_ALLOWED_EMAILS`   | Optional comma-separated allowlist (single-tenant)  |

**Google Cloud setup:** create an OAuth 2.0 Client (type: Web) and add the
authorized redirect URI `http://localhost:3000/api/auth/callback/google`.

> If `npm install` cannot resolve `next-auth@^5.0.0-beta.25`, run
> `npm install next-auth@beta`.

## Auth & theming

- **Auth**: `src/auth.ts` (Auth.js config) + `src/middleware.ts` gate every route
  except `/login`. Unauthenticated users are redirected to a Google sign-in page.
  Version 1 is **login-gated single-tenant**: any Google account (or an allowlist)
  accesses the one dataset.
- **Theme**: `next-themes` (class strategy) drives the CSS variables in
  `globals.css`; the toggle lives in the header (`components/theme-toggle.tsx`).

## Structure

```
src/
├── auth.ts                 # NextAuth (Auth.js v5) config
├── middleware.ts           # route protection
├── app/
│   ├── login/              # Google sign-in
│   ├── api/auth/[...nextauth]/route.ts
│   └── (app)/              # protected app shell + pages
│       ├── dashboard/  activity/  timeline/
│       ├── memory/  insights/  summary/  onboarding/
├── components/             # app-shell, theme-toggle, providers, ui/
└── lib/                    # api client, types, useApi hook
```

## Scripts

| Command         | Description                    |
| --------------- | ------------------------------ |
| `npm run dev`   | Dev server                     |
| `npm run build` | Production build               |
| `npm run start` | Serve the production build     |
| `npm run lint`  | Lint with `eslint-config-next` |
