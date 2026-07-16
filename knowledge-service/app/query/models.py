from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KnowledgeCategory(str, Enum):
    MITRE_TECHNIQUE = "mitre_technique"
    MITRE_TACTIC = "mitre_tactic"
    FRAUD = "fraud"
    DETECTION = "detection"
    PLAYBOOK = "playbook"
    CONTROL = "control"
    RECOMMENDATION = "recommendation"
    THREAT_INTELLIGENCE = "threat_intelligence"
    QUANTUM = "quantum"
    POLICY = "policy"
    GENERIC = "generic"


class KnowledgeTag(BaseModel):
    name: str
    value: Optional[str] = None


class KnowledgeSource(BaseModel):
    provider: str
    name: str
    uri: Optional[str] = None
    trust_level: str = "enterprise"


class KnowledgeVersion(BaseModel):
    version: str
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    status: str = "current"
    replacement_id: Optional[str] = None
    changelog: Optional[str] = None


class KnowledgeReference(BaseModel):
    reference_id: str
    title: Optional[str] = None
    uri: Optional[str] = None
    source: Optional[str] = None


class KnowledgeEvidence(BaseModel):
    evidence_type: str
    description: str
    required: bool = True


class KnowledgeRecommendation(BaseModel):
    id: str
    name: str
    description: str
    priority: int = Field(default=50, ge=0, le=100)
    actions: List[str] = Field(default_factory=list)
    references: List[KnowledgeReference] = Field(default_factory=list)


class KnowledgeSummary(BaseModel):
    id: str
    name: str
    category: KnowledgeCategory
    description: str = ""
    version: str = "1.0"
    provider: str = "enterprise"
    tags: List[KnowledgeTag] = Field(default_factory=list)
    deprecated: bool = False


class KnowledgeDetails(KnowledgeSummary):
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[KnowledgeSource] = None
    references: List[KnowledgeReference] = Field(default_factory=list)
    evidence: List[KnowledgeEvidence] = Field(default_factory=list)
    recommendations: List[KnowledgeRecommendation] = Field(default_factory=list)
    versions: List[KnowledgeVersion] = Field(default_factory=list)
    related_ids: List[str] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)


class SecurityControl(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.CONTROL
    control_family: str = ""
    objective: str = ""
    policy_refs: List[str] = Field(default_factory=list)


class MITRETechnique(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.MITRE_TECHNIQUE
    technique_id: str = ""
    tactics: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)


class MITRETactic(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.MITRE_TACTIC
    tactic_id: str = ""
    techniques: List[str] = Field(default_factory=list)


class FraudPattern(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.FRAUD
    indicators: List[str] = Field(default_factory=list)
    risk_score: int = 0
    controls: List[str] = Field(default_factory=list)


class DetectionRule(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.DETECTION
    rule_type: str = ""
    expression: str = ""
    severity: str = "medium"
    techniques: List[str] = Field(default_factory=list)


class ThreatIndicator(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.THREAT_INTELLIGENCE
    indicator_type: str = ""
    pattern: str = ""
    confidence: int = 0
    source_name: str = ""


class Playbook(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.PLAYBOOK
    steps: List[str] = Field(default_factory=list)
    trigger_rules: List[str] = Field(default_factory=list)
    required_controls: List[str] = Field(default_factory=list)


class QuantumThreatPattern(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.QUANTUM
    quantum_risk: str = ""
    migration_actions: List[str] = Field(default_factory=list)


class AttackPattern(KnowledgeDetails):
    category: KnowledgeCategory = KnowledgeCategory.GENERIC
    indicators: List[str] = Field(default_factory=list)
    techniques: List[str] = Field(default_factory=list)


class KnowledgeRelationship(BaseModel):
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    description: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    version: str = "1.0"


class PatternVersion(BaseModel):
    id: str
    item_id: str
    version: KnowledgeVersion
    snapshot: Optional[KnowledgeDetails] = None


class KnowledgeMetadata(BaseModel):
    platform_version: str = "1.0"
    registry_version: str = "1.0"
    provider_count: int = 0
    item_count: int = 0
    relationship_count: int = 0
    categories: Dict[str, int] = Field(default_factory=dict)
    last_updated: Optional[str] = None


class KnowledgeStatistics(BaseModel):
    item_count: int = 0
    relationship_count: int = 0
    provider_count: int = 0
    by_category: Dict[str, int] = Field(default_factory=dict)
    deprecated_count: int = 0
    current_version: str = "1.0"


class KnowledgeValidation(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class KnowledgeSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[KnowledgeCategory] = None
    provider: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    relationship_type: Optional[str] = None
    version: Optional[str] = None
    include_deprecated: bool = False
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class KnowledgeSearchResponse(BaseModel):
    items: List[KnowledgeDetails] = Field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 100
    metadata: KnowledgeMetadata
