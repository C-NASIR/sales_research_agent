from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResearchReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    account_id: str | None = None
    company_name: str | None = None
    domain: str | None = None
    company_summary: str | None
    business_model: str | None = None
    fit_claims: list[Any] | None
    evidence: list[Any] | None
    risks: list[Any] | None
    confidence: float | None
    workspace_file: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SignalReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    account_id: str | None = None
    company_name: str | None = None
    domain: str | None = None
    signals: list[Any] | None
    timing_score: float | None
    why_now: str | None
    confidence: float | None
    workspace_file: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
