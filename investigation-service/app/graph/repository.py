"""Graph repository interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.graph.models import (
    GraphNode,
    GraphRelationship,
    GraphNode,
    GraphQueryResult,
    GraphSearchResult,
    NodeType,
    RelationshipType,
)


class GraphRepository(ABC):
    """Abstract interface for graph repository operations."""

    @abstractmethod
    async def create_node(self, node: GraphNode) -> GraphNode:
        """Create a new node in the graph."""
        ...

    @abstractmethod
    async def get_node(self, node_id: str, tenant_id: str) -> Optional[GraphNode]:
        """Retrieve a node by ID."""
        ...

    @abstractmethod
    async def update_node(self, node: GraphNode) -> GraphNode:
        """Update an existing node."""
        ...

    @abstractmethod
    async def delete_node(self, node_id: str, tenant_id: str) -> bool:
        """Delete a node and its relationships."""
        ...

    @abstractmethod
    async def create_relationship(self, relationship: GraphRelationship) -> GraphRelationship:
        """Create a relationship between two nodes."""
        ...

    @abstractmethod
    async def get_relationships(
        self, 
        node_id: str, 
        tenant_id: str, 
        relationship_type: Optional[str] = None,
        direction: str = "both"
    ) -> List[GraphRelationship]:
        """Get relationships for a node."""
        ...

    @abstractmethod
    async def get_neighbors(
        self, 
        node_id: str, 
        tenant_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
        limit: int = 100
    ) -> List[GraphNode]:
        """Get neighboring nodes."""
        ...

    @abstractmethod
    async def find_shortest_path(
        self, 
        source_id: str, 
        target_id: str, 
        tenant_id: str,
        max_depth: int = 10
    ) -> List[GraphNode]:
        """Find shortest path between two nodes."""
        ...

    @abstractmethod
    async def search_nodes(
        self,
        tenant_id: str,
        node_type: Optional[str] = None,
        property_filters: dict = None,
        limit: int = 100
    ) -> List[GraphNode]:
        """Search for nodes matching criteria."""
        ...

    @abstractmethod
    async def find_related_evidence(
        self,
        investigation_id: str,
        tenant_id: str,
        depth: int = 2
    ) -> List[GraphNode]:
        """Find evidence related to an investigation."""
        ...

    @abstractmethod
    async def find_related_entities(
        self,
        entity_id: str,
        tenant_id: str,
        max_depth: int = 2
    ) -> List[GraphNode]:
        """Find entities related to a given entity."""
        ...

    @abstractmethod
    async def merge_node(self, node: GraphNode) -> GraphNode:
        """Create or update a node (upsert)."""
        ...

    @abstractmethod
    async def merge_relationship(self, relationship: GraphRelationship) -> GraphRelationship:
        """Create or update a relationship (upsert)."""
        ...

    @abstractmethod
    async def execute_custom_query(self, query: str, parameters: dict) -> list:
        """Execute a custom Cypher query."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check database connectivity."""
        ...

    @abstractmethod
    async def create_constraints_and_indexes(self) -> None:
        """Create necessary constraints and indexes."""
        ...