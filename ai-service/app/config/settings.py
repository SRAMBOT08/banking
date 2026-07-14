from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = Field("ai-investigation-service", alias="AI_SERVICE_NAME")
    api_port: int = Field(8600, alias="AI_API_PORT")
    investigation_service_url: str = Field("http://investigation-service:8500", alias="INVESTIGATION_SERVICE_URL")
    kafka_bootstrap: str = Field("localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    snapshot_topic: str = Field("investigation.snapshot.created.v1", alias="SNAPSHOT_TOPIC")
    reasoned_topic: str = Field("investigation.reasoned.v1", alias="REASONED_TOPIC")
    report_topic: str = Field("investigation.report.generated.v1", alias="REPORT_TOPIC")
    metrics_topic: str = Field("investigation.ai.metrics.v1", alias="AI_METRICS_TOPIC")
    consumer_group: str = Field("ai-investigation-service-group", alias="AI_CONSUMER_GROUP")
    llm_provider: str = Field("mock", alias="LLM_PROVIDER")
    gemini_api_key: str = Field("", alias="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-2.5-flash", alias="GEMINI_MODEL")
    temperature: float = Field(0.0, alias="LLM_TEMPERATURE")
    top_p: float = Field(1.0, alias="LLM_TOP_P")
    top_k: int = Field(1, alias="LLM_TOP_K")
    max_tokens: int = Field(2048, alias="LLM_MAX_TOKENS")
    timeout_seconds: float = Field(30.0, alias="LLM_TIMEOUT_SECONDS")
    retry_count: int = Field(2, alias="LLM_RETRY_COUNT")
    retry_backoff_seconds: float = Field(0.25, alias="LLM_RETRY_BACKOFF_SECONDS")
    streaming: bool = Field(False, alias="LLM_STREAMING")


settings = Settings()
