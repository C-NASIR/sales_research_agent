from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class OutreachDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    subject: str | None
    body: str | None
    personalization_source: str | None
    sales_angle: str | None
    risk_notes: list[Any] | None
    quality_status: str | None
    workspace_file: str | None
    created_at: datetime
    updated_at: datetime
