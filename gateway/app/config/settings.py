from __future__ import annotations

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except Exception:
    from pydantic import BaseSettings, Field

from typing import Dict


class Settings(BaseSettings):
    service_name: str = Field("gateway", env="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    # mapping from event_type -> kafka topic
    topic_map: Dict[str, str] = Field(
        {
            "authentication": "security-events.v1",
            "transaction": "transaction-events.v1",
            "threat": "threat-events.v1",
            "fraud": "fraud-events.v1",
            "identity": "identity-events.v1",
            "asset": "asset-events.v1",
            # fallback
            "default": "events.unified.v1",
        },
        env="TOPIC_MAP",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
