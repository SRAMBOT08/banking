"""Graph domain models."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of nodes in the graph."""
    ENTITY = "Entity"
    EVIDENCE = "Evidence"
    INDICATOR = "Indicator"
    ASSET = "Asset"
    ALERT = "Alert"
    USER = "User"
    DEVICE = "Device"
    IP_ADDRESS = "IPAddress"
    HOSTNAME = "Hostname"
    FILE_HASH = "FileHash"
    URL = "URL"
    PROCESS = "Process"


class RelationshipType(str, Enum):
    """Types of relationships in the graph."""
    OBSERVED_ON = "OBSERVED_ON"
    USES = "USES"
    CONNECTED_TO = "CONNECTED_TO"
    GENERATED = "GENERATED"
    RELATED_TO = "RELATED_TO"
    TARGETS = "TARGETS"
    RESOLVES_TO = "RESOLVES_TO"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"


class GraphNode(BaseModel):
    """Base graph node model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: NodeType
    tenant_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        use_enum_values = True


class GraphRelationship(BaseModel):
    """Graph relationship model."""
    source_id: str
    target_id: str
    type: RelationshipType
    tenant_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        use_enum_values = True


class EntityNode(GraphNode):
    """Entity node representing a real-world entity."""
    type: NodeType = NodeType.ENTITY
    name: str
    description: Optional[str] = None
    confidence: float = 1.0


class EvidenceNode(GraphNode):
    """Evidence node representing observed facts."""
    type: NodeType = NodeType.EVIDENCE
    evidence_type: str
    source: str
    confidence: float = 1.0
    timestamp: datetime


class IndicatorNode(GraphNode):
    """Threat indicator node."""
    type: NodeType = NodeType.INDICATOR
    indicator_type: str
    value: str
    severity: str = "medium"
    source: str


class AssetNode(GraphNode):
    """Asset node representing infrastructure assets."""
    type: NodeType = NodeType.ASSET
    name: str
    asset_type: str
    criticality: str = "medium"


class AlertNode(GraphNode):
    """Alert node representing security alerts."""
    type: NodeType = NodeType.ALERT
    severity: str
    description: str
    status: str = "open"


class GraphQueryResult(BaseModel):
    """Result of a graph query."""
    nodes: List[GraphNode] = Field(default_factory=list)
    relationships: List[GraphRelationship] = Field(default_factory=list)
    paths: List[List[GraphNode]] = Field(default_factory=list)


class GraphSearchResult(BaseModel):
    """Result of a graph search operation."""
    node: Optional[GraphNode] = None
    neighbors: List[GraphNode] = Field(default_factory=list)
    relationships: List[GraphRelationship] = Field(default_factory=list)


# Type imports
from datetime import timezone