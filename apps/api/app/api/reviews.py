from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.outreach import OutreachDraftResponse, OutreachDraftUpdate
from app.schemas.review import ReviewStatusResponse, ReviewStatusUpdate
from app.services import account_service, campaign_service, review_service

router = APIRouter(tags=["reviews"])


@router.patch(
    "/campaigns/{campaign_id}/accounts/{account_id}/review",
    response_model=ReviewStatusResponse,
)
def update_account_review_status(
    campaign_id: str,
    account_id: str,
    input: ReviewStatusUpdate,
    db: Session = Depends(get_db),
) -> ReviewStatusResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    try:
        result = review_service.update_account_review_status(
            db,
            campaign_id,
            account_id,
            input.review_status,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return ReviewStatusResponse.model_validate(result)


@router.patch(
    "/campaigns/{campaign_id}/accounts/{account_id}/draft",
    response_model=OutreachDraftResponse,
)
def update_outreach_draft(
    campaign_id: str,
    account_id: str,
    input: OutreachDraftUpdate,
    db: Session = Depends(get_db),
) -> OutreachDraftResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    account = account_service.get_account(db, campaign_id, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    try:
        draft = review_service.update_outreach_draft(db, campaign_id, account_id, input)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outreach draft not found")
    return OutreachDraftResponse.model_validate(draft)
