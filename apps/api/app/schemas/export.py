from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.review import REVIEW_STATUSES


class ExportCreateRequest(BaseModel):
    include_review_statuses: list[str] = Field(default_factory=lambda: ["approved"])

    @field_validator("include_review_statuses")
    @classmethod
    def validate_review_statuses(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for item in value:
            status = item.strip()
            if status not in REVIEW_STATUSES:
                raise ValueError("Invalid review status in export request.")
            if status not in normalized:
                normalized.append(status)
        if not normalized:
            raise ValueError("At least one review status is required for export.")
        return normalized


class ExportFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    export_type: str
    file_path: str
    download_url: str
    created_at: datetime


class ExportCreateResponse(BaseModel):
    campaign_id: str
    exports: list[ExportFileResponse]


class ExportListResponse(BaseModel):
    campaign_id: str
    exports: list[ExportFileResponse]
