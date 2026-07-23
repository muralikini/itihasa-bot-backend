from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_env: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000"

    # LLM
    xai_api_key: str = ""
    google_api_key: str = ""
    primary_llm: str = "ollama"          # "ollama" | "grok" | "gemini"
    ollama_model: str = "llama3.2"

    # Database (not used while on Chroma)
    database_url: str = "postgresql://postgres:postgres@localhost:5432/itihasa"

    # RAG
    embedding_model: str = "models/embedding-001"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 6

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
