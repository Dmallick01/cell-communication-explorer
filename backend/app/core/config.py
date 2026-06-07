import json
from pathlib import Path
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Cell Communication Explorer"
    api_prefix: str = "/api/v1"
    data_dir: Path = Path("data")
    uploads_dir: Path = Path("data/uploads")
    results_dir: Path = Path("data/results")
    database_url: str = "sqlite+aiosqlite:///./data/jobs.db"
    max_upload_bytes: int = 2 * 1024 * 1024 * 1024  # 2 GB
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://frontend-sigma-nine-39.vercel.app",
        "https://frontend-dmallick01s-projects.vercel.app",
        "https://frontend-git-main-dmallick01s-projects.vercel.app",
    ]
    pipeline_demo_mode: bool = False
    development_only: bool = False
    reference_dir: Path = Path("reference")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [part.strip() for part in stripped.split(",") if part.strip()]
        return value

    @model_validator(mode="after")
    def apply_data_dir(self) -> "Settings":
        base = Path(self.data_dir)
        self.uploads_dir = base / "uploads"
        self.results_dir = base / "results"
        db_path = (base / "jobs.db").resolve()
        self.database_url = f"sqlite+aiosqlite:///{db_path}"
        return self


settings = Settings()
