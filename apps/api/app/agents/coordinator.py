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
from app.agents.real_research_workflow import get_real_research_context, real_account_researcher, real_signal_detector
from app.config import settings
from app.db.models import CampaignRun
from app.services import (
    account_service,
    campaign_service,
    event_service,
    result_service,
    run_service,
    todo_service,
)
from app.services.research_service import ensure_real_research_ready
from app.tools.research_synthesis import build_low_confidence_reports
from app.tools.web_search import SearchError
from app.workspace import readers, writers


def build_deep_agent():
    from deepagents import create_deep_agent
    from langchain.chat_models import init_chat_model

    model = init_chat_model(settings.model_name)
    return create_deep_agent(model=model, system_prompt="Prospecting Agent Phase 4 coordinator")


def _get_context_lists(account: dict) -> tuple[list[dict], list[dict], list[dict]]:
    context = get_real_research_context(account)
    if context is None:
        return [], [], []
    return context.search_results, context.scraped_sources, context.evidence_items


def _persist_account_reports(
    db: Session,
    campaign_id: str,
    run_id: str,
    account,
    research_report: dict,
    signal_report: dict,
) -> None:
    research_path = writers.write_research_report(campaign_id, account.id, research_report)
    result_service.upsert_research_report(db, account.id, research_report, str(research_path))
    event_service.record_event(
        db,
        campaign_id,
        "research_report_created",
        "Research report created",
        payload={
            "account_id": account.id,
            "company_name": account.company_name,
            "domain": account.domain,
            "source_count": len(research_report.get("sources") or []),
            "evidence_count": len(research_report.get("evidence") or []),
        },
        run_id=run_id,
    )

    signal_path = writers.write_signal_report(campaign_id, account.id, signal_report)
    result_service.upsert_signal_report(db, account.id, signal_report, str(signal_path))
    if settings.research_mode == "real":
        event_service.record_event(
            db,
            campaign_id,
            "research_synthesis_completed",
            "Research synthesis completed",
            payload={
                "account_id": account.id,
                "company_name": account.company_name,
                "domain": account.domain,
                "source_count": len(research_report.get("sources") or []),
                "evidence_count": len(research_report.get("evidence") or []),
            },
            run_id=run_id,
        )
        event_service.record_event(
            db,
            campaign_id,
            "signal_synthesis_completed",
            "Signal synthesis completed",
            payload={
                "account_id": account.id,
                "company_name": account.company_name,
                "domain": account.domain,
                "source_count": len(signal_report.get("sources") or []),
                "evidence_count": len(signal_report.get("signals") or []),
            },
            run_id=run_id,
        )
    event_service.record_event(
        db,
        campaign_id,
        "signal_report_created",
        "Signal report created",
        payload={
            "account_id": account.id,
            "company_name": account.company_name,
            "domain": account.domain,
            "source_count": len(signal_report.get("sources") or []),
            "evidence_count": len(signal_report.get("signals") or []),
        },
        run_id=run_id,
    )


def _persist_account_outputs(
    db: Session,
    campaign_id: str,
    run_id: str,
    brief: dict,
    normalized_account: dict,
    account,
    research_report: dict,
    signal_report: dict,
    icp: dict,
) -> None:
    _persist_account_reports(db, campaign_id, run_id, account, research_report, signal_report)

    score_report = fake_scoring_analyst(normalized_account, brief, research_report, signal_report, icp)
    score_path = writers.write_score_report(campaign_id, account.id, score_report)
    result_service.upsert_score_report(db, account.id, score_report, str(score_path))
    event_service.record_event(
        db,
        campaign_id,
        "score_report_created",
        "Score report created",
        payload={
            "account_id": account.id,
            "company_name": account.company_name,
            "domain": account.domain,
            "overall_score": score_report["overall_score"],
        },
        run_id=run_id,
    )
    event_service.record_event(
        db,
        campaign_id,
        "persona_recommended",
        "Recommended persona selected",
        payload={
            "account_id": account.id,
            "company_name": account.company_name,
            "domain": account.domain,
            "overall_score": score_report["overall_score"],
        },
        run_id=run_id,
    )
    event_service.record_event(
        db,
        campaign_id,
        "sales_angle_created",
        "Sales angle created",
        payload={
            "account_id": account.id,
            "company_name": account.company_name,
            "domain": account.domain,
            "overall_score": score_report["overall_score"],
        },
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
        payload={
            "account_id": account.id,
            "company_name": account.company_name,
            "domain": account.domain,
            "overall_score": score_report["overall_score"],
        },
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
        payload={
            "account_id": account.id,
            "company_name": account.company_name,
            "domain": account.domain,
            "overall_score": score_report["overall_score"],
            "quality_status": quality_review["quality_status"],
        },
        run_id=run_id,
    )
    if quality_review["quality_status"] == "flagged":
        event_service.record_event(
            db,
            campaign_id,
            "draft_flagged",
            "Outreach draft was flagged during review",
            payload={
                "account_id": account.id,
                "company_name": account.company_name,
                "domain": account.domain,
                "overall_score": score_report["overall_score"],
                "quality_status": quality_review["quality_status"],
            },
            run_id=run_id,
        )
    if quality_review["quality_status"] == "blocked":
        event_service.record_event(
            db,
            campaign_id,
            "draft_blocked",
            "Outreach draft was blocked during review",
            payload={
                "account_id": account.id,
                "company_name": account.company_name,
                "domain": account.domain,
                "overall_score": score_report["overall_score"],
                "quality_status": quality_review["quality_status"],
            },
            run_id=run_id,
        )


