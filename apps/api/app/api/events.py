from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.event import ActivityEventListResponse, ActivityEventResponse
from app.services import campaign_service, event_service

router = APIRouter(tags=["events"])


@router.get("/campaigns/{campaign_id}/events", response_model=ActivityEventListResponse)
def list_events(campaign_id: str, db: Session = Depends(get_db)) -> ActivityEventListResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    events = event_service.list_events_for_campaign(db, campaign_id)
    return ActivityEventListResponse(events=[ActivityEventResponse.model_validate(item) for item in events])
