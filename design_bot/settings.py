from typing import Any

from pydantic import BaseSettings, PostgresDsn, DirectoryPath, FilePath, Json
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    DB_DSN: PostgresDsn
    PARENT_FOLDER_ID: str
    FILE_PATH: DirectoryPath = "static"
    ADMIN_SECRET: dict[str, str] = {"admin": "42"}
    CREDS: str

    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
