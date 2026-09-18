"""
Cấu hình ứng dụng - đọc từ .env
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Settings cho ứng dụng"""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://hienhuu:hienhuu123@localhost:5432/hienhuu_db"
    DATABASE_URL_SYNC: str = "postgresql://hienhuu:hienhuu123@localhost:5432/hienhuu_db"

    # JWT
    SECRET_KEY: str = "hienhuu-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
