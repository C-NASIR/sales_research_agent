# Prospecting Agent API

This FastAPI service provides the Phase 1 backend foundation for Prospecting Agent.

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

## List events

Replace the campaign id after creating one:

```bash
curl http://localhost:8000/campaigns/campaign_REPLACE_ME/events
```
