from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExportCreateRequest(BaseModel):
    include_review_statuses: list[str] = ["approved"]


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
