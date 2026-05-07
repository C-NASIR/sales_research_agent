from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.workspace import paths


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def write_markdown(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_todos(campaign_id: str, todos: list[dict[str, Any]]) -> Path:
    return write_json(paths.plan_dir(campaign_id) / "todos.json", todos)


def write_icp(campaign_id: str, icp: dict[str, Any]) -> Path:
    return write_json(paths.plan_dir(campaign_id) / "icp.json", icp)


def write_research_report(campaign_id: str, account_id: str, data: dict[str, Any]) -> Path:
    return write_json(paths.research_dir(campaign_id) / f"{account_id}.json", data)


def write_signal_report(campaign_id: str, account_id: str, data: dict[str, Any]) -> Path:
    return write_json(paths.signals_dir(campaign_id) / f"{account_id}.json", data)


def write_score_report(campaign_id: str, account_id: str, data: dict[str, Any]) -> Path:
    return write_json(paths.scores_dir(campaign_id) / f"{account_id}.json", data)


def write_outreach_draft(campaign_id: str, account_id: str, data: dict[str, Any]) -> Path:
    return write_json(paths.outreach_dir(campaign_id) / f"{account_id}.json", data)


def write_quality_review(campaign_id: str, account_id: str, data: dict[str, Any]) -> Path:
    return write_json(paths.review_dir(campaign_id) / f"{account_id}.json", data)
