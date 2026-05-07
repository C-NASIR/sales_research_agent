from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class UploadInvalidRow(BaseModel):
    row_number: int
    reason: str
    raw: dict[str, Any]


class UploadDuplicateRow(BaseModel):
    row_number: int
    company_name: str
    domain: str
    duplicate_of_domain: str


class UploadAccountPreview(BaseModel):
    id: str | None = None
    company_name: str
    domain: str


class UploadReportResponse(BaseModel):
    campaign_id: str
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    created_accounts: int
    accounts: list[UploadAccountPreview]
    invalid: list[UploadInvalidRow]
    duplicates: list[UploadDuplicateRow]
