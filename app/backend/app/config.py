from __future__ import annotations

from pathlib import Path
import os


class Settings:
    app_name = "F1 Intelligence Hub API"
    app_env = os.getenv("APP_ENV", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    local_timezone = os.getenv("LOCAL_TIMEZONE", "America/Los_Angeles")
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/f1_intelligence_hub",
    )
    llm_provider = os.getenv("LLM_PROVIDER", "mock")
    openf1_base_url = os.getenv("OPENF1_BASE_URL", "https://api.openf1.org/v1")
    auto_sync_days = tuple(
        int(day.strip())
        for day in os.getenv("AUTO_SYNC_DAYS", "4,5,6").split(",")
        if day.strip()
    )
    auto_sync_start_hour = int(os.getenv("AUTO_SYNC_START_HOUR", "6"))
    auto_sync_end_hour = int(os.getenv("AUTO_SYNC_END_HOUR", "12"))
    prediction_enable_live_training = (
        os.getenv("PREDICTION_ENABLE_LIVE_TRAINING", "false" if app_env == "production" else "true").lower()
        == "true"
    )
    prediction_http_timeout_seconds = float(os.getenv("PREDICTION_HTTP_TIMEOUT_SECONDS", "8"))
    seed_data_path = Path(__file__).resolve().parents[2] / "shared" / "demo-data.json"
    runtime_cache_path = Path(__file__).resolve().parents[1] / "data" / "runtime-cache.json"


settings = Settings()
