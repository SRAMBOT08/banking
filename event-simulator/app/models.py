from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class ScenarioName(str, Enum):
    CREDENTIAL_STUFFING = 'credential_stuffing'
    PASSWORD_SPRAY = 'password_spray'
    ACCOUNT_TAKEOVER = 'account_takeover'
    IMPOSSIBLE_TRAVEL = 'impossible_travel'
    NEW_DEVICE_LOGIN = 'new_device_login'
    PRIVILEGE_ESCALATION = 'privilege_escalation'
    PHISHING_CAMPAIGN = 'phishing_campaign'
    BUSINESS_EMAIL_COMPROMISE = 'business_email_compromise'
    SUSPICIOUS_POWERSHELL = 'suspicious_powershell'
    MALWARE_EXECUTION = 'malware_execution'
    SUSPICIOUS_DNS = 'suspicious_dns'
    TOR_LOGIN = 'tor_login'
    VPN_ABUSE = 'vpn_abuse'
    DATA_EXFILTRATION = 'data_exfiltration'
    LARGE_BANKING_TRANSFER = 'large_banking_transfer'
    MONEY_MULE = 'money_mule'
    INSIDER_THREAT = 'insider_threat'
    RANSOMWARE = 'ransomware'
    HARVEST_NOW_DECRYPT_LATER = 'harvest_now_decrypt_later'
    QUANTUM_READINESS_FAILURES = 'quantum_readiness_failures'


class EventType(str, Enum):
    AUTHENTICATION = 'authentication'
    TRANSACTION = 'transaction'
    IDENTITY = 'identity'
    ASSET = 'asset'
    THREAT = 'threat'
    FRAUD = 'fraud'
    EVIDENCE = 'evidence'
    # These telemetry domains are represented by the shared Asset/Identity
    # categories; the precise kind remains in payload.action.
    NETWORK = 'asset'
    ENDPOINT = 'asset'
    EMAIL = 'identity'
    CLOUD = 'asset'


class Severity(str, Enum):
    INFO = 'info'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class SimulationEvent(BaseModel):
    """Telemetry envelope accepted by ingestion and traceable to a simulation."""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    event_version: str = '1.0'
    timestamp: datetime
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: UUID
    investigation_id: UUID | None = None
    tenant_id: str
    source_id: str
    producer_service: str = 'event-simulator'
    schema_version: str = '1.0'
    severity: Severity = Severity.INFO
    classification: str = 'event'
    scenario: ScenarioName | None = None
    sequence: int = 0
    entity: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulationRequest(BaseModel):
    scenarios: list[ScenarioName] = Field(min_length=1)
    seed: int = 1
    tenant_id: str = 'demo-bank'
    start_time: datetime | None = None
    event_rate_per_second: float = Field(0, ge=0, le=1000, description='0 generates once; positive value schedules continuously')
    noise_ratio: float = Field(0.7, ge=0, le=1)
    duration_seconds: int | None = Field(default=None, ge=1, le=86400)
    concurrent: bool = True


class SimulationStatus(BaseModel):
    simulation_id: UUID
    status: str
    scenarios: list[ScenarioName]
    seed: int
    generated_events: int = 0
    published_events: int = 0
    started_at: datetime
    stopped_at: datetime | None = None
    error: str | None = None
