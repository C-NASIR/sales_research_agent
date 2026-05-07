from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.campaign import CampaignCreate, CampaignListResponse, CampaignResponse
from app.services import campaign_service, event_service

router = APIRouter(tags=["campaigns"])


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)) -> CampaignResponse:
    campaign = campaign_service.create_campaign(db, payload)
    event_service.record_event(
        db,
        campaign_id=campaign.id,
        type="campaign_created",
        message="Campaign created",
    )
    return CampaignResponse.model_validate(campaign)


@router.get("/campaigns", response_model=CampaignListResponse)
def list_campaigns(db: Session = Depends(get_db)) -> CampaignListResponse:
    campaigns = campaign_service.list_campaigns(db)
    return CampaignListResponse(campaigns=[CampaignResponse.model_validate(item) for item in campaigns])


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)) -> CampaignResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return CampaignResponse.model_validate(campaign)
