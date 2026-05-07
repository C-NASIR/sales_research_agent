from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.workspace import paths


def read_campaign_brief(campaign_id: str) -> dict[str, Any]:
    return _read_json(paths.input_dir(campaign_id) / "brief.json")


def read_normalized_accounts(campaign_id: str) -> list[dict[str, Any]]:
    path = paths.input_dir(campaign_id) / "normalized_accounts.json"
    if not path.exists():
        raise FileNotFoundError(f"Required workspace file is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("normalized_accounts.json must contain a list")
    return data


def read_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required workspace file is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data
