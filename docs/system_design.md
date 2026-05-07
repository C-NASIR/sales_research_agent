# System design

## High-level architecture

The project uses a simple monorepo with two runnable apps:

- A Next.js frontend in `apps/web`
- A FastAPI backend in `apps/api`

## Current responsibilities

The frontend provides a basic landing page that confirms the project shell is running. The backend now provides:

- Root and health endpoints for local verification
- A SQLite-backed state layer for campaigns, accounts, runs, events, exports, and future report entities
- Phase 1 campaign APIs for creating and reading campaigns plus listing campaign accounts and events

## Planned expansion

- A future Deep Agents coordinator will manage multi-step research and enrichment workflows.
- Future campaign workspaces will live under `data/campaigns`.
- Later phases will add CSV upload, research orchestration, scoring, review, and export workflows on top of the Phase 1 backend foundation.
