from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator

REVIEW_STATUSES = (
    "unreviewed",
    "approved",
    "rejected",
    "needs_edit",
    "not_enough_evidence",
)


class ReviewStatusUpdate(BaseModel):
    review_status: str

    @field_validator("review_status")
    @classmethod
    def validate_review_status(cls, value: str) -> str:
        normalized = value.strip()
        if normalized not in REVIEW_STATUSES:
            raise ValueError("Invalid review status.")
        return normalized


class ReviewStatusResponse(BaseModel):
    account_id: str
    campaign_id: str
    review_status: str
    updated_at: datetime
