# API contracts

## Implemented in Phase 0

### `GET /health`

Returns a simple service health payload:

```json
{
  "status": "ok",
  "service": "prospecting-agent-api"
}
```

## Planned, not implemented yet

- `POST /campaigns`
- `POST /campaigns/{campaign_id}/upload`
- `POST /campaigns/{campaign_id}/runs`
- `GET /campaigns/{campaign_id}/results`

These endpoints are placeholders for later phases and are intentionally not implemented in Phase 0.
