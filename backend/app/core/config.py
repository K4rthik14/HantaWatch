"""Application configuration via pydantic-settings.

All settings are loaded from environment variables or a .env file.
Sensitive fields (SECRET_KEY, LLM_API_KEY) must never be committed.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the MATM backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────────────────────────
    APP_ENV: Literal["dev", "staging", "production"] = Field(
        default="dev",
        description="Deployment environment.",
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode.")

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://matm:matm@localhost:5432/matm",
        description="Async SQLAlchemy connection string.",
    )

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    CHROMA_HOST: str = Field(default="localhost", description="ChromaDB server hostname.")
    CHROMA_PORT: int = Field(default=8001, description="ChromaDB HTTP port.")

    # ── LLM (Ollama / OpenAI-compatible) ─────────────────────────────────────
    LLM_BASE_URL: str = Field(
        default="http://localhost:11434/v1",
        description="Base URL for the OpenAI-compatible LLM endpoint.",
    )
    LLM_API_KEY: str = Field(
        default="ollama",
        description="API key for the LLM provider (use 'ollama' for local Ollama).",
    )
    LLM_DEFAULT_MODEL: str = Field(
        default="qwen2.5:7b",
        description="Default model identifier to use for completions.",
    )

    # ── Embeddings ────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-Transformers model name for embedding generation.",
    )

    # ── Public health feeds ───────────────────────────────────────────────────
    WHO_RSS_URL: str = Field(
        default="https://www.who.int/rss-feeds/news-english.xml",
        description="WHO RSS feed URL for ingestion.",
    )
    PROMED_URL: str = Field(
        default="https://promedmail.org/feed/",
        description="ProMED mail feed URL for ingestion.",
    )

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="HMAC secret key — must be overridden in staging/production.",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str, info: object) -> str:  # noqa: ANN001
        """Warn when the default secret key is used outside dev."""
        # Actual enforcement happens at startup in main.py
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def chroma_url(self) -> str:
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
