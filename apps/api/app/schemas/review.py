from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

REVIEW_STATUSES = (
    "unreviewed",
    "approved",
    "rejected",
    "needs_edit",
    "not_enough_evidence",
)


class ReviewStatusUpdate(BaseModel):
    review_status: str


class ReviewStatusResponse(BaseModel):
    account_id: str
    campaign_id: str
    review_status: str
    updated_at: datetime
