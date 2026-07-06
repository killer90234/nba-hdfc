from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/hdfc_nba"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "hdfc-nba-2-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    GEMINI_API_KEY: str = ""
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
