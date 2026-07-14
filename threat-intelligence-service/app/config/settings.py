from __future__ import annotations
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except Exception:
    from pydantic import BaseSettings, Field

from typing import List


class Settings(BaseSettings):
    service_name: str = Field("threat-intelligence-service", env="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    consumer_topic: str = Field("evidence.graph.events.v1", env="CONSUMER_TOPIC")
    producer_topic: str = Field("investigation.candidates.v1", env="PRODUCER_TOPIC")
    patterns_dir: str = Field("patterns", env="PATTERNS_DIR")
    score_threshold: int = Field(30, env="SCORE_THRESHOLD")
    validate_on_start: bool = Field(True, env="VALIDATE_PATTERNS")
    required_pattern_fields: List[str] = Field(["name", "version", "nodes", "edges"], env="REQUIRED_PATTERN_FIELDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
