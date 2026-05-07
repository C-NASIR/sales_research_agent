from __future__ import annotations

from pathlib import Path

from app.config import settings


def campaign_workspace(campaign_id: str) -> Path:
    return settings.data_dir / "campaigns" / campaign_id


def input_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "input"


def plan_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "plan"


def research_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "research"


def signals_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "signals"


def scores_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "scores"


def outreach_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "outreach"


def review_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "review"


def exports_dir(campaign_id: str) -> Path:
    return campaign_workspace(campaign_id) / "exports"
