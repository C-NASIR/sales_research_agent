from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ActivityEventCreate(BaseModel):
    type: str
    message: str
    payload: dict[str, Any] | None = None
    run_id: str | None = None

    @field_validator("type", "message")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")
        return cleaned


class ActivityEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    run_id: str | None
    type: str
    message: str
    payload: dict[str, Any] | None
    created_at: datetime


class ActivityEventListResponse(BaseModel):
    events: list[ActivityEventResponse]
