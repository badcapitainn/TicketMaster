from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    secret_key: str = "changeme-super-secret-key-please-replace-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./ticketmaster.db"

    class Config:
        env_file = ".env"

    @property
    def get_valid_database_url(self) -> str:
        # SQLAlchemy 1.4+ removed support for the 'postgres://' scheme
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql://", 1)
        return self.database_url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
