# Prospecting Agent API

This FastAPI service provides the Phase 0 backend foundation for Prospecting Agent.

## Setup

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

## Available endpoints

- `GET /`
- `GET /health`
