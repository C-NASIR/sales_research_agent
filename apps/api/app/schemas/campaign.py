from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CampaignCreate(BaseModel):
    name: str
    product_description: str
    ideal_customer_profile: str
    pain_statement: str
    target_persona: str
    tone: str
    max_accounts: int = Field(default=10, ge=1, le=100)

    @field_validator(
        "name",
        "product_description",
        "ideal_customer_profile",
        "pain_statement",
        "target_persona",
        "tone",
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")
        return cleaned


class CampaignUpdate(BaseModel):
    name: str | None = None
    product_description: str | None = None
    ideal_customer_profile: str | None = None
    pain_statement: str | None = None
    target_persona: str | None = None
    tone: str | None = None
    max_accounts: int | None = Field(default=None, ge=1, le=100)
    status: str | None = None


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    product_description: str
    ideal_customer_profile: str
    pain_statement: str
    target_persona: str
    tone: str
    max_accounts: int
    status: str
    workspace_path: str
    created_at: datetime
    updated_at: datetime


class CampaignListResponse(BaseModel):
    campaigns: list[CampaignResponse]
