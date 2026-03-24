from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    secret_key: str = "changeme-super-secret-key-please-replace-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./ticketmaster.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
