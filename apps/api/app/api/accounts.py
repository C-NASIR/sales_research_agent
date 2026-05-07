from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_campaign_or_404
from app.db.session import get_db
from app.schemas.account import AccountListResponse, AccountResponse
from app.services import account_service

router = APIRouter(tags=["accounts"])


@router.get("/campaigns/{campaign_id}/accounts", response_model=AccountListResponse)
def list_accounts(campaign_id: str, db: Session = Depends(get_db)) -> AccountListResponse:
    get_campaign_or_404(db, campaign_id)
    accounts = account_service.list_accounts_for_campaign(db, campaign_id)
    return AccountListResponse(accounts=[AccountResponse.model_validate(item) for item in accounts])
