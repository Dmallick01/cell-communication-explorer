from pathlib import Path

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
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    pipeline_demo_mode: bool = False  # set PIPELINE_DEMO_MODE=true for synthetic data


settings = Settings()
