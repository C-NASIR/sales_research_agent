# API contracts

## Implemented in Phase 1

### `GET /health`

Returns a simple service health payload:

```json
{
  "status": "ok",
  "service": "prospecting-agent-api"
}
```

### `POST /campaigns`

Creates a new campaign in `draft` status and records a `campaign_created` activity event.

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

In Phase 1 this will usually be empty because CSV upload is not implemented yet.

### `GET /campaigns/{campaign_id}/events`

Returns campaign activity events:

```json
{
  "events": []
}
```

## Planned, not implemented yet

- `POST /campaigns/{campaign_id}/upload`
- `POST /campaigns/{campaign_id}/runs`
- `GET /campaigns/{campaign_id}/results`
- `PATCH /campaigns/{campaign_id}/accounts/{account_id}/review`
- `POST /campaigns/{campaign_id}/exports`
