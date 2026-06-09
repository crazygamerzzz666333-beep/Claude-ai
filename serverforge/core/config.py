"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the bot and API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    discord_token: str = Field(..., alias="DISCORD_TOKEN")
    database_dsn: str = Field(..., alias="DATABASE_DSN")
    redis_dsn: str = Field(..., alias="REDIS_DSN")
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8080, alias="API_PORT")
    bot_prefix: str = Field("!", alias="BOT_PREFIX")
    public_base_url: str = Field("http://localhost:8080", alias="PUBLIC_BASE_URL")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    owner_ids: tuple[int, ...] = Field(default_factory=tuple, alias="OWNER_IDS")
    command_cooldown_seconds: int = Field(8, alias="COMMAND_COOLDOWN_SECONDS")
    dangerous_action_ttl_seconds: int = Field(600, alias="DANGEROUS_ACTION_TTL_SECONDS")
    scheduled_backup_minutes: int = Field(360, alias="SCHEDULED_BACKUP_MINUTES")

    @field_validator("owner_ids", mode="before")
    @classmethod
    def parse_owner_ids(cls, value: str | list[int] | tuple[int, ...]) -> tuple[int, ...]:
        """Parse comma-separated Discord snowflakes into integers."""
        if isinstance(value, tuple):
            return value
        if isinstance(value, list):
            return tuple(int(item) for item in value)
        if not value:
            return ()
        return tuple(int(item.strip()) for item in value.split(",") if item.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()  # type: ignore[call-arg]
