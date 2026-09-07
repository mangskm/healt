from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    database_url: str
    cors_origins: str = "http://localhost:5173"
    app_env: str = "development"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    log_level: str = "INFO"
    session_ttl_minutes: int = Field(default=10080, gt=0, le=43200)
    session_cookie_name: str = "health_session"
    cookie_secure: bool | None = None

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        if "*" in origins:
            raise ValueError("CORS_ORIGINS cannot include '*' when credentialed sessions are enabled.")
        return origins

    @property
    def trusted_host_list(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]

    @field_validator("cookie_secure", mode="before")
    @classmethod
    def empty_cookie_secure_means_default(cls, value: object) -> object:
        return None if value == "" else value

    @property
    def session_ttl_seconds(self) -> int:
        return self.session_ttl_minutes * 60

    @property
    def session_cookie_secure(self) -> bool:
        return self.cookie_secure if self.cookie_secure is not None else self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
