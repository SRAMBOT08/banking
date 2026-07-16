from __future__ import annotations
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import ConfigDict, Field
except Exception:
    from pydantic import BaseSettings, Field

from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

    service_name: str = Field("threat-intelligence-service", validation_alias="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", validation_alias="KAFKA_BOOTSTRAP_SERVERS")
    consumer_topic: str = Field("evidence.graph.events.v1", validation_alias="CONSUMER_TOPIC")
    producer_topic: str = Field("investigation.candidates.v1", validation_alias="PRODUCER_TOPIC")
    patterns_dir: str = Field("patterns", validation_alias="PATTERNS_DIR")
    score_threshold: int = Field(30, validation_alias="SCORE_THRESHOLD")
    validate_on_start: bool = Field(True, validation_alias="VALIDATE_PATTERNS")
    required_pattern_fields: List[str] = Field(["name", "version", "nodes", "edges"], validation_alias="REQUIRED_PATTERN_FIELDS")

settings = Settings()