def run_campaign_workflow(db: Session, campaign_id: str, run_id: str) -> None:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise ValueError(f"Campaign not found: {campaign_id}")

    run = db.get(CampaignRun, run_id)
    if run is None:
        raise ValueError(f"Run not found: {run_id}")

    if settings.research_mode == "real":
        ensure_real_research_ready()

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
    todo_service.update_todo_status(campaign_id, "todo_icp", "in_progress")

    icp = fake_icp_strategist(brief)
    writers.write_icp(campaign_id, icp)
    event_service.record_event(db, campaign_id, "icp_created", "ICP plan created", run_id=run_id)
    todo_service.update_todo_status(campaign_id, "todo_icp", "completed")
    todo_service.update_todo_status(campaign_id, "todo_research", "in_progress")
    todo_service.update_todo_status(campaign_id, "todo_signals", "in_progress")
    todo_service.update_todo_status(campaign_id, "todo_scoring", "in_progress")
    todo_service.update_todo_status(campaign_id, "todo_outreach", "in_progress")

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
                payload={"account_id": account.id, "company_name": account.company_name, "domain": account.domain},
                run_id=run_id,
            )

            if settings.research_mode == "real":
                event_service.record_event(
                    db,
                    campaign_id,
                    "web_search_started",
                    "Public web search started",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": 0,
                        "evidence_count": 0,
                    },
                    run_id=run_id,
                )
                event_service.record_event(
                    db,
                    campaign_id,
                    "web_scrape_started",
                    "Public page scraping started",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": 0,
                        "evidence_count": 0,
                    },
                    run_id=run_id,
                )
                research_report = real_account_researcher(normalized_account, icp, brief)
                signal_report = real_signal_detector(normalized_account, research_report, icp, brief)
                search_results, scraped_sources, evidence_items = _get_context_lists(normalized_account)
                event_service.record_event(
                    db,
                    campaign_id,
                    "web_search_completed",
                    "Public web search completed",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": len(search_results),
                        "evidence_count": len(evidence_items),
                    },
                    run_id=run_id,
                )
                event_service.record_event(
                    db,
                    campaign_id,
                    "web_scrape_completed",
                    "Public page scraping completed",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": len([item for item in scraped_sources if item.get("success")]),
                        "evidence_count": len(evidence_items),
                    },
                    run_id=run_id,
                )
                event_service.record_event(
                    db,
                    campaign_id,
                    "evidence_extracted",
                    "Evidence extracted from public sources",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": len(scraped_sources),
                        "evidence_count": len(evidence_items),
                    },
                    run_id=run_id,
                )
                if not evidence_items:
                    event_service.record_event(
                        db,
                        campaign_id,
                        "research_low_confidence",
                        "Public research produced low-confidence evidence",
                        payload={
                            "account_id": account.id,
                            "company_name": account.company_name,
                            "domain": account.domain,
                            "source_count": len(scraped_sources),
                            "evidence_count": 0,
                        },
                        run_id=run_id,
                    )
                writers.write_research_sources(
                    campaign_id,
                    account.id,
                    {"search_results": search_results, "scraped_sources": scraped_sources},
                )
            else:
                research_report = fake_account_researcher(normalized_account, icp)
                signal_report = fake_signal_detector(normalized_account, research_report, icp)
            _persist_account_outputs(
                db,
                campaign_id,
                run_id,
                brief,
                normalized_account,
                account,
                research_report,
                signal_report,
                icp,
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
        except SearchError as exc:
            research_report, signal_report = build_low_confidence_reports(
                normalized_account,
                f"Search failed: {exc}",
            )
            _persist_account_outputs(
                db,
                campaign_id,
                run_id,
                brief,
                normalized_account,
                account,
                research_report,
                signal_report,
                icp,
            )
            account_service.update_account_research_status(db, account, "completed")
            event_service.record_event(
                db,
                campaign_id,
                "research_tool_failed",
                "Search tool failed for account",
                payload={
                    "account_id": account.id,
                    "company_name": account.company_name,
                    "domain": account.domain,
                    "source_count": len(research_report.get("sources") or []),
                    "evidence_count": len(research_report.get("evidence") or []),
                },
                run_id=run_id,
            )
            event_service.record_event(
                db,
                campaign_id,
                "research_low_confidence",
                "Fallback low-confidence reports were written after search failure",
                payload={
                    "account_id": account.id,
                    "company_name": account.company_name,
                    "domain": account.domain,
                    "source_count": len(research_report.get("sources") or []),
                    "evidence_count": len(research_report.get("evidence") or []),
                },
                run_id=run_id,
            )
            event_service.record_event(
                db,
                campaign_id,
                "account_research_failed",
                "Account research tool failed but low-confidence reports were written",
                payload={
                    "account_id": account.id,
                    "company_name": account.company_name,
                    "domain": account.domain,
                    "source_count": len(research_report.get("sources") or []),
                    "evidence_count": len(research_report.get("evidence") or []),
                    "error": str(exc),
                },
                run_id=run_id,
            )
            success_count += 1
        except Exception as exc:
            if settings.research_mode == "real":
                search_results, scraped_sources, evidence_items = _get_context_lists(normalized_account)
                if search_results or scraped_sources:
                    writers.write_research_sources(
                        campaign_id,
                        account.id,
                        {"search_results": search_results, "scraped_sources": scraped_sources},
                    )
                research_report, signal_report = build_low_confidence_reports(
                    normalized_account,
                    f"Research tools produced an error: {exc}",
                    search_results=search_results,
                    scraped_sources=scraped_sources,
                )
                _persist_account_outputs(
                    db,
                    campaign_id,
                    run_id,
                    brief,
                    normalized_account,
                    account,
                    research_report,
                    signal_report,
                    icp,
                )
                account_service.update_account_research_status(db, account, "completed")
                event_service.record_event(
                    db,
                    campaign_id,
                    "research_tool_failed",
                    "Research or scrape tool failed for account",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": len(research_report.get("sources") or []),
                        "evidence_count": len(research_report.get("evidence") or []),
                    },
                    run_id=run_id,
                )
                event_service.record_event(
                    db,
                    campaign_id,
                    "research_low_confidence",
                    "Low-confidence reports were written after a research tool error",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": len(research_report.get("sources") or []),
                        "evidence_count": len(research_report.get("evidence") or []),
                    },
                    run_id=run_id,
                )
                event_service.record_event(
                    db,
                    campaign_id,
                    "account_research_failed",
                    "Account research encountered an error but fallback reports were produced",
                    payload={
                        "account_id": account.id,
                        "company_name": account.company_name,
                        "domain": account.domain,
                        "source_count": len(research_report.get("sources") or []),
                        "evidence_count": len(research_report.get("evidence") or []),
                        "error": str(exc),
                    },
                    run_id=run_id,
                )
                success_count += 1
            else:
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
        todo_service.update_todo_status(campaign_id, "todo_research", "failed")
        todo_service.update_todo_status(campaign_id, "todo_signals", "failed")
        todo_service.update_todo_status(campaign_id, "todo_scoring", "failed")
        todo_service.update_todo_status(campaign_id, "todo_outreach", "failed")
    elif failed_count > 0:
        final_status = "partial"
        final_event_type = "run_partial"
        final_message = "Campaign run completed with partial failures"
        todo_service.update_todo_status(campaign_id, "todo_research", "completed")
        todo_service.update_todo_status(campaign_id, "todo_signals", "completed")
        todo_service.update_todo_status(campaign_id, "todo_scoring", "completed")
        todo_service.update_todo_status(campaign_id, "todo_outreach", "completed")
    else:
        final_status = "completed"
        final_event_type = "run_completed"
        final_message = "Campaign run completed"
        todo_service.update_todo_status(campaign_id, "todo_research", "completed")
        todo_service.update_todo_status(campaign_id, "todo_signals", "completed")
        todo_service.update_todo_status(campaign_id, "todo_scoring", "completed")
        todo_service.update_todo_status(campaign_id, "todo_outreach", "completed")

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
