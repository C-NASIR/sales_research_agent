# Prospecting Agent

Prospecting Agent is a local full-stack sales research workspace that will eventually coordinate account research, scoring, outreach drafting, review, and export workflows.

## MVP goal

The MVP is intended to let a user create a campaign, upload target companies, run research, review results, and export approved prospects from one local workspace.

## Current scope

The project currently includes Phase 0 and Phase 1:

- Minimal FastAPI backend with a root endpoint and `GET /health`
- SQLite-backed backend foundation for campaigns, accounts, events, and future report entities
- Campaign APIs for create, list, get, and campaign-scoped accounts and events
- CSV upload, domain normalization, account creation, and campaign workspace files under `data/campaigns`
- Minimal Next.js frontend with a landing page
- Root documentation, environment examples, and sample CSV data
- Local project folders for future campaign workspaces

The project does not include CSV upload flows, Deep Agents, authentication, CRM integrations, or production deployment yet.

## Local setup

1. Copy `.env.example` to `.env` if you want to customize local values.
2. Start the backend from `apps/api`.
3. Start the frontend from `apps/web`.

## Backend run instructions

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

## Frontend run instructions

```bash
cd apps/web
npm install
npm run dev
```

## Expected URLs

- Backend health: [http://localhost:8000/health](http://localhost:8000/health)
- Frontend: [http://localhost:3000](http://localhost:3000)
