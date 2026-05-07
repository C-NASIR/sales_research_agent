# Prospecting Agent Web

This Next.js app now provides the Phase 6 campaign setup workflow for Prospecting Agent.

## Dependencies added in Phase 6

- `@tanstack/react-query`
- `react-hook-form`
- `zod`
- `@hookform/resolvers`

## Environment

The frontend reads the backend base URL from `NEXT_PUBLIC_API_BASE_URL`.

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

## Phase 6 browser flow

1. Open `http://localhost:3000`
2. Go to `/campaigns`
3. Create a campaign at `/campaigns/new`
4. Upload `samples/devtools_companies.csv`
5. Review the uploaded accounts table
6. Start a research run

## Known limitations

- There is no results dashboard yet.
- There are no account detail pages yet.
- Review and export workflows are not in the frontend yet.

## Phase 7 browser validation

1. Create a campaign and upload `samples/devtools_companies.csv`
2. Start a run from the campaign detail page
3. Confirm the browser navigates to `/campaigns/{campaignId}/run?runId={runId}`
4. Confirm the run page shows status, account progress, todos, and activity
5. Wait for polling to stop after `completed`, `failed`, or `partial`
