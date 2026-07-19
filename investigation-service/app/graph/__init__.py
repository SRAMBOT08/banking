"""Graph module initialization."""
from __future__ import annotations

from app.graph.config import settings
from app.graph.client import graph_manager
from app.graph.models import (
    GraphNode,
    GraphRelationship,
    GraphQueryResult,
    GraphSearchResult,
    NodeType,
    RelationshipType,
    EntityNode,
    EvidenceNode,
    IndicatorNode,
    AssetNode,
    AlertNode,
)
from app.graph.repository import GraphRepository
from app.graph.neo4j_repository import Neo4jGraphRepository
from app.graph.service import EvidenceGraphService, evidence_graph_service

__all__ = [
    "settings",
    "graph_manager",
    "GraphNode",
    "GraphRelationship",
    "GraphQueryResult",
    "GraphSearchResult",
    "NodeType",
    "RelationshipType",
    "EntityNode",
    "EvidenceNode",
    "IndicatorNode",
    "AssetNode",
    "AlertNode",
    "GraphRepository",
    "Neo4jGraphRepository",
    "EvidenceGraphService",
    "evidence_graph_service",
]