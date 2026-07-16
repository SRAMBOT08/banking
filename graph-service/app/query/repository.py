from __future__ import annotations

from abc import abstractmethod
from typing import List, Optional
from shared.query import BaseQueryRepository
from .models import (
    GraphBlastRadius, GraphCentrality, GraphCommunity, GraphComponent, GraphEvidenceCorrelation,
    GraphExpandRequest, GraphInvestigationCorrelation, GraphMetadata, GraphNeighborhood, GraphNode,
    GraphNodeSearchRequest, GraphNodeSearchResponse, GraphPath, GraphPathRequest, GraphRelationshipSearchRequest,
    GraphStatistics, GraphSubgraphRequest, GraphTimeline, GraphTraversalResult, Relationship,
    GraphSimilarity, RiskPropagation,
)


class GraphRepository(BaseQueryRepository[GraphNodeSearchRequest, GraphNodeSearchResponse]):
    """Read-side repository contract; storage and graph engine details stay behind it."""

    @abstractmethod
    def find_node(self, node_id: str) -> Optional[GraphNode]: ...

    @abstractmethod
    def find_relationship(self, relationship_id: str) -> Optional[Relationship]: ...

    @abstractmethod
    def find_neighbors(self, node_id: str, depth: int = 1, relationship_types=None, direction: str = "both", max_nodes: int = 1000) -> GraphNeighborhood: ...

    @abstractmethod
    def find_connected_nodes(self, node_id: str) -> GraphComponent: ...

    @abstractmethod
    def shortest_path(self, request: GraphPathRequest) -> Optional[GraphPath]: ...

    @abstractmethod
    def multi_hop(self, request: GraphExpandRequest) -> GraphTraversalResult: ...

    @abstractmethod
    def breadth_first_search(self, node_id: str, depth: int = 1) -> GraphTraversalResult: ...

    @abstractmethod
    def depth_first_search(self, node_id: str, depth: int = 1) -> GraphTraversalResult: ...

    @abstractmethod
    def community(self, node_id: str) -> GraphCommunity: ...

    @abstractmethod
    def centrality(self, node_id: str) -> GraphCentrality: ...

    @abstractmethod
    def blast_radius(self, node_id: str, depth: int = 3) -> GraphBlastRadius: ...

    @abstractmethod
    def investigation_graph(self, investigation_id: str) -> GraphInvestigationCorrelation: ...

    @abstractmethod
    def evidence_graph(self, node_id: str) -> GraphEvidenceCorrelation: ...

    @abstractmethod
    def timeline(self, node_id: str) -> GraphTimeline: ...

    @abstractmethod
    def search_relationships(self, request: GraphRelationshipSearchRequest) -> List[Relationship]: ...

    @abstractmethod
    def subgraph(self, request: GraphSubgraphRequest) -> GraphTraversalResult: ...

    @abstractmethod
    def statistics(self) -> GraphStatistics: ...

    @abstractmethod
    def metadata(self) -> GraphMetadata: ...

    @abstractmethod
    def risk_propagation(self, source_id: str, hops: int = 3, decay: float = 0.5) -> RiskPropagation: ...

    @abstractmethod
    def similarity(self, source_id: str, target_id: str) -> GraphSimilarity: ...
