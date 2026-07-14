from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = Field("execution-decision-service", alias="EXECUTION_SERVICE_NAME")
    api_port: int = Field(8700, alias="EXECUTION_API_PORT")
    kafka_bootstrap: str = Field("localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    consumer_group: str = Field("execution-decision-service-group", alias="EXECUTION_CONSUMER_GROUP")

    investigation_completed_topic: str = Field("investigation.completed.v1", alias="INVESTIGATION_COMPLETED_TOPIC")
    plan_created_topic: str = Field("execution.plan.created.v1", alias="EXECUTION_PLAN_CREATED_TOPIC")
    policy_checked_topic: str = Field("execution.policy.checked.v1", alias="EXECUTION_POLICY_CHECKED_TOPIC")
    awaiting_approval_topic: str = Field("execution.awaiting.approval.v1", alias="EXECUTION_AWAITING_APPROVAL_TOPIC")
    approved_topic: str = Field("execution.approved.v1", alias="EXECUTION_APPROVED_TOPIC")
    ready_topic: str = Field("execution.ready.v1", alias="EXECUTION_READY_TOPIC")
    started_topic: str = Field("execution.started.v1", alias="EXECUTION_STARTED_TOPIC")
    completed_topic: str = Field("execution.completed.v1", alias="EXECUTION_COMPLETED_TOPIC")
    failed_topic: str = Field("execution.failed.v1", alias="EXECUTION_FAILED_TOPIC")
    cancelled_topic: str = Field("execution.cancelled.v1", alias="EXECUTION_CANCELLED_TOPIC")
    verified_topic: str = Field("execution.verified.v1", alias="EXECUTION_VERIFIED_TOPIC")
    audit_topic: str = Field("execution.audit.v1", alias="EXECUTION_AUDIT_TOPIC")

    risk_auto_approve_threshold: int = Field(40, alias="EXECUTION_RISK_AUTO_APPROVE_THRESHOLD")
    risk_hard_block_threshold: int = Field(95, alias="EXECUTION_RISK_HARD_BLOCK_THRESHOLD")
    approval_expiry_minutes: int = Field(120, alias="EXECUTION_APPROVAL_EXPIRY_MINUTES")

    execution_window_start_hour_utc: int = Field(0, alias="EXECUTION_WINDOW_START_HOUR_UTC")
    execution_window_end_hour_utc: int = Field(23, alias="EXECUTION_WINDOW_END_HOUR_UTC")


settings = Settings()
