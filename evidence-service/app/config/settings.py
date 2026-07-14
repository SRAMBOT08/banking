from __future__ import annotations

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except Exception:
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    service_name: str = Field("evidence-service", env="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    normalized_topic: str = Field("normalized-events.v1", env="NORMALIZED_TOPIC")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
