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
- A Phase 3 deterministic workflow that remains available as a fallback path
- A Phase 4 real research workflow that searches the public web, scrapes selected pages, extracts deterministic evidence, synthesizes reports, persists result rows, and exposes ranked results through the API

## Workflow modes

- The coordinator reads `input/brief.json` and `input/normalized_accounts.json`
- It writes `plan/todos.json` and `plan/icp.json`
- `RESEARCH_MODE=fake` keeps the deterministic Phase 3 account researcher and signal detector
- `RESEARCH_MODE=real` runs Tavily search, Firecrawl scraping with `httpx` and BeautifulSoup fallback, deterministic snippet extraction, and deterministic report synthesis
- Each account gets research, signal, score, outreach, and review JSON files
- Real mode also writes `research/sources/{account_id}.json` for debugging source collection without bloating the primary report files
- Optional Deep Agents wiring still exists, but the default local workflow remains deterministic

## Phase 5 scoring and outreach pipeline

- The coordinator keeps the same run surface but now delegates scoring, persona recommendation, sales angle generation, outreach drafting, and quality review to shared deterministic tool modules
- `scoring_tools.py` turns research evidence plus timing signals into explainable fit, timing, confidence, persona, and overall scores
- `persona_tools.py` chooses the best target persona based on the campaign brief and evidence-backed company context
- `outreach_tools.py` generates a short sales angle, selects one personalization anchor when available, and drafts a cautious outreach email
- `quality_review_tools.py` checks for fake familiarity, deceptive subject lines, unsupported claims, weak evidence, and missing personalization
- Research evidence stays separate from inference: the score and outreach steps can reason from evidence-backed fields, but they do not invent unsupported company pain

## Subagent responsibilities

- ICP strategist: campaign rubric and target criteria
- Account researcher: fake simulated research or real public-source synthesis depending on configuration
- Signal detector: fake timing signals or real source-backed timing signals depending on configuration
- Scoring analyst: deterministic weighted scores based on fit claims, signal timing, evidence count, and persona alignment
- Outreach writer: short draft anchored to research evidence when available
- Compliance reviewer: checks personalization, unsupported familiarity, missing sources, deceptive framing, and weak evidence

## Persistence

- Campaign runs are stored in SQLite as `CampaignRun`
- Structured results are upserted into `ResearchReport`, `SignalReport`, `ScoreReport`, and `OutreachDraft`
- Real source URLs are preserved inside the JSON evidence and signal payloads stored in SQLite
- Quality review remains a workspace file under `review/{account_id}.json`

## Planned expansion

- A future Deep Agents coordinator will manage multi-step research and enrichment workflows.
- Later phases will add research orchestration, scoring, review, and export workflows on top of the Phase 2 input foundation.
