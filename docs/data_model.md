# Data model

The project now has a Phase 2 SQLite-backed data model plus a campaign workspace on disk. The schema is intentionally simple and is designed to support later research, scoring, review, and export phases.

## Campaign

- `id`
- `name`
- `product_description`
- `ideal_customer_profile`
- `pain_statement`
- `target_persona`
- `tone`
- `max_accounts`
- `status`
- `workspace_path`
- `created_at`
- `updated_at`

Related entities: accounts, runs, events, exports.

## Account

- `id`
- `campaign_id`
- `company_name`
- `domain`
- `research_status`
- `review_status`
- `created_at`
- `updated_at`

Related entities: campaign, research_report, signal_report, score_report, outreach_draft.

Phase 2 creates `Account` rows from uploaded CSV files after domain normalization and duplicate filtering.

## CampaignRun

- `id`
- `campaign_id`
- `status`
- `started_at`
- `completed_at`
- `error_message`
- `agent_thread_id`
- `created_at`
- `updated_at`

## ActivityEvent

- `id`
- `campaign_id`
- `run_id`
- `type`
- `message`
- `payload`
- `created_at`

## ResearchReport

- `id`
- `account_id`
- `company_summary`
- `fit_claims`
- `evidence`
- `risks`
- `confidence`
- `workspace_file`
- `created_at`
- `updated_at`

## SignalReport

- `id`
- `account_id`
- `signals`
- `timing_score`
- `why_now`
- `confidence`
- `workspace_file`
- `created_at`
- `updated_at`

## ScoreReport

- `id`
- `account_id`
- `fit_score`
- `timing_score`
- `confidence_score`
- `persona_score`
- `overall_score`
- `score_explanation`
- `score_breakdown`
- `workspace_file`
- `created_at`
- `updated_at`

## OutreachDraft

- `id`
- `account_id`
- `subject`
- `body`
- `personalization_source`
- `sales_angle`
- `risk_notes`
- `quality_status`
- `workspace_file`
- `created_at`
- `updated_at`

## ExportFile

- `id`
- `campaign_id`
- `export_type`
- `file_path`
- `created_at`

## Workspace files

Phase 2 also writes campaign input artifacts under:

- `data/campaigns/{campaign_id}/input/brief.json`
- `data/campaigns/{campaign_id}/input/uploaded_companies.csv`
- `data/campaigns/{campaign_id}/input/normalized_accounts.json`
- `data/campaigns/{campaign_id}/input/upload_report.json`
