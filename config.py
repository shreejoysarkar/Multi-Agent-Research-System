"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Tavily Configuration
    TAVILY_API_KEY: str

    # Mistral Configuration
   GROQ_API_KEY: str

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Application Info
    app_name: str = "RAG Q&A System"
    app_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    settings = Settings()

    return settings