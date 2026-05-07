from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class OutreachDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    account_id: str | None = None
    company_name: str | None = None
    domain: str | None = None
    subject: str | None
    body: str | None
    personalization_source: str | None
    personalization_source_url: str | None = None
    sales_angle: str | None
    risk_notes: list[Any] | None
    quality_status: str | None = None
    workspace_file: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OutreachDraftUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None
    personalization_source: str | None = None
    personalization_source_url: str | None = None
    sales_angle: str | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "OutreachDraftUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one draft field must be provided.")

        if "subject" in self.model_fields_set:
            subject = (self.subject or "").strip()
            if not subject:
                raise ValueError("Subject cannot be empty.")
            self.subject = subject

        if "body" in self.model_fields_set:
            body = (self.body or "").strip()
            if not body:
                raise ValueError("Body cannot be empty.")
            self.body = body

        if "personalization_source" in self.model_fields_set and self.personalization_source is not None:
            self.personalization_source = self.personalization_source.strip()

        if "personalization_source_url" in self.model_fields_set and self.personalization_source_url is not None:
            self.personalization_source_url = self.personalization_source_url.strip()

        if "sales_angle" in self.model_fields_set and self.sales_angle is not None:
            self.sales_angle = self.sales_angle.strip()

        return self


class QualityReviewResponse(BaseModel):
    company_name: str
    domain: str
    quality_status: str
    issues: list[str]
    blocked_reasons: list[str]
    recommended_edits: list[str]
