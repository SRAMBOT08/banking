from __future__ import annotations

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field
except Exception:
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = Field("evidence-service", validation_alias="SERVICE_NAME")
    kafka_bootstrap: str = Field("localhost:9092", validation_alias="KAFKA_BOOTSTRAP_SERVERS")
    normalized_topic: str = Field("normalized-events.v1", validation_alias="NORMALIZED_TOPIC")
    evidence_graph_topic: str = Field("evidence.graph.events.v1", validation_alias="EVIDENCE_GRAPH_TOPIC")
    consumer_group: str = Field("evidence-service-group", validation_alias="CONSUMER_GROUP")
    dlq_topic: str = Field("normalized-events.dlq.v1", validation_alias="DLQ_TOPIC")

    # Neo4j settings
    neo4j_uri: str = Field("bolt://localhost:7687", validation_alias="NEO4J_URI")
    neo4j_user: str = Field("neo4j", validation_alias="NEO4J_USER")
    neo4j_password: str = Field("testpassword", validation_alias="NEO4J_PASSWORD")
    neo4j_database: str = Field("neo4j", validation_alias="NEO4J_DATABASE")
    neo4j_max_connection_pool_size: int = Field(50, validation_alias="NEO4J_MAX_CONNECTION_POOL_SIZE")
    neo4j_connection_timeout: int = Field(30, validation_alias="NEO4J_CONNECTION_TIMEOUT")
    neo4j_max_transaction_retry_time: int = Field(30, validation_alias="NEO4J_MAX_TRANSACTION_RETRY_TIME")


settings = Settings()
