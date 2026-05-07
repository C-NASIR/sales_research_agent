# Prospecting Agent

Prospecting Agent is a local full-stack sales research workspace that coordinates account research, scoring, outreach drafting, review, and later export workflows.

## MVP goal

The MVP is intended to let a user create a campaign, upload target companies, run research, review results, and export approved prospects from one local workspace.

## Current scope

The project currently includes the first five backend phases:

- Minimal FastAPI backend with a root endpoint and `GET /health`
- SQLite-backed backend foundation for campaigns, accounts, events, and future report entities
- Campaign APIs for create, list, get, and campaign-scoped accounts and events
- CSV upload, domain normalization, account creation, and campaign workspace files under `data/campaigns`
- Phase 3 deterministic workflow runs with simulated research, scoring, outreach, and results APIs
- Phase 4 real public web research mode with Tavily search, Firecrawl scraping, deterministic evidence synthesis, and a configurable fake-mode fallback
- Phase 5 deterministic scoring, persona recommendation, sales-angle generation, outreach drafting, and quality review on the existing API surfaces
- Minimal Next.js frontend with a landing page
- Root documentation, environment examples, and sample CSV data
- Local project folders for future campaign workspaces

The project does not include frontend campaign screens, review approvals, export workflow, CRM integrations, or production deployment yet.

## Local setup

1. Copy `.env.example` to `.env` if you want to customize local values.
2. Start the backend from `apps/api`.
3. Start the frontend from `apps/web`.

For Phase 4 there are two research modes:

- `RESEARCH_MODE=fake` keeps the deterministic no-key workflow from Phase 3.
- `RESEARCH_MODE=real` uses Tavily and Firecrawl for public web research and requires `TAVILY_API_KEY` plus `FIRECRAWL_API_KEY`.

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
