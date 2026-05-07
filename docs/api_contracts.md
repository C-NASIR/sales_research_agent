# API contracts

## Implemented in Phase 4

### `GET /health`

Returns a simple service health payload:

```json
{
  "status": "ok",
  "service": "prospecting-agent-api"
}
```

### `POST /campaigns`

Creates a new campaign in `draft` status, creates the campaign workspace, writes `input/brief.json`, and records `campaign_created` plus `campaign_workspace_created` events.

### `GET /campaigns`

Returns all campaigns:

```json
{
  "campaigns": []
}
```

### `GET /campaigns/{campaign_id}`

Returns a single campaign or `404` if it does not exist.

### `GET /campaigns/{campaign_id}/accounts`

Returns campaign accounts:

```json
{
  "accounts": []
}
```

Before upload this will usually be empty. After Phase 2 CSV upload it returns the created account rows.

### `GET /campaigns/{campaign_id}/events`

Returns campaign activity events:

```json
{
  "events": []
}
```

### `POST /campaigns/{campaign_id}/upload`

Accepts `multipart/form-data` with a file field named `file`.

The CSV must contain `company_name` and `domain` headers, matched case-insensitively.

Response shape:

```json
{
  "campaign_id": "campaign_...",
  "valid_rows": 5,
  "invalid_rows": 0,
  "duplicate_rows": 0,
  "created_accounts": 5,
  "accounts": [
    {
      "id": "account_...",
      "company_name": "Sentry",
      "domain": "sentry.io"
    }
  ],
  "invalid": [],
  "duplicates": []
}
```

The upload endpoint writes:

- `data/campaigns/{campaign_id}/input/uploaded_companies.csv`
- `data/campaigns/{campaign_id}/input/normalized_accounts.json`
- `data/campaigns/{campaign_id}/input/upload_report.json`

### `POST /campaigns/{campaign_id}/runs`

Starts a background campaign workflow run and returns immediately with the persisted run record.

- With `RESEARCH_MODE=fake`, the run uses the deterministic Phase 3 workflow and does not require API keys.
- With `RESEARCH_MODE=real`, the run performs public web search, scraping, evidence extraction, deterministic report synthesis, scoring, outreach drafting, and quality review.
- With `RESEARCH_MODE=real` and missing required keys, the run fails cleanly with a persisted failed run and error events.
- If another run for the same campaign is already `pending` or `running`, the endpoint returns `400` with `A campaign run is already in progress.`

### `GET /campaigns/{campaign_id}/runs`

Returns campaign runs sorted newest first:

```json
{
  "runs": []
}
```

### `GET /campaigns/{campaign_id}/runs/latest`

Returns the latest persisted run record for the campaign or `404` if no run exists.

### `GET /campaigns/{campaign_id}/runs/{run_id}`

Returns the persisted run record:

```json
{
  "id": "run_...",
  "campaign_id": "campaign_...",
  "status": "completed",
  "started_at": "2026-05-07T01:10:16.529359",
  "completed_at": "2026-05-07T01:10:16.612419",
  "error_message": null,
  "agent_thread_id": "run_...",
  "created_at": "2026-05-07T01:10:16.525376",
  "updated_at": "2026-05-07T01:10:16.612419"
}
```

### `GET /campaigns/{campaign_id}/todos`

Returns the latest todo plan written under `plan/todos.json`:

```json
{
  "todos": [
    {
      "id": "todo_icp",
      "title": "Define ICP and rubric",
      "status": "completed"
    }
  ]
}
```

If the todo file does not exist yet, the endpoint returns:

```json
{
  "todos": []
}
```

### `GET /campaigns/{campaign_id}/results`

Phase 8 uses this read-only endpoint to populate the results dashboard.

Returns ranked account results sorted by `overall_score` descending, with missing scores kept at the bottom. Per-account rows expose deterministic scoring, persona, and draft quality output. Low-confidence fallback accounts may still appear with low scores and flagged drafts if research tools failed for that account:

