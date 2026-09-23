"""
Cấu hình ứng dụng - đọc từ .env
"""
import json
from pydantic_settings import BaseSettings
from typing import List, Union


def parse_list(v: Union[str, List[str]]) -> List[str]:
    """Parse list từ JSON string hoặc list"""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return [item.strip() for item in v.strip("[]").split(",")]
    return []


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.CORS_ORIGINS = parse_list(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
