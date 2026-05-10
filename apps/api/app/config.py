from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def _resolve_data_dir(raw_value: str) -> Path:
    data_dir = Path(raw_value)
    if not data_dir.is_absolute():
        data_dir = (PROJECT_ROOT / data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _resolve_database_url(raw_value: str, data_dir: Path) -> str:
    sqlite_relative_prefix = "sqlite:///./"
    if raw_value.startswith(sqlite_relative_prefix):
        relative_path = raw_value.removeprefix(sqlite_relative_prefix)
        return f"sqlite:///{(PROJECT_ROOT / relative_path).resolve()}"
    if raw_value == "sqlite:///":
        return f"sqlite:///{data_dir / 'prospecting_agent.db'}"
    return raw_value


def _parse_bool(raw_value: str | None) -> bool:
    if raw_value is None:
        return False
    return raw_value.strip().lower() in {"true", "1", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    data_dir: Path
    database_url: str
    model_name: str
    workflow_provider_mode: str
    use_deep_agents: bool
    research_mode: str
    tavily_api_key: str
    firecrawl_api_key: str
    max_search_results: int
    max_scraped_pages_per_account: int
    max_source_chars: int


data_dir = _resolve_data_dir(os.getenv("DATA_DIR", "./data"))

settings = Settings(
    app_name="prospecting-agent-api",
    environment=os.getenv("APP_ENV", "local"),
    data_dir=data_dir,
    database_url=_resolve_database_url(
        os.getenv("DATABASE_URL", "sqlite:///./data/prospecting_agent.db"),
        data_dir,
    ),
    model_name=os.getenv("MODEL_NAME", "openai:gpt-4.1-mini"),
    workflow_provider_mode=os.getenv("WORKFLOW_PROVIDER_MODE", "live").strip().lower(),
    use_deep_agents=_parse_bool(os.getenv("USE_DEEP_AGENTS", "false")),
    research_mode=os.getenv("RESEARCH_MODE", "real").strip().lower(),
    tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
    firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY", ""),
    max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "5")),
    max_scraped_pages_per_account=int(os.getenv("MAX_SCRAPED_PAGES_PER_ACCOUNT", "4")),
    max_source_chars=int(os.getenv("MAX_SOURCE_CHARS", "12000")),
)
