"""
Configuration - Environment variables and settings
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/ai_agent_cs"

    # LLM
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # App
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # API
    API_V1_PREFIX: str = "/api"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
