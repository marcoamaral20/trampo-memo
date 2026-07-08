from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://trampomemo:trampomemo@localhost:5432/trampomemo"
    source_storage_path: Path = Path("storage/sources")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
