from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.fake_workflow import (
    build_fake_todos,
    fake_account_researcher,
    fake_compliance_reviewer,
    fake_icp_strategist,
    fake_outreach_writer,
    fake_scoring_analyst,
    fake_signal_detector,
)
from app.config import settings
from app.db.models import CampaignRun
from app.services import account_service, campaign_service, event_service, result_service, run_service, workspace_service
from app.workspace import readers, writers


def build_deep_agent():
    from deepagents import create_deep_agent
    from langchain.chat_models import init_chat_model

    model = init_chat_model(settings.model_name)
    return create_deep_agent(model=model, system_prompt="Prospecting Agent Phase 3 coordinator")


def run_campaign_workflow(db: Session, campaign_id: str, run_id: str) -> None:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise ValueError(f"Campaign not found: {campaign_id}")

    run = db.get(CampaignRun, run_id)
    if run is None:
        raise ValueError(f"Run not found: {run_id}")

    brief = readers.read_campaign_brief(campaign_id)
    normalized_accounts = readers.read_normalized_accounts(campaign_id)
    if not normalized_accounts:
        raise ValueError("No normalized accounts found in workspace")

    event_service.record_event(db, campaign_id, "run_started", "Campaign run started", run_id=run_id)
    run_service.update_run_status(db, run, "running", started=True)
    campaign_service.update_campaign_status(db, campaign_id, "running")

    todos = build_fake_todos()
    writers.write_todos(campaign_id, todos)
    event_service.record_event(db, campaign_id, "todo_created", "Run todo plan created", run_id=run_id)

    icp = fake_icp_strategist(brief)
    writers.write_icp(campaign_id, icp)
    event_service.record_event(db, campaign_id, "icp_created", "ICP plan created", run_id=run_id)

    success_count = 0
    failed_count = 0

    for normalized_account in normalized_accounts:
        account = account_service.get_account_by_domain(db, campaign_id, normalized_account["domain"])
        if account is None:
            failed_count += 1
            event_service.record_event(
                db,
                campaign_id,
                "account_research_failed",
                "Account row missing for normalized domain",
                payload={"domain": normalized_account["domain"]},
                run_id=run_id,
            )
            continue

        try:
            account_service.update_account_research_status(db, account, "researching")
            event_service.record_event(
                db,
                campaign_id,
                "account_research_started",
                "Account research started",
                payload={"account_id": account.id, "domain": account.domain},
                run_id=run_id,
            )

            research_report = fake_account_researcher(normalized_account, icp)
            research_path = writers.write_research_report(campaign_id, account.id, research_report)
            result_service.upsert_research_report(db, account.id, research_report, str(research_path))
            event_service.record_event(
                db,
                campaign_id,
                "research_report_created",
                "Research report created",
                payload={"account_id": account.id},
                run_id=run_id,
            )

            signal_report = fake_signal_detector(normalized_account, research_report, icp)
            signal_path = writers.write_signal_report(campaign_id, account.id, signal_report)
            result_service.upsert_signal_report(db, account.id, signal_report, str(signal_path))
            event_service.record_event(
                db,
                campaign_id,
                "signal_report_created",
                "Signal report created",
                payload={"account_id": account.id},
                run_id=run_id,
            )

            score_report = fake_scoring_analyst(normalized_account, research_report, signal_report, icp)
            score_path = writers.write_score_report(campaign_id, account.id, score_report)
            result_service.upsert_score_report(db, account.id, score_report, str(score_path))
            event_service.record_event(
                db,
                campaign_id,
                "score_report_created",
                "Score report created",
                payload={"account_id": account.id},
                run_id=run_id,
            )

            outreach_draft = fake_outreach_writer(brief, normalized_account, research_report, signal_report, score_report)
            outreach_path = writers.write_outreach_draft(campaign_id, account.id, outreach_draft)
            result_service.upsert_outreach_draft(db, account.id, outreach_draft, str(outreach_path))
            event_service.record_event(
                db,
                campaign_id,
                "draft_created",
                "Outreach draft created",
                payload={"account_id": account.id},
                run_id=run_id,
            )

            quality_review = fake_compliance_reviewer(outreach_draft, research_report, signal_report)
            writers.write_quality_review(campaign_id, account.id, quality_review)
            result_service.update_outreach_quality_status(db, account.id, quality_review["quality_status"])
            event_service.record_event(
                db,
                campaign_id,
                "quality_review_created",
                "Quality review created",
                payload={"account_id": account.id, "quality_status": quality_review["quality_status"]},
                run_id=run_id,
            )

            account_service.update_account_research_status(db, account, "completed")
            event_service.record_event(
                db,
                campaign_id,
                "account_research_completed",
                "Account research completed",
                payload={"account_id": account.id},
                run_id=run_id,
            )
            success_count += 1
        except Exception as exc:
            account_service.update_account_research_status(db, account, "failed")
            event_service.record_event(
                db,
                campaign_id,
                "account_research_failed",
                "Account research failed",
                payload={"account_id": account.id, "error": str(exc)},
                run_id=run_id,
            )
            failed_count += 1

    if success_count == 0:
        final_status = "failed"
        final_event_type = "run_failed"
        final_message = "Campaign run failed"
    elif failed_count > 0:
        final_status = "partial"
        final_event_type = "run_partial"
        final_message = "Campaign run completed with partial failures"
    else:
        final_status = "completed"
        final_event_type = "run_completed"
        final_message = "Campaign run completed"

    run_service.update_run_status(db, run, final_status, completed=True)
    campaign_service.update_campaign_status(db, campaign_id, final_status)
    event_service.record_event(
        db,
        campaign_id,
        final_event_type,
        final_message,
        payload={"succeeded": success_count, "failed": failed_count},
        run_id=run_id,
    )
