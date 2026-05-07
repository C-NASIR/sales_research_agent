# Prospecting Agent Web

This Next.js app now provides the Phase 9 campaign setup, run visibility, results dashboard, account review, draft editing, and export workflow for Prospecting Agent.

## Dependencies added in Phase 6

- `@tanstack/react-query`
- `@tanstack/react-table`
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

- The app still does not send emails.
- The app still does not write to a CRM.
- Bulk review workflows are not in the frontend yet.

## Phase 7 browser validation

1. Create a campaign and upload `samples/devtools_companies.csv`
2. Start a run from the campaign detail page
3. Confirm the browser navigates to `/campaigns/{campaignId}/run?runId={runId}`
4. Confirm the run page shows status, account progress, todos, and activity
5. Wait for polling to stop after `completed`, `failed`, or `partial`

## Phase 8 browser validation

1. Open `http://localhost:3000`
2. Create a campaign if needed and upload `samples/devtools_companies.csv`
3. Start a run and wait for `completed` or `partial`
4. Open `/campaigns/{campaignId}/results`
5. Confirm rows are sorted by overall score
6. Use search, research status, quality status, and minimum score filters
7. Open one account from the results table
8. Confirm the account detail page shows research, evidence, timing signals, score breakdown, outreach draft, quality review, and risks
9. Confirm there are no approve, reject, edit, or export controls yet

## Phase 9 browser validation

1. Open `http://localhost:3000`
2. Create a campaign if needed and upload `samples/devtools_companies.csv`
3. Start a run and wait for `completed` or `partial`
4. Open `/campaigns/{campaignId}/accounts/{accountId}`
5. Change the review status and confirm it saves
6. Edit the draft subject or body and save
7. Confirm the quality review panel still renders after the edit
8. Open `/campaigns/{campaignId}/results`
9. Filter by review status and confirm the updated account appears
10. Create exports with the default approved-only selection
11. Download the generated CSV, Markdown report, and JSON archive
