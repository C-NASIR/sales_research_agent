from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.account import AccountDetailResponse, CampaignResultsResponse
from app.services import campaign_service, result_service

router = APIRouter(tags=["results"])


@router.get("/campaigns/{campaign_id}/results", response_model=CampaignResultsResponse)
def get_results(campaign_id: str, db: Session = Depends(get_db)) -> CampaignResultsResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return CampaignResultsResponse.model_validate(result_service.get_campaign_results(db, campaign_id))


@router.get("/campaigns/{campaign_id}/accounts/{account_id}", response_model=AccountDetailResponse)
def get_account_detail(campaign_id: str, account_id: str, db: Session = Depends(get_db)) -> AccountDetailResponse:
    detail = result_service.get_account_detail(db, campaign_id, account_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return AccountDetailResponse.model_validate(detail)
