from __future__ import annotations

import importlib
import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


def _clear_app_modules() -> None:
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            sys.modules.pop(name)


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    original_env = {
        "DATA_DIR": os.environ.get("DATA_DIR"),
        "DATABASE_URL": os.environ.get("DATABASE_URL"),
        "RESEARCH_MODE": os.environ.get("RESEARCH_MODE"),
        "USE_DEEP_AGENTS": os.environ.get("USE_DEEP_AGENTS"),
    }

    os.environ["DATA_DIR"] = str(tmp_path / "data")
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'prospecting_agent_test.db'}"
    os.environ["RESEARCH_MODE"] = "fake"
    os.environ["USE_DEEP_AGENTS"] = "false"

    _clear_app_modules()
    app_main = importlib.import_module("app.main")

    with TestClient(app_main.app) as test_client:
        yield test_client

    _clear_app_modules()
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def campaign_payload() -> dict[str, object]:
    return {
        "name": "AI code review outbound",
        "product_description": "AI code review tool for engineering teams",
        "ideal_customer_profile": "B2B SaaS companies with active engineering teams",
        "pain_statement": "Slow pull request review and inconsistent code quality",
        "target_persona": "VP Engineering, CTO, Head of Platform",
        "tone": "Direct, specific, no hype",
        "max_accounts": 10,
    }
