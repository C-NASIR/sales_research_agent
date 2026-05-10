from __future__ import annotations

import importlib
import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

TEST_ENV_DEFAULTS = {
    "RESEARCH_MODE": "real",
    "WORKFLOW_PROVIDER_MODE": "stub",
    "STUB_SEARCH_BEHAVIOR": "success",
    "STUB_SCRAPE_BEHAVIOR": "success",
    "STUB_LLM_BEHAVIOR": "success",
    "USE_DEEP_AGENTS": "false",
}


def _clear_app_modules() -> None:
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            sys.modules.pop(name)


@contextmanager
def _client_context(tmp_path: Path, extra_env: dict[str, str] | None = None) -> Iterator[TestClient]:
    tracked_keys = {
        "DATA_DIR",
        "DATABASE_URL",
        *TEST_ENV_DEFAULTS.keys(),
        *(extra_env or {}).keys(),
    }
    original_env = {key: os.environ.get(key) for key in tracked_keys}

    os.environ["DATA_DIR"] = str(tmp_path / "data")
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'prospecting_agent_test.db'}"
    for key, value in TEST_ENV_DEFAULTS.items():
        os.environ[key] = value
    for key, value in (extra_env or {}).items():
        os.environ[key] = value

    _clear_app_modules()
    app_main = importlib.import_module("app.main")

    try:
        with TestClient(app_main.app) as test_client:
            yield test_client
    finally:
        _clear_app_modules()
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    with _client_context(tmp_path) as test_client:
        yield test_client


@pytest.fixture
def client_factory(tmp_path: Path):
    @contextmanager
    def _factory(extra_env: dict[str, str] | None = None) -> Iterator[TestClient]:
        with _client_context(tmp_path, extra_env=extra_env) as test_client:
            yield test_client

    return _factory


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
