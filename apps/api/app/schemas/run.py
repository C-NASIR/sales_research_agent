from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CampaignRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    agent_thread_id: str | None
    created_at: datetime
    updated_at: datetime
