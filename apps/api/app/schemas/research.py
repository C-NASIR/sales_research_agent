from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResearchReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    company_summary: str | None
    fit_claims: list[Any] | None
    evidence: list[Any] | None
    risks: list[Any] | None
    confidence: float | None
    workspace_file: str | None
    created_at: datetime
    updated_at: datetime


class SignalReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    signals: list[Any] | None
    timing_score: float | None
    why_now: str | None
    confidence: float | None
    workspace_file: str | None
    created_at: datetime
    updated_at: datetime