```json
{
  "campaign_id": "campaign_...",
  "status": "completed",
  "accounts": [
    {
      "account_id": "account_...",
      "company_name": "Sentry",
      "domain": "sentry.io",
      "overall_score": 78,
      "fit_score": 82,
      "timing_score": 68,
      "confidence_score": 79,
      "persona_score": 80,
      "recommended_persona": "VP Engineering",
      "sales_angle": "Engineering workflow quality",
      "review_status": "unreviewed",
      "research_status": "completed",
      "draft_quality_status": "approved_by_reviewer"
    }
  ]
}
```

### `GET /campaigns/{campaign_id}/accounts/{account_id}`

Phase 8 uses this read-only endpoint to power the account detail page.

Returns the account row plus the run artifacts:

- `account`
- `research_report`
- `signal_report`
- `score_report`
- `outreach_draft`
- `quality_review`

In Phase 5, `score_report` includes a structured `score_breakdown`, `recommended_persona`, and `sales_angle`. `outreach_draft` includes `personalization_source_url`, and `quality_review` may return `approved_by_reviewer`, `flagged`, or `blocked`.

The frontend renders these sections read-only in Phase 8. No review mutation, draft editing, export creation, or email sending is attached to this response yet.

### `PATCH /campaigns/{campaign_id}/accounts/{account_id}/review`

Phase 9 adds supervised account review updates.

Request:

```json
{
  "review_status": "approved"
}
```

Allowed statuses:

- `unreviewed`
- `approved`
- `rejected`
- `needs_edit`
- `not_enough_evidence`

The endpoint updates the account review status, updates the account timestamp, and records an `account_review_updated` event.

### `PATCH /campaigns/{campaign_id}/accounts/{account_id}/draft`

Phase 9 adds read-write draft editing for the generated outreach artifact.

Request fields are optional, but at least one must be present:

- `subject`
- `body`
- `personalization_source`
- `personalization_source_url`
- `sales_angle`

The endpoint updates only provided fields, rewrites the workspace outreach file, reruns quality review, updates draft quality status, and records `draft_updated` plus `quality_review_updated` events.

### `POST /campaigns/{campaign_id}/exports`

Creates export files for accounts matching the requested review statuses.

Default request behavior when omitted:

```json
{
  "include_review_statuses": ["approved"]
}
```

Response:

```json
{
  "campaign_id": "campaign_...",
  "exports": [
    {
      "id": "export_...",
      "campaign_id": "campaign_...",
      "export_type": "prospects_csv",
      "file_path": "data/campaigns/campaign_.../exports/prospects.csv",
      "download_url": "/campaigns/campaign_.../exports/export_.../download",
      "created_at": "2026-05-07T17:03:25.390732"
    }
  ]
}
```

Phase 9 generates:

- `prospects.csv`
- `campaign_report.md`
- `archive.json`

If no accounts match the requested statuses, the endpoint returns `400` with `No accounts are available for export.`

### `GET /campaigns/{campaign_id}/exports`

Returns export metadata newest first:

```json
{
  "campaign_id": "campaign_...",
  "exports": []
}
```

### `GET /campaigns/{campaign_id}/exports/{export_id}/download`

Downloads the stored export file with a useful filename and a matching media type where easy:

- `text/csv`
- `text/markdown`
- `application/json`

### `GET /campaigns/{campaign_id}/events`

Phase 4 extends activity events with real-research steps, including:

- `web_search_started`
- `web_search_completed`
- `web_scrape_started`
- `web_scrape_completed`
- `evidence_extracted`
- `research_synthesis_completed`
- `signal_synthesis_completed`
- `research_low_confidence`
- `research_tool_failed`

Phase 5 adds or updates downstream workflow events, including:

- `score_report_created`
- `persona_recommended`
- `sales_angle_created`
- `draft_created`
- `quality_review_created`
- `draft_flagged`
- `draft_blocked`

## Planned, not implemented yet

- Review-side bulk actions
- CRM sync and send workflows
