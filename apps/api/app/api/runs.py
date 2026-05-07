from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.run import CampaignRunCreateResponse, CampaignRunResponse
from app.services import run_service

router = APIRouter(tags=["runs"])


@router.post("/campaigns/{campaign_id}/runs", response_model=CampaignRunCreateResponse)
def create_run(campaign_id: str, db: Session = Depends(get_db)) -> CampaignRunCreateResponse:
    try:
        run = run_service.run_campaign_now(db, campaign_id)
    except run_service.RunServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return CampaignRunCreateResponse.model_validate(run)


@router.get("/campaigns/{campaign_id}/runs/{run_id}", response_model=CampaignRunResponse)
def get_run(campaign_id: str, run_id: str, db: Session = Depends(get_db)) -> CampaignRunResponse:
    run = run_service.get_campaign_run(db, campaign_id, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return CampaignRunResponse.model_validate(run)
