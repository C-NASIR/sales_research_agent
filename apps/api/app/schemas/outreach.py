from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class OutreachDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    account_id: str | None = None
    company_name: str | None = None
    domain: str | None = None
    subject: str | None
    body: str | None
    personalization_source: str | None
    sales_angle: str | None
    risk_notes: list[Any] | None
    quality_status: str | None = None
    workspace_file: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class QualityReviewResponse(BaseModel):
    company_name: str
    domain: str
    quality_status: str
    issues: list[str]
    blocked_reasons: list[str]
    recommended_edits: list[str]
