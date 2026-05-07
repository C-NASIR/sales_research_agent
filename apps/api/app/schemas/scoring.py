from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ScoreReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    account_id: str | None = None
    company_name: str | None = None
    domain: str | None = None
    fit_score: int | None
    timing_score: int | None
    confidence_score: int | None
    persona_score: int | None
    overall_score: int | None
    score_explanation: str | None
    score_breakdown: dict[str, Any] | None
    recommended_persona: str | None = None
    sales_angle: str | None = None
    workspace_file: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
