from __future__ import annotations

import logging
from typing import Optional
from .models import *
from .repository import GraphRepository

logger = logging.getLogger("sentineliq.graph.query")


class GraphQueryService:
    """Read application service; graph algorithms remain repository concerns."""

    def __init__(self, repository: GraphRepository):
        self.repository = repository

    def _log(self, operation: str, **extra):
        logger.info({"event": "graph_query", "operation": operation, **extra})

    def find_node(self, node_id: str):
        self._log("node", node_id=node_id)
        return self.repository.find_node(node_id)

    def find_relationship(self, relationship_id: str):
        self._log("relationship", relationship_id=relationship_id)
        return self.repository.find_relationship(relationship_id)

    def neighborhood(self, node_id: str, depth: int = 1, relationship_types=None, direction: str = "both", max_nodes: int = 1000):
        result = self.repository.find_neighbors(node_id, depth, relationship_types, direction, max_nodes)
        self._log("neighborhood", node_id=node_id, traversal_depth=depth, node_count=len(result.nodes), relationship_count=len(result.relationships))
        return result

    def relationships(self, request: GraphRelationshipSearchRequest):
        result = self.repository.search_relationships(request)
        self._log("relationships", result_count=len(result))
        return result

    def entity_lookup(self, request: GraphNodeSearchRequest):
        return self.repository.search(request)

    def shortest_path(self, request: GraphPathRequest):
        result = self.repository.shortest_path(request)
        self._log("shortest_path", source_id=request.source_id, target_id=request.target_id, result_count=1 if result else 0)
        return result

    def multi_hop(self, request: GraphExpandRequest):
        return self.repository.multi_hop(request)

    def breadth_first_search(self, node_id: str, depth: int = 1):
        return self.repository.breadth_first_search(node_id, depth)

    def depth_first_search(self, node_id: str, depth: int = 1):
        return self.repository.depth_first_search(node_id, depth)

    def community_detection(self, node_id: str):
        return self.repository.community(node_id)

    def connected_component(self, node_id: str):
        return self.repository.find_connected_nodes(node_id)

    def timeline(self, node_id: str):
        return self.repository.timeline(node_id)

    def centrality(self, node_id: str):
        return self.repository.centrality(node_id)

    def blast_radius(self, node_id: str, depth: int = 3):
        return self.repository.blast_radius(node_id, depth)

    def evidence_correlation(self, node_id: str):
        return self.repository.evidence_graph(node_id)

    def investigation_correlation(self, investigation_id: str):
        return self.repository.investigation_graph(investigation_id)

    def expand(self, request: GraphExpandRequest):
        return self.repository.multi_hop(request)

    def subgraph(self, request: GraphSubgraphRequest):
        return self.repository.subgraph(request)

    def metadata(self):
        return self.repository.metadata()

    def statistics(self):
        return self.repository.statistics()

    def risk_propagation(self, source_id: str, hops: int = 3, decay: float = 0.5):
        return self.repository.risk_propagation(source_id, hops, decay)

    def similarity(self, source_id: str, target_id: str):
        return self.repository.similarity(source_id, target_id)
