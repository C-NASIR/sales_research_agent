# API contracts

## Implemented in Phase 2

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

## Planned, not implemented yet

- `POST /campaigns/{campaign_id}/runs`
- `GET /campaigns/{campaign_id}/results`
- `PATCH /campaigns/{campaign_id}/accounts/{account_id}/review`
- `POST /campaigns/{campaign_id}/exports`
