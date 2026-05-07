# System design

## High-level architecture

The project uses a simple monorepo with two runnable apps:

- A Next.js frontend in `apps/web`
- A FastAPI backend in `apps/api`

## Current responsibilities

The frontend provides a basic landing page that confirms the project shell is running. The backend now provides:

- Root and health endpoints for local verification
- A SQLite-backed state layer for campaigns, accounts, runs, events, exports, and future report entities
- Campaign APIs for creating and reading campaigns plus listing campaign accounts and events
- Phase 2 campaign workspace creation under `data/campaigns/{campaign_id}`
- CSV input processing that normalizes company rows, detects duplicates, creates account records, and writes input artifacts to disk

## Planned expansion

- A future Deep Agents coordinator will manage multi-step research and enrichment workflows.
- Later phases will add research orchestration, scoring, review, and export workflows on top of the Phase 2 input foundation.
