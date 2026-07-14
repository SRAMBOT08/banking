from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4


class KnowledgeVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    version: str
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None
    author: Optional[str] = None
    checksum: Optional[str] = None
    status: str = "active"
    deprecated: bool = False
    superseded_by: Optional[str] = None


class PatternMetadata(BaseModel):
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    related_patterns: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class ConfidenceModel(BaseModel):
    required: Dict[str, int] = Field(default_factory=dict)
    optional: Dict[str, int] = Field(default_factory=dict)
    max_score: int = 100

    @validator('max_score')
    def max_positive(cls, v):
        if v <= 0:
            raise ValueError('max_score must be positive')
        return v


class Recommendation(BaseModel):
    id: Optional[str] = None
    steps: List[str] = Field(default_factory=list)
    required_evidence: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class ThreatIndicator(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    weight: Optional[int] = 0
    confidence: Optional[int] = 100
    source: Optional[str]


class MitreTechnique(BaseModel):
    id: str
    name: str
    tactic: Optional[str] = None
    references: List[str] = Field(default_factory=list)


class MitreTactic(BaseModel):
    id: str
    name: str


class FraudPattern(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    indicators: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class PatternRelationship(BaseModel):
    source: str
    target: str
    relationship: str


class KnowledgeStatistics(BaseModel):
    pattern_count: int = 0
    indicator_count: int = 0
    mitre_count: int = 0
    fraud_count: int = 0
    recommendation_count: int = 0
    confidence_model_count: int = 0
    relationship_count: int = 0
    registry_version: str = "1"
    validation_status: str = "unknown"
    cache_hit_rate: float = 0.0
    cache_miss_rate: float = 0.0
    registry_load_time: float = 0.0
    registry_reload_time: float = 0.0
    knowledge_size: int = 0
    provider_count: int = 0

    def __getitem__(self, key: str):
        return getattr(self, key)


class AttackPattern(BaseModel):
    name: str
    version: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[PatternMetadata] = None
    confidence_model: Optional[ConfidenceModel] = None
    recommendations: List[Recommendation] = Field(default_factory=list)
    related_patterns: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    mitre: Optional[Dict[str, Any]] = None
    fraud: Optional[Dict[str, Any]] = None
    weights: Dict[str, Any] = Field(default_factory=dict)

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('name is required')
        return v

    def model_dump_dict(self) -> Dict[str, Any]:
        return self.model_dump()
