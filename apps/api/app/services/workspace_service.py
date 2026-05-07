from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.db.models import Campaign


WORKSPACE_DIRS = [
    "input",
    "plan",
    "research",
    "signals",
    "scores",
    "outreach",
    "review",
    "exports",
]


def ensure_campaign_workspace(campaign: Campaign) -> Path:
    workspace_path = Path(campaign.workspace_path)
    workspace_path.mkdir(parents=True, exist_ok=True)
    for name in WORKSPACE_DIRS:
        (workspace_path / name).mkdir(parents=True, exist_ok=True)
    return workspace_path


def write_campaign_brief(campaign: Campaign) -> Path:
    input_dir = ensure_campaign_workspace(campaign) / "input"
    brief_path = input_dir / "brief.json"
    brief = {
        "id": campaign.id,
        "name": campaign.name,
        "product_description": campaign.product_description,
        "ideal_customer_profile": campaign.ideal_customer_profile,
        "pain_statement": campaign.pain_statement,
        "target_persona": campaign.target_persona,
        "tone": campaign.tone,
        "max_accounts": campaign.max_accounts,
        "status": campaign.status,
    }
    _write_json(brief_path, brief)
    return brief_path


def write_uploaded_csv(campaign: Campaign, file_bytes: bytes) -> Path:
    input_dir = ensure_campaign_workspace(campaign) / "input"
    csv_path = input_dir / "uploaded_companies.csv"
    csv_path.write_bytes(file_bytes)
    return csv_path


def write_normalized_accounts(campaign: Campaign, accounts: list[dict[str, Any]]) -> Path:
    input_dir = ensure_campaign_workspace(campaign) / "input"
    accounts_path = input_dir / "normalized_accounts.json"
    _write_json(accounts_path, accounts)
    return accounts_path


def write_upload_report(campaign: Campaign, report: dict[str, Any]) -> Path:
    input_dir = ensure_campaign_workspace(campaign) / "input"
    report_path = input_dir / "upload_report.json"
    _write_json(report_path, report)
    return report_path


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
