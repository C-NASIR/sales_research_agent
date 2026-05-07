from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.coordinator import run_campaign_workflow
from app.db.models import CampaignRun
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


def run_campaign_now(db: Session, campaign_id: str) -> CampaignRun:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise RunServiceError(status_code=404, detail="Campaign not found")
    if campaign.status == "draft":
        raise RunServiceError(status_code=400, detail="Campaign is still draft and has no ready input state")
    if not campaign.accounts:
        raise RunServiceError(status_code=400, detail="Campaign has no accounts to process")

    run = create_campaign_run(db, campaign_id)
    try:
        run_campaign_workflow(db, campaign_id, run.id)
        refreshed = get_campaign_run(db, campaign_id, run.id)
        if refreshed is None:
            raise RunServiceError(status_code=500, detail="Run record disappeared during execution")
        return refreshed
    except ResearchConfigurationError as exc:
        update_run_status(db, run, "failed", completed=True, error_message=str(exc))
        campaign_service.update_campaign_status(db, campaign_id, "failed")
        event_service.record_event(
            db,
            campaign_id,
            "research_tool_failed",
            "Real research mode is not configured correctly",
            payload={"error": str(exc)},
            run_id=run.id,
        )
        event_service.record_event(
            db,
            campaign_id,
            "run_failed",
            "Campaign run failed",
            payload={"error": str(exc)},
            run_id=run.id,
        )
        raise RunServiceError(status_code=500, detail=str(exc)) from exc
    except RunServiceError:
        raise
    except Exception as exc:
        update_run_status(db, run, "failed", completed=True, error_message=str(exc))
        campaign_service.update_campaign_status(db, campaign_id, "failed")
        event_service.record_event(
            db,
            campaign_id,
            "run_failed",
            "Campaign run failed with an unhandled error",
            payload={"error": str(exc)},
            run_id=run.id,
        )
        raise RunServiceError(status_code=500, detail=str(exc)) from exc


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
