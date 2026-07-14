from enum import Enum


class EventType(str, Enum):
    AUTHENTICATION = "authentication"
    TRANSACTION = "transaction"
    THREAT = "threat"
    IDENTITY = "identity"
    ASSET = "asset"
    FRAUD = "fraud"
    EVIDENCE = "evidence"
    INVESTIGATION = "investigation"
    DECISION = "decision"
    EXECUTION = "execution"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Classification(str, Enum):
    ALERT = "alert"
    EVENT = "event"
    METRIC = "metric"
    AUDIT = "audit"


class SourceType(str, Enum):
    TELEMETRY = "telemetry"
    TRANSACTION = "transaction"
    THREAT_FEED = "threat_feed"
    INTERNAL = "internal"


class ProducerService(str, Enum):
    GATEWAY = "gateway"
    INGESTION = "ingestion-service"
    EVIDENCE = "evidence-service"
    KNOWLEDGE = "knowledge-service"
    INVESTIGATION = "investigation-service"
    AI = "ai-service"
    EXECUTION = "execution-service"
    FRONTEND = "frontend"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InvestigationStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DecisionType(str, Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
