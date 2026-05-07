from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_account_or_404, get_campaign_or_404
from app.db.session import get_db
from app.schemas.outreach import OutreachDraftResponse, OutreachDraftUpdate
from app.schemas.review import ReviewStatusResponse, ReviewStatusUpdate
from app.services import review_service

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
    get_campaign_or_404(db, campaign_id)

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
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
    get_campaign_or_404(db, campaign_id)
    get_account_or_404(db, campaign_id, account_id)

    try:
        draft = review_service.update_outreach_draft(db, campaign_id, account_id, input)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outreach draft not found.")
    return OutreachDraftResponse.model_validate(draft)
