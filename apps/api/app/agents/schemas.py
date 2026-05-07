from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.source import SearchResult


class TodoItem(BaseModel):
    id: str
    title: str
    status: str


class ICPProfile(BaseModel):
    target_company_criteria: list[str]
    target_personas: list[str]
    positive_signals: list[str]
    negative_signals: list[str]
    scoring_rubric: dict[str, Any]


class EvidenceItem(BaseModel):
    claim: str
    evidence: str
    source_url: str
    source_title: str | None = None
    confidence: str
    evidence_type: str = "unknown"


class RiskItem(BaseModel):
    risk: str
    reason: str
    confidence: str


class ResearchReportData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: str
    domain: str
    company_summary: str
    business_model: str
    fit_claims: list[EvidenceItem]
    evidence: list[EvidenceItem]
    risks: list[RiskItem]
    confidence: int
    sources: list[SearchResult | dict[str, Any]]


class SignalItem(BaseModel):
    type: str
    description: str
    why_it_matters: str
    source_url: str
    confidence: str


class SignalReportData(BaseModel):
    company_name: str
    domain: str
    signals: list[SignalItem]
    timing_score: int
    why_now: str
    confidence: int
    sources: list[SearchResult | dict[str, Any]]


class ScoreReportData(BaseModel):
    company_name: str
    domain: str
    fit_score: int
    timing_score: int
    confidence_score: int
    persona_score: int
    overall_score: int
    score_explanation: str
    score_breakdown: dict[str, Any]
    recommended_persona: str
    sales_angle: str


class OutreachDraftData(BaseModel):
    company_name: str
    domain: str
    subject: str
    body: str
    personalization_source: str
    personalization_source_url: str | None = None
    sales_angle: str
    risk_notes: list[str]


class QualityReviewData(BaseModel):
    company_name: str
    domain: str
    quality_status: str
    issues: list[str]
    blocked_reasons: list[str]
    recommended_edits: list[str]
