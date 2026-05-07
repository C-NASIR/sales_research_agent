# Prospecting Agent API

This FastAPI service now supports campaign setup, research runs, results inspection, supervised review updates, draft editing, and export generation for Prospecting Agent.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Run

```bash
uvicorn app.main:app --reload
```

The API starts on `http://localhost:8000` by default.

## Research mode

Phase 4 supports two backend research modes:

- `RESEARCH_MODE=fake` keeps the deterministic Phase 3 behavior and does not require API keys.
- `RESEARCH_MODE=real` runs public web search and scraping and requires both `TAVILY_API_KEY` and `FIRECRAWL_API_KEY`.

Other useful Phase 4 environment variables:

- `MAX_SEARCH_RESULTS`
- `MAX_SCRAPED_PAGES_PER_ACCOUNT`
- `MAX_SOURCE_CHARS`

During MVP development, delete `data/prospecting_agent.db` and restart the API if your local SQLite file was created before the latest schema changes. Phase 9 adds review and export routes on top of the existing schema.

## Phase 10 reliability updates

Phase 10 keeps the existing API surface but hardens it with:

- Consistent `400`, `404`, `409`, and `500` responses
- Validation errors returned as JSON with a top-level `detail`
- Safer export download path handling
- Standard logging for important campaign, run, upload, and export events
- Pytest coverage for the main MVP routes and deterministic scoring logic

## Health check

```bash
curl http://localhost:8000/health
```

## Create campaign

```bash
curl -X POST http://localhost:8000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI code review outbound",
    "product_description": "AI code review tool for engineering teams",
    "ideal_customer_profile": "B2B SaaS companies with 20 to 200 engineers",
    "pain_statement": "Slow pull request review and inconsistent code quality",
    "target_persona": "VP Engineering, CTO, Head of Platform",
    "tone": "Direct, specific, no hype",
    "max_accounts": 10
  }'
```

## List campaigns

```bash
curl http://localhost:8000/campaigns
```

## Upload sample CSV

Replace the campaign id after creating one:

```bash
curl -X POST http://localhost:8000/campaigns/campaign_REPLACE_ME/upload \
  -F "file=@../../samples/devtools_companies.csv"
```

## List accounts

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/accounts
```

## List events

Replace the campaign id after creating one:

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/events
```

## Start run

```bash
curl -X POST http://localhost:8000/campaigns/campaign_REPLACE_ME/runs
```

This now returns quickly and continues the workflow in the background.

With `RESEARCH_MODE=real`, a misconfigured backend returns a clear run failure instead of crashing at import time.

## Get latest run

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/runs/latest
```

## Get todos

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/todos
```

## Phase 5 validation flow

Start in fake mode with a fresh SQLite file if you want to validate the deterministic workflow:

```bash
RESEARCH_MODE=fake DATABASE_URL=sqlite:///./data/phase5_validation.db uvicorn app.main:app --reload
```

Then run:

```bash
curl -X POST http://localhost:8000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI code review outbound",
    "product_description": "AI code review tool for engineering teams",
    "ideal_customer_profile": "B2B SaaS companies and developer tool companies with active engineering teams",
    "pain_statement": "Slow pull request review and inconsistent code quality",
    "target_persona": "VP Engineering, CTO, Head of Platform",
    "tone": "Direct, specific, no hype",
    "max_accounts": 10
  }'
```

```bash
curl -X POST http://localhost:8000/campaigns/campaign_REPLACE_ME/upload \
  -F "file=@../../samples/devtools_companies.csv"
```

```bash
curl -X POST http://localhost:8000/campaigns/campaign_REPLACE_ME/runs
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/results
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/events
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/accounts/account_REPLACE_ME
```

## Get results

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/results
```

## Get account detail

Replace the account id:

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/accounts/account_REPLACE_ME
```

## Update review status

```bash
curl -X PATCH http://localhost:8000/campaigns/campaign_REPLACE_ME/accounts/account_REPLACE_ME/review \
  -H "Content-Type: application/json" \
  -d '{
    "review_status": "approved"
  }'
```

## Update draft

```bash
curl -X PATCH http://localhost:8000/campaigns/campaign_REPLACE_ME/accounts/account_REPLACE_ME/draft \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Engineering workflow quality",
    "body": "Hi there,\n\nI came across your company while researching developer focused software teams.\n\nWe help engineering teams reduce review bottlenecks and keep code quality consistent.\n\nWorth comparing notes?"
  }'
```

## Create export

```bash
curl -X POST http://localhost:8000/campaigns/campaign_REPLACE_ME/exports \
  -H "Content-Type: application/json" \
  -d '{
    "include_review_statuses": ["approved"]
  }'
```

## List exports

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/exports
```

## Download export

```bash
curl -L http://localhost:8000/campaigns/campaign_REPLACE_ME/exports/export_REPLACE_ME/download
```

## Seed a demo campaign

```bash
python3 scripts/seed_demo.py
```

For a fully populated fake-mode demo:

```bash
RESEARCH_MODE=fake python3 scripts/seed_demo.py --run-fake-workflow
```

## Run tests

```bash
python3 -m pytest
```

## Inspect workspace files

The upload and run flows write files under:

```text
data/campaigns/campaign_REPLACE_ME/input/brief.json
data/campaigns/campaign_REPLACE_ME/input/uploaded_companies.csv
data/campaigns/campaign_REPLACE_ME/input/normalized_accounts.json
data/campaigns/campaign_REPLACE_ME/input/upload_report.json
data/campaigns/campaign_REPLACE_ME/plan/todos.json
data/campaigns/campaign_REPLACE_ME/plan/icp.json
data/campaigns/campaign_REPLACE_ME/research/account_REPLACE_ME.json
data/campaigns/campaign_REPLACE_ME/research/sources/account_REPLACE_ME.json
data/campaigns/campaign_REPLACE_ME/signals/account_REPLACE_ME.json
data/campaigns/campaign_REPLACE_ME/scores/account_REPLACE_ME.json
data/campaigns/campaign_REPLACE_ME/outreach/account_REPLACE_ME.json
data/campaigns/campaign_REPLACE_ME/review/account_REPLACE_ME.json
```

The `research/sources` file is intended for debugging source collection. The main research and signal reports keep only source metadata and source-backed evidence, not full scraped page dumps.
