from __future__ import annotations

from dataclasses import dataclass

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CampaignRun
from app.db.session import SessionLocal
from app.services import campaign_service, event_service
from app.services.research_service import ResearchConfigurationError
from app.utils.ids import new_id
from app.utils.timestamps import utc_now


@dataclass
class RunServiceError(Exception):
    status_code: int
    detail: str


def create_campaign_run(db: Session, campaign_id: str) -> CampaignRun:
    run_id = new_id("run")
    now = utc_now()
    run = CampaignRun(
        id=run_id,
        campaign_id=campaign_id,
        status="pending",
        started_at=None,
        completed_at=None,
        error_message=None,
        agent_thread_id=run_id,
        created_at=now,
        updated_at=now,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_campaign_run(db: Session, campaign_id: str, run_id: str) -> CampaignRun | None:
    run = db.get(CampaignRun, run_id)
    if run is None or run.campaign_id != campaign_id:
        return None
    return run


def list_campaign_runs(db: Session, campaign_id: str) -> list[CampaignRun]:
    statement = (
        select(CampaignRun)
        .where(CampaignRun.campaign_id == campaign_id)
        .order_by(CampaignRun.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_latest_campaign_run(db: Session, campaign_id: str) -> CampaignRun | None:
    runs = list_campaign_runs(db, campaign_id)
    return runs[0] if runs else None


def get_active_campaign_run(db: Session, campaign_id: str) -> CampaignRun | None:
    statement = (
        select(CampaignRun)
        .where(
            CampaignRun.campaign_id == campaign_id,
            CampaignRun.status.in_(["pending", "running"]),
        )
        .order_by(CampaignRun.created_at.desc())
    )
    return db.scalars(statement).first()


def start_campaign_run_background(
    background_tasks: BackgroundTasks,
    db: Session,
    campaign_id: str,
) -> CampaignRun:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise RunServiceError(status_code=404, detail="Campaign not found")
    if campaign.status == "draft":
        raise RunServiceError(status_code=400, detail="Campaign is still draft and has no ready input state")
    if not campaign.accounts:
        raise RunServiceError(status_code=400, detail="Campaign has no accounts to process")
    if get_active_campaign_run(db, campaign_id) is not None:
        raise RunServiceError(status_code=400, detail="A campaign run is already in progress.")

    run = create_campaign_run(db, campaign_id)
    campaign_service.update_campaign_status(db, campaign_id, "running")
    background_tasks.add_task(execute_campaign_run, run.id, campaign_id)
    return run


def execute_campaign_run(run_id: str, campaign_id: str) -> None:
    from app.agents.coordinator import run_campaign_workflow
    from app.services import account_service

    db = SessionLocal()
    try:
        run = get_campaign_run(db, campaign_id, run_id)
        if run is None:
            return

        account_service.update_all_account_research_statuses(db, campaign_id, "pending")
        run_campaign_workflow(db, campaign_id, run_id)
    except ResearchConfigurationError as exc:
        _mark_run_failed(db, campaign_id, run_id, str(exc), configuration_error=True)
    except Exception as exc:
        _mark_run_failed(db, campaign_id, run_id, str(exc), configuration_error=False)
    finally:
        db.close()


def update_run_status(
    db: Session,
    run: CampaignRun,
    status: str,
    *,
    started: bool = False,
    completed: bool = False,
    error_message: str | None = None,
) -> CampaignRun:
    now = utc_now()
    run.status = status
    run.updated_at = now
    if started and run.started_at is None:
        run.started_at = now
    if completed:
        run.completed_at = now
    if error_message is not None:
        run.error_message = error_message
    db.commit()
    db.refresh(run)
    return run


def _mark_run_failed(
    db: Session,
    campaign_id: str,
    run_id: str,
    error_message: str,
    *,
    configuration_error: bool,
) -> None:
    run = get_campaign_run(db, campaign_id, run_id)
    if run is None:
        return

    update_run_status(db, run, "failed", completed=True, error_message=error_message)
    campaign_service.update_campaign_status(db, campaign_id, "failed")
    if configuration_error:
        event_service.record_event(
            db,
            campaign_id,
            "research_tool_failed",
            "Real research mode is not configured correctly",
            payload={"error": error_message},
            run_id=run_id,
        )
    event_service.record_event(
        db,
        campaign_id,
        "run_failed",
        "Campaign run failed",
        payload={"error": error_message},
        run_id=run_id,
    )
