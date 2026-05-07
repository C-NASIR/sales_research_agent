# Data model

The project now has a Phase 4 SQLite-backed data model plus a campaign workspace on disk. The schema is intentionally simple and is designed to support MVP research, scoring, review, and later export phases.

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

Phase 9 uses `review_status` as a supervised workflow field with these allowed values:

- `unreviewed`
- `approved`
- `rejected`
- `needs_edit`
- `not_enough_evidence`

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

Phase 3 and Phase 4 create a `CampaignRun` row for every run request and update it to `running`, `completed`, `partial`, or `failed`.

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
- `business_model`
- `fit_claims`
- `evidence`
- `risks`
- `confidence`
- `workspace_file`
- `created_at`
- `updated_at`

Phase 4 preserves public source URLs inside `fit_claims` and `evidence`. The `sources` collection is stored in workspace JSON, while SQLite keeps the source-backed evidence payloads.

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

Phase 4 preserves source URLs inside signal items stored in the `signals` JSON field.

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
- `recommended_persona`
- `sales_angle`
- `workspace_file`
- `created_at`
- `updated_at`

## OutreachDraft

- `id`
- `account_id`
- `subject`
- `body`
- `personalization_source`
- `personalization_source_url`
- `sales_angle`
- `risk_notes`
- `quality_status`
- `workspace_file`
- `created_at`
- `updated_at`

Phase 9 allows the user to update `subject`, `body`, `personalization_source`, `personalization_source_url`, and `sales_angle`, then reruns quality review against the edited draft.

## ExportFile

- `id`
- `campaign_id`
- `export_type`
- `file_path`
- `created_at`

Phase 9 creates or updates one `ExportFile` row per generated export artifact:

- `prospects_csv`
- `campaign_report_md`
- `archive_json`

## Workspace files

Phase 2 also writes campaign input artifacts under:

- `data/campaigns/{campaign_id}/input/brief.json`
- `data/campaigns/{campaign_id}/input/uploaded_companies.csv`
- `data/campaigns/{campaign_id}/input/normalized_accounts.json`
- `data/campaigns/{campaign_id}/input/upload_report.json`

Phase 3 and Phase 4 write run artifacts under:

- `data/campaigns/{campaign_id}/plan/todos.json`
- `data/campaigns/{campaign_id}/plan/icp.json`
- `data/campaigns/{campaign_id}/research/{account_id}.json`
- `data/campaigns/{campaign_id}/research/sources/{account_id}.json`
- `data/campaigns/{campaign_id}/signals/{account_id}.json`
- `data/campaigns/{campaign_id}/scores/{account_id}.json`
- `data/campaigns/{campaign_id}/outreach/{account_id}.json`
- `data/campaigns/{campaign_id}/review/{account_id}.json`
- `data/campaigns/{campaign_id}/exports/prospects.csv`
- `data/campaigns/{campaign_id}/exports/campaign_report.md`
- `data/campaigns/{campaign_id}/exports/archive.json`

No migration framework exists yet. If an older local SQLite database does not match the current SQLAlchemy models during MVP development, the expected recovery path is to delete the local database and rerun the app. Phase 5 adds `personalization_source_url` to `OutreachDraft`, so older local SQLite files should be recreated.
