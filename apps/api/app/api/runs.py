from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.run import CampaignRunCreateResponse, CampaignRunListResponse, CampaignRunResponse
from app.services import campaign_service, run_service

router = APIRouter(tags=["runs"])


@router.post("/campaigns/{campaign_id}/runs", response_model=CampaignRunCreateResponse)
def create_run(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> CampaignRunCreateResponse:
    try:
        run = run_service.start_campaign_run_background(background_tasks, db, campaign_id)
    except run_service.RunServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return CampaignRunCreateResponse.model_validate(run)


@router.get("/campaigns/{campaign_id}/runs", response_model=CampaignRunListResponse)
def list_runs(campaign_id: str, db: Session = Depends(get_db)) -> CampaignRunListResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    runs = run_service.list_campaign_runs(db, campaign_id)
    return CampaignRunListResponse(runs=[CampaignRunResponse.model_validate(run) for run in runs])


@router.get("/campaigns/{campaign_id}/runs/latest", response_model=CampaignRunResponse)
def get_latest_run(campaign_id: str, db: Session = Depends(get_db)) -> CampaignRunResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    run = run_service.get_latest_campaign_run(db, campaign_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return CampaignRunResponse.model_validate(run)


@router.get("/campaigns/{campaign_id}/runs/{run_id}", response_model=CampaignRunResponse)
def get_run(campaign_id: str, run_id: str, db: Session = Depends(get_db)) -> CampaignRunResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    run = run_service.get_campaign_run(db, campaign_id, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return CampaignRunResponse.model_validate(run)
