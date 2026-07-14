from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdapterSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = Field("servicenow-execution-adapter", alias="SERVICENOW_ADAPTER_SERVICE_NAME")
    api_port: int = Field(8800, alias="SERVICENOW_ADAPTER_API_PORT")
    log_level: str = Field("INFO", alias="SERVICENOW_ADAPTER_LOG_LEVEL")

    servicenow_base_url: str = Field("https://instance.service-now.com", alias="SERVICENOW_BASE_URL")
    servicenow_username: str = Field("", alias="SERVICENOW_USERNAME")
    servicenow_password: str = Field("", alias="SERVICENOW_PASSWORD")
    servicenow_auth_mode: str = Field("basic", alias="SERVICENOW_AUTH_MODE")
    servicenow_verify_ssl: bool = Field(True, alias="SERVICENOW_VERIFY_SSL")

    request_timeout_seconds: float = Field(20.0, alias="SERVICENOW_TIMEOUT_SECONDS")
    max_retry_count: int = Field(3, alias="SERVICENOW_RETRY_COUNT")
    retry_base_delay_ms: int = Field(250, alias="SERVICENOW_RETRY_BASE_DELAY_MS")
    retry_max_delay_ms: int = Field(5000, alias="SERVICENOW_RETRY_MAX_DELAY_MS")

    kafka_bootstrap_servers: str = Field("localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_consumer_group: str = Field("servicenow-adapter-group", alias="SERVICENOW_ADAPTER_CONSUMER_GROUP")
    execution_ready_topic: str = Field("execution.ready.v1", alias="EXECUTION_READY_TOPIC")
    execution_started_topic: str = Field("execution.started.v1", alias="EXECUTION_STARTED_TOPIC")
    execution_completed_topic: str = Field("execution.completed.v1", alias="EXECUTION_COMPLETED_TOPIC")
    execution_failed_topic: str = Field("execution.failed.v1", alias="EXECUTION_FAILED_TOPIC")
    execution_verified_topic: str = Field("execution.verified.v1", alias="EXECUTION_VERIFIED_TOPIC")

    audit_log_path: str = Field("servicenow-adapter/audit/execution_audit.jsonl", alias="SERVICENOW_ADAPTER_AUDIT_LOG_PATH")


settings = AdapterSettings()
