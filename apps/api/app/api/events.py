from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_campaign_or_404
from app.db.session import get_db
from app.schemas.event import ActivityEventListResponse, ActivityEventResponse
from app.services import event_service

router = APIRouter(tags=["events"])


@router.get("/campaigns/{campaign_id}/events", response_model=ActivityEventListResponse)
def list_events(campaign_id: str, db: Session = Depends(get_db)) -> ActivityEventListResponse:
    get_campaign_or_404(db, campaign_id)
    events = event_service.list_events_for_campaign(db, campaign_id)
    return ActivityEventListResponse(events=[ActivityEventResponse.model_validate(item) for item in events])
