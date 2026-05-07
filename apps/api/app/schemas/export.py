from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExportFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    export_type: str
    file_path: str
    created_at: datetime
