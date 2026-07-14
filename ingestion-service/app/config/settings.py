from __future__ import annotations

try:
    # pydantic v2 split BaseSettings into pydantic-settings
    from pydantic_settings import BaseSettings
    from pydantic import Field, AnyUrl
except Exception:  # pragma: no cover - fallback for older installs
    from pydantic import BaseSettings, Field, AnyUrl


class Settings(BaseSettings):
    service_name: str = Field("ingestion-service", env="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_group_id: str = Field("ingestion-service-group", env="KAFKA_GROUP_ID")
    redis_url: AnyUrl = Field("redis://localhost:6379/0", env="REDIS_URL")
    normalized_topic: str = Field("normalized-events.v1", env="NORMALIZED_TOPIC")
    dlq_suffix: str = Field(".dlq.v1", env="DLQ_SUFFIX")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
