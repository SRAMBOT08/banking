from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class OperationType(str, Enum):
    CREATE_INCIDENT = "CREATE_INCIDENT"
    GET_INCIDENT = "GET_INCIDENT"
    UPDATE_INCIDENT = "UPDATE_INCIDENT"
    LOOKUP_USER = "LOOKUP_USER"
    LOOKUP_CMDB_CI = "LOOKUP_CMDB_CI"
    CREATE_CHANGE_REQUEST = "CREATE_CHANGE_REQUEST"


class RetryPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_retries: int = Field(ge=0, le=10, default=3)
    base_delay_ms: int = Field(ge=10, le=10000, default=250)
    max_delay_ms: int = Field(ge=10, le=60000, default=5000)
    retryable_status_codes: List[int] = Field(default_factory=lambda: [408, 409, 425, 429, 500, 502, 503, 504])


class AuthenticationContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = Field(default="basic")
    username: str = Field(min_length=1)
    password_masked: str = Field(default="***")


class AdapterConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_name: str
    servicenow_base_url: HttpUrl
    verify_ssl: bool
    timeout_seconds: float = Field(gt=0.0, le=120.0)
    retry_policy: RetryPolicy


class ExecutionTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_version: str = Field(default="1.0")
    execution_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    investigation_id: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    operation: OperationType
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(ge=0, le=100)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class IncidentPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    short_description: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1)
    priority: str = Field(default="3")
    impact: str = Field(default="3")
    urgency: str = Field(default="3")
    category: str = Field(default="security")
    work_notes: str = Field(min_length=1)
    correlation_id: str
    investigation_id: str
    execution_id: str
    snapshot_version: str


class IncidentResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    sys_id: str = Field(min_length=1)
    number: Optional[str] = None
    state: Optional[str] = None
    short_description: Optional[str] = None


class ServiceNowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    endpoint: str
    query: Dict[str, Any] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str

    @field_validator("method")
    @classmethod
    def method_must_be_http(cls, value: str) -> str:
        allowed = {"GET", "POST", "PATCH", "PUT"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError("unsupported HTTP method")
        return upper


class ServiceNowResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status_code: int
    latency_ms: float
    body: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verified: bool
    reason: str
    sys_id: Optional[str] = None
    correlation_id_match: bool = False
    investigation_id_match: bool = False
    execution_status_valid: bool = False


class ExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    execution_id: str
    task_id: str
    operation: OperationType
    success: bool
    sys_id: Optional[str] = None
    result: Dict[str, Any] = Field(default_factory=dict)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    verification: Optional[VerificationResult] = None
    processed_at: str = Field(default_factory=utc_now)


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_id: str
    task_id: str
    investigation_id: str
    correlation_id: str
    servicenow_sys_id: Optional[str] = None
    http_method: str
    endpoint: str
    latency_ms: float
    retry_count: int
    verification_result: Optional[bool] = None
    timestamp: str = Field(default_factory=utc_now)
    success: bool
    failure_reason: Optional[str] = None


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    auth_ok: bool
    servicenow_reachable: bool
    configuration_valid: bool
    timestamp: str = Field(default_factory=utc_now)
