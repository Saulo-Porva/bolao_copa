"""Centralized configuration via Pydantic BaseSettings."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # GCP
    gcs_bucket: str = "bolao-copa-2026"
    gcs_project: str = "hub-whatsapp-dev"

    # API keys
    football_data_api_key: str = ""
    api_football_key: str = ""
    odds_api_key: str = ""
    anthropic_api_key: str = ""

    # LLM models
    haiku_model: str = "claude-haiku-4-5-20251001"
    sonnet_model: str = "claude-sonnet-4-6"

    # Sentiment thresholds
    sentiment_low_threshold: float = 3.0
    sentiment_high_threshold: float = 8.0

    # Rate limits
    football_data_sleep_seconds: float = 6.1
    api_football_daily_limit: int = 100
    odds_api_monthly_limit: int = 500
    odds_cache_hours: int = 12

    # Cache TTL (hours, unless noted)
    form_cache_hours: int = 20
    squad_cache_hours: int = 20
    h2h_cache_days: int = 7
    analysis_cache_hours: int = 24
    news_cache_hours: int = 6

    # Pipeline
    pipeline_run_hour: int = 6
    progress_file: str = "data/.upload_progress.json"
    teams_file: str = "data/teams_48.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
