from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ScoreReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    fit_score: float | None
    timing_score: float | None
    confidence_score: float | None
    persona_score: float | None
    overall_score: float | None
    score_explanation: str | None
    score_breakdown: dict[str, Any] | None
    workspace_file: str | None
    created_at: datetime
    updated_at: datetime
