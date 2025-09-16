Vantage AI Marketing SaaS (MVP)

Backend: FastAPI + Postgres (pgvector). Frontend (Next.js) planned. Auth: Clerk.

Quickstart

1) Create virtualenv and install deps
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Configure environment

Create a `.env` with at least:
```
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/vantage_ai
CLERK_JWKS_URL=https://clerk.example.com/.well-known/jwks.json
CLERK_ISSUER=https://clerk.example.com/
META_APP_ID=
META_APP_SECRET=
META_REDIRECT_URI=http://localhost:8000/api/v1/oauth/meta/callback
MODEL_ROUTER_PRIMARY=openai:gpt-4o-mini
MODEL_ROUTER_FALLBACK=ollama:llama3.1
OPENAI_API_KEY=sk-...
```

3) Run API
```
uvicorn app.main:app --reload
```

API

- GET `/api/v1/health` → `{ "status": "ok" }`
- POST `/api/v1/ai/complete` → `{ text }` (requires Bearer token)

Structure

```
app/
  main.py
  api/
    deps.py
    v1/health.py
  core/
    config.py
    security.py
  services/
    model_router.py
requirements.txt
```

