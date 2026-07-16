from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationContext:
    correlation_id: str | None = None
    investigation_id: str | None = None
    workflow_id: str | None = None
    tenant_id: str | None = None
