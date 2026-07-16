from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    service_name: str = Field("investigation-service", alias="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    consumer_topic: str = Field("investigation.candidates.v1", alias="CONSUMER_TOPIC")
    producer_topic: str = Field("investigation.active.v1", alias="PRODUCER_TOPIC")
    updated_topic: str = Field("investigation.updated.v1", alias="UPDATED_TOPIC")
    closed_topic: str = Field("investigation.closed.v1", alias="CLOSED_TOPIC")
    escalated_topic: str = Field("investigation.escalated.v1", alias="ESCALATED_TOPIC")
    snapshot_topic: str = Field("investigation.snapshot.created.v1", alias="SNAPSHOT_TOPIC")
    completed_topic: str = Field("investigation.completed.v1", alias="COMPLETED_TOPIC")
    consumer_group: str = Field("investigation-service-group", alias="CONSUMER_GROUP")
    api_port: int = Field(8500, alias="API_PORT")
    score_evidence_weight: int = Field(30, alias="SCORE_EVIDENCE_WEIGHT")
    score_correlation_weight: int = Field(20, alias="SCORE_CORRELATION_WEIGHT")
    score_completeness_weight: int = Field(20, alias="SCORE_COMPLETENESS_WEIGHT")
    score_history_weight: int = Field(10, alias="SCORE_HISTORY_WEIGHT")


settings = Settings()
