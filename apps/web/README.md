# Prospecting Agent Web Vite

This Vite app is the primary frontend for Prospecting Agent. It preserves the
existing campaign, run, results, account review, draft editing, and export flows
while removing the Next.js App Router dependency.

## Environment

The frontend reads the backend base URL from `VITE_API_BASE_URL`.

If you do not set it, the app defaults to:

```text
http://localhost:8000
```

## Setup

```bash
npm install
```

## Run

```bash
npm run dev
```

The app starts on `http://localhost:3000` by default.

## Validation commands

```bash
npm run typecheck
npm run lint
npm run test
```

## Route map

- `/`
- `/campaigns`
- `/campaigns/new`
- `/campaigns/:campaignId`
- `/campaigns/:campaignId/run`
- `/campaigns/:campaignId/results`
- `/campaigns/:campaignId/accounts/:accountId`

## Browser validation

1. Open `http://localhost:3000`
2. Go to `/campaigns`
3. Create a campaign at `/campaigns/new`
4. Upload `samples/devtools_companies.csv`
5. Start a run from the campaign detail page
6. Open `/campaigns/{campaignId}/run`
7. Open `/campaigns/{campaignId}/results`
8. Open `/campaigns/{campaignId}/accounts/{accountId}`
9. Update review status, edit the draft, and create exports
