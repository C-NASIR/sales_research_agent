# System Design

## Overview

Prospecting Agent is a local monorepo that implements a supervised sales research workflow. A user creates a campaign, uploads a CSV of target companies, starts a research run, reviews account-level outputs, edits outreach drafts, and exports approved prospects.

The system is intentionally simple:

- `apps/api` is a FastAPI backend that owns orchestration, persistence, validation, and export generation.
- `apps/web` is a Next.js app that renders the campaign, run, results, review, and export workflows.
- `data/` stores the SQLite database plus campaign-specific workspace artifacts on disk.
- `docs/` describes the API contracts, data model, and system design.

The MVP is optimized for local execution rather than multi-user production deployment. There is no authentication layer, queue infrastructure, CRM sync, or outbound email delivery.

## High-Level Architecture

```text
Browser
  -> Next.js frontend (`apps/web`)
  -> FastAPI backend (`apps/api`)
  -> SQLite database (`data/prospecting_agent.db`)
  -> Campaign workspace files (`data/campaigns/{campaign_id}/...`)
  -> Optional external research services (Tavily + Firecrawl)
```

The backend uses a dual-storage model:

- SQLite stores normalized application state for campaigns, accounts, runs, events, reports, drafts, and exports.
- Workspace JSON and text files store campaign inputs and generated artifacts in a human-inspectable file tree.

This split keeps the API easy to query while preserving the intermediate artifacts that were used to produce a result.

## Repository Structure

### Backend

- `app/main.py`: FastAPI app bootstrap, CORS, exception handlers, router registration, database initialization.
- `app/api/`: HTTP routes for campaigns, uploads, runs, results, reviews, exports, events, todos, and health.
- `app/services/`: business logic for campaign creation, CSV parsing, run management, review updates, exports, workspace setup, and result persistence.
- `app/agents/`: workflow orchestration for fake mode and real-research mode.
- `app/tools/`: deterministic research synthesis, source extraction, scoring, persona selection, outreach drafting, quality review, export generation, search, and scraping helpers.
- `app/db/`: SQLAlchemy models, engine/session setup, and schema initialization.
- `app/workspace/`: path helpers plus JSON/markdown readers and writers.

### Frontend

- `app/`: Next.js App Router pages for campaign list/create/detail, run progress, results, and account detail.
- `components/`: UI and workflow components grouped by area (`campaign`, `run`, `results`, `account`, `review`, `ui`).
- `lib/api.ts`: typed HTTP client used by server and client components.
- `lib/types.ts`: frontend response and domain types aligned to the backend API.

## Backend Design

### API Layer

FastAPI exposes a thin route layer. Endpoints validate request shape, load referenced campaign/account records, and delegate business logic to services.

Important route groups:

- Campaign setup: create and list campaigns.
- CSV ingestion: upload a target-company CSV, normalize domains, detect invalid and duplicate rows, and create accounts.
- Run control: start a background run, list runs, fetch latest run, and fetch a specific run.
- Read models: list accounts, list events, fetch todos, fetch results, and fetch account detail.
- Review and export mutations: update review status, edit outreach drafts, create exports, and download generated files.

Error handling is centralized:

- Validation errors are converted to `400` JSON responses with a top-level `detail`.
- Missing resources return `404`.
- Run conflicts return `409`.
- Unhandled exceptions are logged and returned as `500 Internal server error.`

### Service Layer

The service layer holds almost all application behavior:

- `campaign_service`: creates campaigns, assigns IDs, stores the workspace path, and writes `input/brief.json`.
- `csv_service`: parses UTF-8 CSV input, normalizes domains, and reports invalid or duplicate rows.
- `account_service`: creates accounts and updates per-account research status.
- `run_service`: creates `CampaignRun` rows and launches the workflow in a FastAPI `BackgroundTasks` job.
- `result_service`: upserts research, signal, score, and outreach records, and assembles result/detail read models.
- `review_service`: updates supervised review status, rewrites edited drafts, reruns quality review, and persists the updated review artifact.
- `export_service`: selects exportable accounts, generates files, and upserts `ExportFile` records.
- `event_service`: persists activity events and logs important event types.
- `todo_service`: manages the workflow todo file in workspace storage.

### Workflow Orchestration

The active orchestration path is `run_service.execute_campaign_run()` -> `agents.coordinator.run_campaign_workflow()`.

The workflow does the following:

1. Load the campaign brief and normalized accounts from workspace files.
2. Create a todo plan and ICP artifact.
3. Iterate over campaign accounts one by one.
4. Run research in either fake mode or real mode.
5. Persist research and signal outputs.
6. Deterministically score the account.
7. Generate an outreach draft.
8. Run quality review on the draft.
9. Update account and campaign statuses and emit activity events.

The implementation is synchronous inside the background task. Accounts are processed sequentially; there is no job queue, worker pool, or distributed execution layer.

### Research Modes

The backend supports two research modes controlled by `RESEARCH_MODE`:

- `fake`: deterministic simulated research with no external API calls.
- `real`: public-web research using Tavily search plus Firecrawl or an `httpx`/BeautifulSoup fallback for page scraping.

Real mode flow:

1. Build search queries for the company and domain.
2. Collect and deduplicate public search results.
3. Prioritize URLs such as homepage, pricing, careers, blog, engineering, and product pages.
4. Scrape a bounded number of pages.
5. Extract evidence snippets by keyword matching.
6. Synthesize research and timing reports from the gathered evidence.

