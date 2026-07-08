from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://trampomemo:trampomemo@localhost:5432/trampomemo"
    source_storage_path: Path = Path("storage/sources")
    embedding_provider: str = "local"
    llm_provider: str = "local"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    openai_llm_model: str = "gpt-5.4-mini"
    openai_llm_max_output_tokens: int = 800

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
