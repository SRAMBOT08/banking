from __future__ import annotations
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SnapshotDocument(BaseModel):
    model_config = ConfigDict(extra="allow")
    metadata: Dict[str, Any]
    investigation: Dict[str, Any]
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: Dict[str, Any]
    confidence_history: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    related_entities: List[str] = Field(default_factory=list)
    related_investigations: List[str] = Field(default_factory=list)
    graph: Dict[str, Any] = Field(default_factory=dict)
    metadata_context: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any]

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        required = {"snapshot_id", "snapshot_version", "investigation_id"}
        missing = required - value.keys()
        if missing:
            raise ValueError(f"snapshot metadata missing: {sorted(missing)}")
        return value

    @property
    def investigation_id(self) -> str:
        return str(self.metadata["investigation_id"])

    @property
    def snapshot_version(self) -> int:
        return int(self.metadata["snapshot_version"])
