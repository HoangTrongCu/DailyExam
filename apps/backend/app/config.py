"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from env vars."""

    model_config = SettingsConfigDict(env_prefix="DAILYEXAM_", env_file=".env", extra="ignore")

    app_name: str = "DailyExam API"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]
    gate_open_hour: int = 8
    gate_close_hour: int = 9
    result_release_hour: int = 9
    result_release_minute: int = 30


def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