If research fails or yields weak evidence, the system writes low-confidence fallback reports instead of aborting the whole campaign when possible. This keeps downstream scoring, drafting, and review steps operational.

### Deterministic Post-Research Pipeline

After research, the remaining pipeline is heuristic and deterministic:

- `scoring_tools.py` computes fit, timing, confidence, persona, and overall scores from evidence and signal structure.
- `persona_tools.py` recommends a target persona from campaign personas plus evidence text.
- `outreach_tools.py` creates a sales angle, chooses a personalization source, and drafts subject/body copy.
- `quality_review_tools.py` flags unsupported claims, missing personalization, deceptive framing, fake familiarity, and low-confidence evidence.

Although the project references Deep Agents and exposes `MODEL_NAME` and `USE_DEEP_AGENTS` settings, the current run path does not execute an LLM-based multi-agent runtime. The MVP behavior is driven by deterministic service and tool code.

## Persistence Model

### Relational State in SQLite

SQLite stores the normalized state required by the API:

- `Campaign`
- `Account`
- `CampaignRun`
- `ActivityEvent`
- `ResearchReport`
- `SignalReport`
- `ScoreReport`
- `OutreachDraft`
- `ExportFile`

SQLAlchemy models use simple foreign-key relationships and `create_all()` on startup. There is no migration framework yet; schema changes currently require recreating the local database when incompatible.

### Workspace File Model

Each campaign has a dedicated workspace under:

```text
data/campaigns/{campaign_id}/
```

Subdirectories:

- `input/`
- `plan/`
- `research/`
- `signals/`
- `scores/`
- `outreach/`
- `review/`
- `exports/`

Representative files:

- `input/brief.json`
- `input/uploaded_companies.csv`
- `input/normalized_accounts.json`
- `input/upload_report.json`
- `plan/todos.json`
- `plan/icp.json`
- `research/{account_id}.json`
- `research/sources/{account_id}.json`
- `signals/{account_id}.json`
- `scores/{account_id}.json`
- `outreach/{account_id}.json`
- `review/{account_id}.json`
- `exports/prospects.csv`
- `exports/campaign_report.md`
- `exports/archive.json`

The database is the primary API datastore, while workspace files are the primary artifact store.

## Frontend Design

The frontend is a Next.js App Router application with a small typed API client and React Query for client-side mutations and refreshes.

### Rendering Strategy

- Page-level route components are mostly server components that fetch initial data from the API.
- Interactive workspaces are client components that use React Query for mutations, invalidation, polling, and refresh.

Examples:

- Campaign detail page renders the brief, CSV uploader, account preview table, and start-run control.
- Run progress page polls the latest run, todos, events, and account statuses every 2 seconds until the run reaches a terminal state.
- Results page renders summary cards, filters, export controls, and the ranked results table.
- Account detail page shows research, signals, evidence, score breakdown, outreach draft, draft editor, review controls, and quality review.

### Frontend State Model

The frontend keeps very little local domain state:

- React Query caches fetched API responses.
- Forms and filters use local component state.
- Mutations invalidate the relevant query keys to refresh results and account detail views.

There is no global client-side state store beyond the React Query cache.

## End-to-End Data Flow

### Campaign Setup

1. User submits campaign metadata from the web app.
2. Backend creates a `Campaign` row and campaign workspace.
3. Backend writes the campaign brief to `input/brief.json`.
4. User uploads a CSV.
5. Backend parses rows, normalizes domains, creates `Account` rows, writes upload artifacts, and marks the campaign `ready` if accounts were created.

### Run Execution

1. User starts a run from the campaign detail page.
2. Backend creates a `CampaignRun` row and enqueues a FastAPI background task.
3. The background task updates account statuses, runs research/account processing, and emits events.
4. The frontend polls run status, todos, accounts, and events until the run is `completed`, `partial`, or `failed`.

### Review and Export

1. Results page loads ranked account summaries from the database.
2. Account detail page loads the merged account record plus workspace artifacts.
3. User updates review status or edits a draft.
4. Backend persists the mutation, rewrites relevant workspace JSON, reruns quality review if needed, and emits events.
5. User creates exports for selected review statuses.
6. Backend builds CSV, Markdown, and JSON export artifacts and exposes them through download routes.

## External Dependencies

The system can run fully offline in `fake` mode. In `real` mode it depends on:

- Tavily for search
- Firecrawl for scraping when configured
- `httpx` plus BeautifulSoup as a fallback scraper

The frontend depends on the backend through `NEXT_PUBLIC_API_BASE_URL`, which defaults to `http://localhost:8000`.

## Testing and Validation

Current automated coverage is split by app:

- Backend: Pytest coverage for health, campaigns, CSV upload, scoring, review/export flows, and related API behavior.
- Frontend: TypeScript typecheck, ESLint, and focused Vitest component tests.

There are no end-to-end browser tests in the current codebase.

## Design Constraints and Limitations

- Single-node local architecture only.
- No authentication or user isolation.
- No migration framework for database schema evolution.
- Background work runs in-process through FastAPI `BackgroundTasks`, so jobs are not durable across process restarts.
- Account processing is sequential.
- Real research quality is bounded by public-source discovery and simple heuristic extraction.
- Export generation is local filesystem output only.
- The app does not send email, write to a CRM, or sync to third-party sales systems.

## Summary

The current system is a pragmatic local MVP: FastAPI owns orchestration and persistence, Next.js provides the review workspace, SQLite stores normalized application state, and campaign workspace files preserve generated artifacts. The design favors inspectability and straightforward iteration over distributed scale or production-hard multi-user concerns.
