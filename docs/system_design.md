# System design

## High-level architecture

Phase 0 uses a simple monorepo with two runnable apps:

- A Next.js frontend in `apps/web`
- A FastAPI backend in `apps/api`

## Current responsibilities

The frontend provides a basic landing page that confirms the project shell is running. The backend provides a root endpoint and `GET /health` for local verification.

## Planned expansion

- A future Deep Agents coordinator will manage multi-step research and enrichment workflows.
- Future campaign workspaces will live under `data/campaigns`.
- A future SQLite database will be introduced in Phase 1 for campaign state and related entities.
