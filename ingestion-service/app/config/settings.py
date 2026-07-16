from __future__ import annotations

try:
    # pydantic v2 split BaseSettings into pydantic-settings
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field, AnyUrl
except Exception:  # pragma: no cover - fallback for older installs
    from pydantic import BaseSettings, Field, AnyUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = Field("ingestion-service", validation_alias="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", validation_alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_group_id: str = Field("ingestion-service-group", validation_alias="KAFKA_GROUP_ID")
    redis_url: AnyUrl = Field("redis://localhost:6379/0", validation_alias="REDIS_URL")
    normalized_topic: str = Field("normalized-events.v1", validation_alias="NORMALIZED_TOPIC")
    # Demo-safe default: subscribe only to the unified ingress topic unless explicitly overridden.
    ingress_topics: list[str] = Field(["events.unified.v1"], validation_alias="INGRESS_TOPICS")
    dlq_suffix: str = Field(".dlq.v1", validation_alias="DLQ_SUFFIX")


settings = Settings()
