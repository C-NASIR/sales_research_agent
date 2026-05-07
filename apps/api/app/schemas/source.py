from __future__ import annotations

from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str | None = None
    source: str = "tavily"


class ScrapedSource(BaseModel):
    url: str
    title: str | None = None
    markdown: str | None = None
    text: str | None = None
    source: str
    success: bool
    error: str | None = None


class SourceEvidence(BaseModel):
    claim: str
    evidence: str
    source_url: str
    source_title: str | None = None
    confidence: str
    evidence_type: str
