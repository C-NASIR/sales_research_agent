from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "prospecting-agent-api"
    environment: str = os.getenv("APP_ENV", "local")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))


settings = Settings()
