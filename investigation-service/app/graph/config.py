"""Neo4j configuration."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class GraphSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    neo4j_uri: str = Field("bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field("neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field("testpassword", alias="NEO4J_PASSWORD")
    neo4j_database: str = Field("neo4j", alias="NEO4J_DATABASE")
    neo4j_max_connection_pool_size: int = Field(50, alias="NEO4J_MAX_CONNECTION_POOL_SIZE")
    neo4j_connection_timeout: int = Field(30, alias="NEO4J_CONNECTION_TIMEOUT")
    neo4j_max_transaction_retry_time: int = Field(30, alias="NEO4J_MAX_TRANSACTION_RETRY_TIME")


settings = GraphSettings()