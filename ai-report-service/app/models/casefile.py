from __future__ import annotations
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CaseFileDocument(BaseModel):
    """Versioned CaseFile wire contract; no InvestigationContext is accepted."""
    model_config = ConfigDict(extra='forbid', frozen=True)
    case_id: UUID
    metadata: dict[str, Any]
    executive_summary: dict[str, Any] = Field(default_factory=dict)
    technical_summary: dict[str, Any] = Field(default_factory=dict)
    timeline: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)
    threat: dict[str, Any] = Field(default_factory=dict)
    knowledge: dict[str, Any] = Field(default_factory=dict)
    graph: dict[str, Any] = Field(default_factory=dict)
    historical: dict[str, Any] = Field(default_factory=dict)
    hypotheses: dict[str, Any] = Field(default_factory=dict)
    confidence: dict[str, Any] = Field(default_factory=dict)
    decision: dict[str, Any] = Field(default_factory=dict)
    recommendations: dict[str, Any] = Field(default_factory=dict)
    execution: dict[str, Any] = Field(default_factory=dict)
    references: dict[str, Any] = Field(default_factory=dict)
    attachments: dict[str, Any] = Field(default_factory=dict)
    audit: dict[str, Any] = Field(default_factory=dict)
    version: dict[str, Any]
    statistics: dict[str, Any] = Field(default_factory=dict)
    relationships: tuple[dict[str, Any], ...] = ()
    context_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator('metadata')
    @classmethod
    def identity_is_present(cls, value: dict[str, Any]) -> dict[str, Any]:
        for key in ('investigation_id', 'tenant_id', 'correlation_id'):
            if not value.get(key):
                raise ValueError(f'CaseFile metadata.{key} is required')
        return value
