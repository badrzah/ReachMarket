# ReachGTM — Deployment Guide

## Prerequisites

- Node.js 22+
- `wrangler` CLI (included as dev dependency)
- Cloudflare account
- **Backend**: Python 3.11+ + PostgreSQL + Redis (hosted separately, e.g. Railway, Render, Fly.io, or a VPS)

---

## Architecture

```
┌─────────────┐     HTTPS      ┌──────────────────┐    HTTP    ┌──────────────────┐
│  Cloudflare  │ ─────────────► │  FastAPI Backend  │ ─────────► │  FastAPI Agents  │
│  Workers     │ ◄── SSE ─────  │  :8000            │           │  LangGraph :8001  │
│  (OpenNext)  │                └──────────────────┘           └──────────────────┘
└─────────────┘                        │                               │
                                   asyncpg pool                    asyncpg pool
                                        │                               │
                               ┌─────────────────┐         ┌──────────────────────┐
                               │  PostgreSQL 16   │         │  Redis 7             │
                               │  + pgvector      │         │  (rate limit, cache) │
                               │  HNSW index      │         └──────────────────────┘
                               └─────────────────┘
```

**Frontend**: Deployed to Cloudflare Workers via OpenNext (Cloudflare adapter)
**Backend/Agents/DB**: Hosted on your provider of choice (Railway, Render, AWS, VPS)

---

## Local Development

```bash
# 1. Enter the repo
cd ReachGTM

# 2. Copy and fill environment
cp .env.example .env
# Required: OPENAI_API_KEY, JWT_SECRET (any random 32-char string)
# Optional: LANGSMITH_API_KEY, PERPLEXITY_API_KEY

# 3. Start backend services
docker compose -f infra/docker-compose.yml up --build

# 4. Start frontend dev server (separate terminal)
cd frontend
npm run dev

# 5. Verify health
curl http://localhost:8000/health   # {"service":"backend","status":"ok"}
curl http://localhost:3000          # HTML
```

---

## Cloudflare Deployment (Frontend)

### One-time setup

1. **Install deps** (already done):
```bash
cd frontend && npm install
```

2. **Login to Cloudflare**:
```bash
npx wrangler login
```

3. **Configure environment variables** in `frontend/.dev.vars`:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Build & Deploy

```bash
cd frontend

# Preview locally
npm run preview

# Deploy to production
npm run deploy
```

The `deploy` script runs `opennextjs-cloudflare build && opennextjs-cloudflare deploy`:
- Builds the Next.js app with Turbopack
- Bundles it into a Cloudflare Worker via OpenNext
- Deploys to Cloudflare Workers under the name `reachgtm-frontend`

### Production environment variables

Set these in the Cloudflare Dashboard → Workers & Pages → `reachgtm-frontend` → Settings → Variables:

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Public URL of your backend API |
| `NEXTJS_ENV` | `production` |

---

## Backend Deployment

The backend (FastAPI) and agents (LangGraph) run as Python services with PostgreSQL + pgvector and Redis.

### Railway (recommended)

Railway gives you $5 free credit/month — enough for both services + PostgreSQL + Redis.

**Step 1 — Set up databases**

In your Railway project dashboard:
- Click **New** → **Provision PostgreSQL** → name: `reachgtm-db`
- Click **New** → **Add Plugin** → search **Redis** → add it

Railway auto-generates `DATABASE_URL` and `REDIS_URL` — note these down.

**Step 2 — Deploy the Backend**

| Setting | Value |
|---|---|
| Source | GitHub → `badrzah/ReachMarket` |
| Branch | `cloudflare-deploy` |
| Root Directory | *(leave empty — uses repo root)* |
| Dockerfile Path | `backend/Dockerfile` |

Railway will build from root (so `shared/` is available) using `backend/Dockerfile`.

**Step 3 — Deploy the Agents**

Same project, add another service:

| Setting | Value |
|---|---|
| Source | GitHub → `badrzah/ReachMarket` |
| Branch | `cloudflare-deploy` |
| Root Directory | *(leave empty — uses repo root)* |
| Dockerfile Path | `agents/Dockerfile` |

**Step 4 — Environment Variables**

For both services, set these in Railway dashboard → Variables:

| Variable | Source |
|---|---|
| `DATABASE_URL` | Auto from PostgreSQL plugin |
| `REDIS_URL` | Auto from Redis plugin |
| `JWT_SECRET` | Generate a random 32-char string |
| `OPENAI_API_KEY` | Your OpenAI key |
| `ENVIRONMENT` | `production` |
| `NEXT_PUBLIC_API_URL` | The backend's Railway URL (e.g. `https://reachgtm-backend.up.railway.app`) |

**Step 5 — Link with Frontend**

In Cloudflare Dashboard → reachgtm-frontend → Settings → Variables:
- Set `NEXT_PUBLIC_API_URL` = your backend's Railway URL

---

## CI/CD

When a PR merges to `main`, GitHub Actions automatically:
1. Installs frontend dependencies
2. Builds with OpenNext
3. Deploys to Cloudflare Workers

Required GitHub Secrets:
- `CLOUDFLARE_API_TOKEN` — Cloudflare API token with Workers & Pages permissions
- `CLOUDFLARE_ACCOUNT_ID` — Your Cloudflare account ID
- `NEXT_PUBLIC_API_URL` — Backend API URL

---

## Rollback

Via wrangler:
```bash
npx wrangler rollback --name reachgtm-frontend
```

Or in the Cloudflare Dashboard → Workers & Pages → reachgtm-frontend → Deployments.
