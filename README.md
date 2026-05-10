# Prospecting Agent 🚧

Prospecting Agent is a local full-stack sales research workspace that coordinates account research, scoring, outreach drafting, supervised review, and export workflows.

## How it works

A user can give the system a product, an ideal customer profile, and a list of companies. The system researches those companies, scores them, explains the reasoning, drafts outreach, lets the user review the work, and exports a usable prospecting file.

## MVP goal

The MVP is intended to let a user create a campaign, upload target companies, run research, review results, and export approved prospects from one local workspace.

## Current scope

The project now includes the Phase 10 MVP flow:

- Campaign setup, listing, and detail pages
- CSV upload with duplicate detection and validation
- Background campaign runs with progress polling
- Results dashboard and account detail workspaces
- Supervised review controls and draft editing
- Local export generation and downloads
- Backend test coverage for health, campaigns, CSV upload, scoring, review, and exports
- Frontend typecheck, lint, and small component tests
- Demo seed script plus sample CSVs for repeatable walkthroughs

CRM integrations, email sending, authentication, billing, and production deployment are still out of scope.

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
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

## Frontend run instructions

```bash
cd apps/web
npm install
npm run dev
```

If you need a custom backend URL:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Expected URLs

- Backend health: [http://localhost:8000/health](http://localhost:8000/health)
- Frontend: [http://localhost:3000](http://localhost:3000)

## Demo seed

To create a demo campaign and preload accounts:

```bash
cd apps/api
python3 scripts/seed_demo.py
```

To also run the deterministic fake workflow:

```bash
cd apps/api
RESEARCH_MODE=fake python3 scripts/seed_demo.py --run-fake-workflow
```

The script prints the campaign, run, and results URLs for the browser.

## Verification

Backend:

```bash
cd apps/api
python3 -m pytest
```

Frontend:

```bash
cd apps/web
npm run typecheck
npm run lint
npm run test
```

## Browser workflow

1. Open [http://localhost:3000](http://localhost:3000)
2. Click through to `/campaigns`
3. Create a campaign from `/campaigns/new`
4. Upload `samples/devtools_companies.csv` on the campaign detail page
5. Confirm the uploaded accounts appear in the table
6. Start the research run from the same page
7. Open the run progress page and wait for `completed` or `partial`
8. Click `View results`
9. Open one account to inspect evidence, signals, scores, draft, and quality notes
10. Approve or reject the account, edit the draft, and return to results
11. Create an export for approved accounts and download the generated files

The browser can now show run progress through polling, let the user supervise review decisions, edit drafts locally, and generate export artifacts after a run finishes. The app still does not send outreach or write to a CRM.
