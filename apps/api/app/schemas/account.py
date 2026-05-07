from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.outreach import OutreachDraftResponse, QualityReviewResponse
from app.schemas.research import ResearchReportResponse, SignalReportResponse
from app.schemas.scoring import ScoreReportResponse


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    company_name: str
    domain: str
    research_status: str
    review_status: str
    created_at: datetime
    updated_at: datetime


class AccountListResponse(BaseModel):
    accounts: list[AccountResponse]


class CampaignResultAccountResponse(BaseModel):
    account_id: str
    company_name: str
    domain: str
    overall_score: int | None
    fit_score: int | None
    timing_score: int | None
    confidence_score: int | None
    persona_score: int | None
    recommended_persona: str | None
    sales_angle: str | None
    review_status: str
    research_status: str
    draft_quality_status: str | None


class CampaignResultsResponse(BaseModel):
    campaign_id: str
    status: str
    accounts: list[CampaignResultAccountResponse]


class AccountDetailResponse(BaseModel):
    account: AccountResponse
    research_report: ResearchReportResponse | None
    signal_report: SignalReportResponse | None
    score_report: ScoreReportResponse | None
    outreach_draft: OutreachDraftResponse | None
    quality_review: QualityReviewResponse | None
