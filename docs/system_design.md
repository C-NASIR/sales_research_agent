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

## Phase 6 frontend campaign setup

- The Next.js app now exposes the first usable browser workflow: campaign list, campaign creation, campaign detail, CSV upload, account preview, and run start
- Route pages stay server-rendered so campaign lists and detail views fetch directly from the FastAPI API on navigation
- React Query is used for client-side mutations only: create campaign, upload CSV, and start run
- The shared frontend API client reads `NEXT_PUBLIC_API_BASE_URL`, defaults to `http://localhost:8000`, and preserves backend `detail` messages when requests fail
- CSV parsing and validation remain backend-owned; the browser only submits `FormData` with a `file` field and renders the returned upload report
- After upload or run start, the client calls `router.refresh()` so the server-rendered campaign status and account list stay aligned with backend state

## Phase 7 progress visibility

- Run start is now backgrounded with FastAPI `BackgroundTasks`, so `POST /campaigns/{campaign_id}/runs` returns quickly with a persisted run id instead of waiting for workflow completion
- The background task creates its own database session, runs the coordinator locally in-process, and persists terminal `completed`, `partial`, or `failed` state back onto the run row and campaign row
- The frontend progress page uses polling every 2 seconds for `GET /runs/{run_id}` or `GET /runs/latest`, `GET /events`, `GET /accounts`, and `GET /todos`
- Polling stops when the run reaches a terminal state; websocket or SSE streaming is intentionally deferred to keep the MVP local and simple
- Campaign todos are still workspace-backed in `plan/todos.json`, but the API now exposes them so the browser can show plan progress
- Account progress is inferred from persisted `research_status` values instead of a separate progress subsystem

## Phase 8 results and account detail

- The frontend now adds two read-only result routes: `/campaigns/{campaignId}/results` for ranked campaign output and `/campaigns/{campaignId}/accounts/{accountId}` for one-account inspection
- The results dashboard fetches `GET /campaigns/{campaign_id}` plus `GET /campaigns/{campaign_id}/results`, then applies client-side search, status filtering, quality filtering, and minimum-score filtering without changing backend contracts
- The account detail page fetches `GET /campaigns/{campaign_id}` plus `GET /campaigns/{campaign_id}/accounts/{account_id}` and renders missing optional artifacts defensively so incomplete accounts do not crash the page
- Evidence is rendered as compact cards that expose the claim, supporting evidence, confidence, evidence type, and source URL, while timing signals get a matching read model with `why_now` context
- Scores are shown both as high-level pills and as a raw explanation plus compact JSON breakdown so the user can inspect the scoring rationale without editing it
- Quality review remains read-only in Phase 8: the UI surfaces quality status, issues, blocked reasons, and recommended edits, but does not yet allow approve, reject, edit, or export actions

## Phase 9 review workflow and export

- Review status is now a supervised user-controlled field on each account, with explicit `approved`, `rejected`, `needs_edit`, `not_enough_evidence`, and `unreviewed` states
- Draft editing stays local to the app: the user can change the generated outreach subject, body, personalization source, personalization URL, and sales angle, but the system still does not send anything
- After any draft edit, the backend rewrites the workspace outreach file and reruns `quality_review_tools.py` so the quality panel reflects the edited draft instead of stale generated output
- Export generation is campaign-scoped and review-gated: only approved accounts are included by default, though the user can opt into other review statuses when generating an export
- The export subsystem writes three file types under `data/campaigns/{campaign_id}/exports`: `prospects.csv` for spreadsheet use, `campaign_report.md` for human-readable review, and `archive.json` for structured debugging or future import
- No email sending exists in the MVP because Phase 9 is still a supervised preparation workflow, not an execution workflow
