# Prospecting Agent API

This FastAPI service provides the Phase 2 backend foundation for Prospecting Agent.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
uvicorn app.main:app --reload
```

The API starts on `http://localhost:8000` by default.

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

## Inspect workspace files

The upload flow writes files under:

```text
data/campaigns/campaign_REPLACE_ME/input/brief.json
data/campaigns/campaign_REPLACE_ME/input/uploaded_companies.csv
data/campaigns/campaign_REPLACE_ME/input/normalized_accounts.json
data/campaigns/campaign_REPLACE_ME/input/upload_report.json
```
