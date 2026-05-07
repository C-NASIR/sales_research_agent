from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.account import AccountListResponse, AccountResponse
from app.services import account_service, campaign_service

router = APIRouter(tags=["accounts"])


@router.get("/campaigns/{campaign_id}/accounts", response_model=AccountListResponse)
def list_accounts(campaign_id: str, db: Session = Depends(get_db)) -> AccountListResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    accounts = account_service.list_accounts_for_campaign(db, campaign_id)
    return AccountListResponse(accounts=[AccountResponse.model_validate(item) for item in accounts])
