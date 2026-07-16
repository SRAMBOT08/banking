from __future__ import annotations

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field
except Exception:
    from pydantic import BaseSettings, Field

from typing import Dict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = Field("gateway", validation_alias="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", validation_alias="KAFKA_BOOTSTRAP_SERVERS")
    simulator_service_url: str = Field("http://event-simulator:8900", validation_alias="SIMULATOR_SERVICE_URL")
    investigation_service_url: str = Field("http://investigation-service:8500", validation_alias="INVESTIGATION_SERVICE_URL")
    case_service_url: str = Field("http://case-service:8950", validation_alias="CASE_SERVICE_URL")
    report_service_url: str = Field("http://ai-report-service:8960", validation_alias="REPORT_SERVICE_URL")
    execution_service_url: str = Field("http://execution-service:8700", validation_alias="EXECUTION_SERVICE_URL")
    graph_service_url: str = Field("http://graph-service:8010", validation_alias="GRAPH_SERVICE_URL")
    servicenow_service_url: str = Field("http://servicenow-adapter:8800", validation_alias="SERVICENOW_SERVICE_URL")
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
        validation_alias="TOPIC_MAP",
    )


settings = Settings()
