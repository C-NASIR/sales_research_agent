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
- A Phase 3 deterministic workflow that reads the workspace, generates fake structured research outputs, persists result rows, and exposes ranked results through the API

## Phase 3 workflow

- The coordinator reads `input/brief.json` and `input/normalized_accounts.json`
- It writes `plan/todos.json` and `plan/icp.json`
- Each account gets simulated research, signal, score, outreach, and review JSON files
- The fake workflow is deterministic by default and does not require API keys
- Optional Deep Agents wiring exists for future phases, but local validation stays on the fake path

## Subagent responsibilities

- ICP strategist: campaign rubric and target criteria
- Account researcher: simulated company summary and fake evidence
- Signal detector: simulated timing signal and why-now note
- Scoring analyst: deterministic weighted scores
- Outreach writer: short draft based on simulated research
- Compliance reviewer: basic quality and familiarity checks

## Persistence

- Campaign runs are stored in SQLite as `CampaignRun`
- Structured results are upserted into `ResearchReport`, `SignalReport`, `ScoreReport`, and `OutreachDraft`
- Quality review remains a workspace file under `review/{account_id}.json`

## Planned expansion

- A future Deep Agents coordinator will manage multi-step research and enrichment workflows.
- Later phases will add research orchestration, scoring, review, and export workflows on top of the Phase 2 input foundation.
