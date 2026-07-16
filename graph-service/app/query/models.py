from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    USER = "user"
    ACCOUNT = "account"
    CUSTOMER = "customer"
    DEVICE = "device"
    IP_ADDRESS = "ip_address"
    ENDPOINT = "endpoint"
    SESSION = "session"
    TRANSACTION = "transaction"
    MERCHANT = "merchant"
    BENEFICIARY = "beneficiary"
    COUNTRY = "country"
    GEO_LOCATION = "geo_location"
    BROWSER_FINGERPRINT = "browser_fingerprint"
    AUTHENTICATION_EVENT = "authentication_event"
    SECURITY_EVENT = "security_event"
    INCIDENT = "incident"
    THREAT_INDICATOR = "threat_indicator"
    EVIDENCE = "evidence"
    KNOWLEDGE_ITEM = "knowledge_item"


class RelationshipType(str, Enum):
    AUTHENTICATED_FROM = "AUTHENTICATED_FROM"
    USES_DEVICE = "USES_DEVICE"
    INITIATED_TRANSACTION = "INITIATED_TRANSACTION"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    CONNECTED_TO = "CONNECTED_TO"
    RELATED_TO = "RELATED_TO"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    HAS_EVIDENCE = "HAS_EVIDENCE"
    GENERATED_ALERT = "GENERATED_ALERT"
    LINKED_TO_INCIDENT = "LINKED_TO_INCIDENT"
    HAS_INDICATOR = "HAS_INDICATOR"
    USES_IP = "USES_IP"
    HAS_SESSION = "HAS_SESSION"
    SAME_IDENTITY = "SAME_IDENTITY"
    SAME_DEVICE = "SAME_DEVICE"
    SAME_LOCATION = "SAME_LOCATION"
    SAME_BROWSER = "SAME_BROWSER"
    SAME_ACCOUNT = "SAME_ACCOUNT"
    PART_OF_COMMUNITY = "PART_OF_COMMUNITY"


class GraphNode(BaseModel):
    id: str
    entity_type: EntityType
    name: str = ""
    labels: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class EntityNode(GraphNode):
    entity_type: EntityType = EntityType.USER


class IdentityNode(EntityNode):
    entity_type: EntityType = EntityType.USER
    identity_key: Optional[str] = None


class DeviceNode(EntityNode):
    entity_type: EntityType = EntityType.DEVICE
    device_fingerprint: Optional[str] = None
    operating_system: Optional[str] = None


class IPAddressNode(EntityNode):
    entity_type: EntityType = EntityType.IP_ADDRESS
    address: str = ""
    country: Optional[str] = None


class TransactionNode(EntityNode):
    entity_type: EntityType = EntityType.TRANSACTION
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None


class AccountNode(EntityNode):
    entity_type: EntityType = EntityType.ACCOUNT
    account_number_masked: Optional[str] = None


class CustomerNode(EntityNode):
    entity_type: EntityType = EntityType.CUSTOMER
    customer_reference: Optional[str] = None


class EndpointNode(EntityNode):
    entity_type: EntityType = EntityType.ENDPOINT
    endpoint: Optional[str] = None


class SessionNode(EntityNode):
    entity_type: EntityType = EntityType.SESSION
    session_type: Optional[str] = None


class Relationship(BaseModel):
    id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    observed_at: Optional[datetime] = None
    evidence_ids: List[str] = Field(default_factory=list)


EntityRelationship = Relationship


class GraphPath(BaseModel):
    node_ids: List[str] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    total_hops: int = 0
    total_risk: float = 0.0


class GraphNeighborhood(BaseModel):
    center: GraphNode
    nodes: List[GraphNode] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    depth: int = 1


class GraphComponent(BaseModel):
    id: str
    node_ids: List[str] = Field(default_factory=list)
    edge_count: int = 0
    risk_score: float = 0.0


class GraphCommunity(BaseModel):
    id: str
    node_ids: List[str] = Field(default_factory=list)
    representative_node_id: Optional[str] = None
    density: float = 0.0
    risk_score: float = 0.0


class GraphCentrality(BaseModel):
    node_id: str
    degree: float = 0.0
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    pagerank: float = 0.0


class GraphSimilarity(BaseModel):
    source_id: str
    target_id: str
    score: float = Field(ge=0.0, le=1.0)
    shared_neighbors: List[str] = Field(default_factory=list)


class GraphEvidenceLink(BaseModel):
    relationship_id: str
    evidence_id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class GraphInvestigationLink(BaseModel):
    investigation_id: str
    node_ids: List[str] = Field(default_factory=list)
    relationship_ids: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None


class RiskPropagation(BaseModel):
    source_id: str
    node_scores: Dict[str, float] = Field(default_factory=dict)
    hops: int = 0
    decay: float = Field(default=0.5, ge=0.0, le=1.0)


class GraphStatistics(BaseModel):
    node_count: int = 0
    relationship_count: int = 0
    by_entity_type: Dict[str, int] = Field(default_factory=dict)
    by_relationship_type: Dict[str, int] = Field(default_factory=dict)
    connected_components: int = 0
    average_degree: float = 0.0
    high_risk_node_count: int = 0


class GraphMetadata(BaseModel):
    service_version: str = "1.0"
    repository: str = "in-memory"
    schema_version: str = "1.0"
    supported_entity_types: List[EntityType] = Field(default_factory=lambda: list(EntityType))
    supported_relationship_types: List[RelationshipType] = Field(default_factory=lambda: list(RelationshipType))
    last_updated: Optional[datetime] = None


class GraphTraversalResult(BaseModel):
    start_node_id: str
    nodes: List[GraphNode] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    paths: List[GraphPath] = Field(default_factory=list)
    depth: int = 1
    truncated: bool = False


class GraphNodeSearchRequest(BaseModel):
    query: Optional[str] = None
    entity_type: Optional[EntityType] = None
    labels: List[str] = Field(default_factory=list)
    min_risk_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class GraphNodeSearchResponse(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 100


class GraphRelationshipSearchRequest(BaseModel):
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    relationship_type: Optional[RelationshipType] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class GraphExpandRequest(BaseModel):
    node_id: str
    depth: int = Field(default=1, ge=1, le=10)
    relationship_types: List[RelationshipType] = Field(default_factory=list)
    direction: str = Field(default="both", pattern="^(in|out|both)$")
    max_nodes: int = Field(default=1000, ge=1, le=10000)


class GraphPathRequest(BaseModel):
    source_id: str
    target_id: str
    max_hops: int = Field(default=6, ge=1, le=20)
    relationship_types: List[RelationshipType] = Field(default_factory=list)


class GraphSubgraphRequest(BaseModel):
    node_ids: List[str] = Field(min_length=1, max_length=1000)
    include_neighbors: bool = False
    depth: int = Field(default=1, ge=1, le=5)


class GraphTimelineEvent(BaseModel):
    timestamp: Optional[datetime] = None
    relationship_id: str
    relationship_type: RelationshipType
    source_id: str
    target_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphTimeline(BaseModel):
    node_id: str
    events: List[GraphTimelineEvent] = Field(default_factory=list)


class GraphBlastRadius(BaseModel):
    source_id: str
    nodes: List[GraphNode] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    affected_node_count: int = 0
    max_depth: int = 0
    risk_score: float = 0.0


class GraphEvidenceCorrelation(BaseModel):
    node_id: str
    links: List[GraphEvidenceLink] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)


class GraphInvestigationCorrelation(BaseModel):
    investigation_id: str
    node_ids: List[str] = Field(default_factory=list)
    relationship_ids: List[str] = Field(default_factory=list)
    graph: Optional[GraphTraversalResult] = None
