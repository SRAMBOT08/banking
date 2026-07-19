"""Evidence Graph Service - orchestrates graph operations for evidence."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.graph.client import graph_manager
from app.graph.models import (
    GraphNode,
    GraphRelationship,
    GraphSearchResult,
    EntityNode,
    EvidenceNode,
    IndicatorNode,
    AssetNode,
    AlertNode,
    NodeType,
    RelationshipType,
)
from app.graph.repository import GraphRepository


class EvidenceGraphService:
    """Service for managing evidence graph operations."""

    def __init__(self, repository: Optional[GraphRepository] = None):
        self.repository = repository

    async def initialize(self) -> None:
        """Initialize the graph repository and create indexes."""
        if self.repository:
            await self.repository.create_constraints_and_indexes()

    async def add_evidence_node(self, evidence: Any, tenant_id: str) -> Any:
        """Add an evidence node to the graph."""
        if not self.repository:
            return None
        
        evidence_node = EvidenceNode(
            id=evidence.evidence_id,
            type="Evidence",
            tenant_id=tenant_id,
            evidence_type=evidence.evidence_type,
            source=evidence.source,
            confidence=evidence.confidence,
            timestamp=evidence.timestamp,
            metadata=evidence.properties or {},
        )
        return await self.repository.merge_node(evidence_node)

    async def add_entity_node(self, entity: Any, tenant_id: str) -> Any:
        """Add an entity node to the graph."""
        if not self.repository:
            return None
        
        entity_node = EntityNode(
            id=entity.entity_id,
            type="Entity",
            tenant_id=tenant_id,
            name=entity.name,
            description=entity.description,
            confidence=entity.confidence,
        )
        return await self.repository.merge_node(entity_node)

    async def add_indicator_node(self, indicator: Any, tenant_id: str) -> Any:
        """Add a threat indicator node to the graph."""
        if not self.repository:
            return None
        
        indicator_node = IndicatorNode(
            id=indicator.indicator_id,
            type="Indicator",
            tenant_id=tenant_id,
            indicator_type=indicator.indicator_type,
            value=indicator.value,
            severity=indicator.severity,
            source=indicator.source,
        )
        return await self.repository.merge_node(indicator_node)

    async def add_asset_node(self, asset: Any, tenant_id: str) -> Any:
        """Add an asset node to the graph."""
        if not self.repository:
            return None
        
        asset_node = AssetNode(
            id=asset.asset_id,
            type="Asset",
            tenant_id=tenant_id,
            name=asset.name,
            asset_type=asset.asset_type,
            criticality=asset.criticality,
        )
        return await self.repository.merge_node(asset_node)

    async def add_alert_node(self, alert: Any, tenant_id: str) -> Any:
        """Add an alert node to the graph."""
        if not self.repository:
            return None
        
        alert_node = AlertNode(
            id=alert.alert_id,
            type="Alert",
            tenant_id=tenant_id,
            severity=alert.severity,
            description=alert.description,
            status=alert.status,
        )
        return await self.repository.merge_node(alert_node)

    async def link_evidence_to_entity(
        self, evidence_id: str, entity_id: str, tenant_id: str
    ) -> bool:
        """Create OBSERVED_ON relationship between evidence and entity."""
        if not self.repository:
            return False
        
        rel = GraphRelationship(
            source_id=evidence_id,
            target_id=entity_id,
            type="OBSERVED_ON",
            tenant_id=tenant_id,
        )
        await self.repository.merge_relationship(rel)
        return True

    async def link_entity_to_entity(
        self, source_id: str, target_id: str, relationship_type: str, tenant_id: str
    ) -> bool:
        """Create a relationship between two entities."""
        if not self.repository:
            return False
        
        rel = GraphRelationship(
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            tenant_id=tenant_id,
        )
        await self.repository.merge_relationship(rel)
        return True

    async def link_evidence_to_evidence(
        self, source_id: str, target_id: str, relationship_type: str, tenant_id: str
    ) -> bool:
        """Create a relationship between two evidence nodes."""
        if not self.repository:
            return False
        
        rel = GraphRelationship(
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            tenant_id=tenant_id,
        )
        await self.repository.merge_relationship(rel)
        return True

    async def link_indicator_to_entity(
        self, indicator_id: str, entity_id: str, tenant_id: str
    ) -> bool:
        """Link a threat indicator to an entity."""
        if not self.repository:
            return False
        
        rel = GraphRelationship(
            source_id=indicator_id,
            target_id=entity_id,
            type="TARGETS",
            tenant_id=tenant_id,
        )
        await self.repository.merge_relationship(rel)
        return True

    async def get_evidence_neighborhood(
        self, evidence_id: str, tenant_id: str, depth: int = 2
    ) -> dict:
        """Get the neighborhood of an evidence node."""
        if not self.repository:
            return {}
        
        return await self.repository.find_related_evidence(evidence_id, tenant_id, depth)

    async def get_entity_neighborhood(
        self, entity_id: str, tenant_id: str, depth: int = 2
    ) -> dict:
        """Get the neighborhood of an entity node."""
        if not self.repository:
            return {}
        
        return await self.repository.find_related_entities(entity_id, tenant_id, depth)

    async def find_shortest_path(
        self, source_id: str, target_id: str, tenant_id: str, max_depth: int = 10
    ) -> list:
        """Find the shortest path between two nodes."""
        if not self.repository:
            return []
        
        return await self.repository.find_shortest_path(
            source_id, target_id, tenant_id, max_depth
        )

    async def find_related_alerts(
        self, investigation_id: str, tenant_id: str
    ) -> list:
        """Find alerts related to an investigation."""
        if not self.repository:
            return []
        
        # This would query for alerts connected to the investigation
        return await self.repository.find_related_entities(
            investigation_id, tenant_id, max_depth=3
        )

    async def find_related_devices(
        self, device_id: str, tenant_id: str, max_depth: int = 2
    ) -> list:
        """Find devices related to a device."""
        if not self.repository:
            return []
        
        return await self.repository.find_related_entities(
            device_id, tenant_id, max_depth
        )

    async def find_related_users(
        self, user_id: str, tenant_id: str, max_depth: int = 2
    ) -> list:
        """Find users related to a user."""
        if not self.repository:
            return []
        
        return await self.repository.find_related_entities(
            user_id, tenant_id, max_depth
        )

    async def find_related_ips(
        self, ip_id: str, tenant_id: str, max_depth: int = 2
    ) -> list:
        """Find IPs related to an IP."""
        if not self.repository:
            return []
        
        return await self.repository.find_related_entities(
            ip_id, tenant_id, max_depth
        )

    async def search_nodes(
        self, tenant_id: str, node_type: str = None, filters: dict = None, limit: int = 100
    ) -> list:
        """Search for nodes matching criteria."""
        if not self.repository:
            return []
        
        return await self.repository.search_nodes(tenant_id, node_type, filters, limit)

    async def delete_node(self, node_id: str, tenant_id: str) -> bool:
        """Delete a node and its relationships."""
        if not self.repository:
            return False
        
        return await self.repository.delete_node(node_id, tenant_id)

    async def health_check(self) -> bool:
        """Check graph database connectivity."""
        if not self.repository:
            return False
        return await self.repository.health_check()


# Global instance
evidence_graph_service = EvidenceGraphService()