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
    use_deep_agents: bool


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
    use_deep_agents=_parse_bool(os.getenv("USE_DEEP_AGENTS", "false")),
)
