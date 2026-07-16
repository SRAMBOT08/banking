from __future__ import annotations

from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
import math
import re
from typing import Iterable, List, Optional, Sequence

from .models import *
from .repository import GraphRepository


class InMemoryGraphRepository(GraphRepository):
    """Deterministic graph repository used locally and as a reference engine.

    A production deployment can replace this class with a Neo4j-backed repository
    without changing the query service or Agent adapter contracts.
    """

    def __init__(self, nodes: Optional[Iterable[GraphNode]] = None, relationships: Optional[Iterable[Relationship]] = None):
        seeded_nodes, seeded_relationships = self._seed() if nodes is None or relationships is None else (list(nodes), list(relationships))
        self._nodes = {node.id: node for node in (nodes if nodes is not None else seeded_nodes)}
        self._relationships = {edge.id: edge for edge in (relationships if relationships is not None else seeded_relationships)}
        self._adjacency: dict[str, list[tuple[str, Relationship]]] = defaultdict(list)
        for edge in self._relationships.values():
            self._adjacency[edge.source_id].append((edge.target_id, edge))
            self._adjacency[edge.target_id].append((edge.source_id, edge))

    @staticmethod
    def _seed() -> tuple[list[GraphNode], list[Relationship]]:
        now = datetime.now(timezone.utc)
        nodes = [
            IdentityNode(id="user-001", name="Customer 001", identity_key="customer-001", risk_score=72, first_seen=now, last_seen=now),
            CustomerNode(id="customer-001", name="Customer 001", customer_reference="CUST-001", risk_score=72, first_seen=now, last_seen=now),
            AccountNode(id="account-001", name="Account ****1001", account_number_masked="****1001", risk_score=68, first_seen=now, last_seen=now),
            DeviceNode(id="device-001", name="Device 001", device_fingerprint="device-fingerprint-001", operating_system="Windows", risk_score=61, first_seen=now, last_seen=now),
            DeviceNode(id="device-002", name="Device 002", device_fingerprint="device-fingerprint-002", operating_system="Android", risk_score=54, first_seen=now, last_seen=now),
            IPAddressNode(id="ip-203.0.113.10", name="203.0.113.10", address="203.0.113.10", country="US", risk_score=78, first_seen=now, last_seen=now),
            IPAddressNode(id="ip-198.51.100.7", name="198.51.100.7", address="198.51.100.7", country="GB", risk_score=45, first_seen=now, last_seen=now),
            SessionNode(id="session-001", name="Session 001", session_type="authentication", risk_score=67, first_seen=now, last_seen=now),
            TransactionNode(id="transaction-001", name="Transaction 001", amount=12500.0, currency="USD", status="review", risk_score=88, first_seen=now, last_seen=now),
            EntityNode(id="beneficiary-001", entity_type=EntityType.BENEFICIARY, name="Beneficiary 001", risk_score=81, first_seen=now, last_seen=now),
            EntityNode(id="merchant-001", entity_type=EntityType.MERCHANT, name="Merchant 001", risk_score=20, first_seen=now, last_seen=now),
            EntityNode(id="evidence-001", entity_type=EntityType.EVIDENCE, name="Authentication evidence", properties={"evidence_type": "authentication_event"}, first_seen=now, last_seen=now),
            EntityNode(id="incident-001", entity_type=EntityType.INCIDENT, name="Account takeover incident", risk_score=90, first_seen=now, last_seen=now),
            EntityNode(id="indicator-001", entity_type=EntityType.THREAT_INDICATOR, name="Suspicious IP indicator", properties={"indicator": "203.0.113.10"}, risk_score=86, first_seen=now, last_seen=now),
            EntityNode(id="knowledge-pattern-account-takeover", entity_type=EntityType.KNOWLEDGE_ITEM, name="Account Takeover Pattern", properties={"knowledge_id": "pattern.account_takeover"}, risk_score=85, first_seen=now, last_seen=now),
        ]
        def edge(edge_id, source, target, kind, evidence=None, **properties):
            return Relationship(id=edge_id, source_id=source, target_id=target, relationship_type=kind, evidence_ids=evidence or [], observed_at=now, properties=properties)
        relationships = [
            edge("rel.user.customer", "user-001", "customer-001", RelationshipType.SAME_IDENTITY),
            edge("rel.customer.account", "customer-001", "account-001", RelationshipType.SAME_ACCOUNT),
            edge("rel.user.device1", "user-001", "device-001", RelationshipType.USES_DEVICE),
            edge("rel.user.device2", "user-001", "device-002", RelationshipType.USES_DEVICE),
            edge("rel.user.ip", "user-001", "ip-203.0.113.10", RelationshipType.USES_IP, ["evidence-001"]),
            edge("rel.device1.ip", "device-001", "ip-203.0.113.10", RelationshipType.CONNECTED_TO, ["evidence-001"]),
            edge("rel.device2.ip", "device-002", "ip-203.0.113.10", RelationshipType.CONNECTED_TO),
            edge("rel.user.session", "user-001", "session-001", RelationshipType.HAS_SESSION),
            edge("rel.session.ip", "session-001", "ip-203.0.113.10", RelationshipType.AUTHENTICATED_FROM, ["evidence-001"]),
            edge("rel.account.transaction", "account-001", "transaction-001", RelationshipType.INITIATED_TRANSACTION),
            edge("rel.transaction.beneficiary", "transaction-001", "beneficiary-001", RelationshipType.TRANSFERRED_TO),
            edge("rel.transaction.merchant", "transaction-001", "merchant-001", RelationshipType.RELATED_TO),
            edge("rel.incident.account", "incident-001", "account-001", RelationshipType.LINKED_TO_INCIDENT, ["evidence-001"]),
            edge("rel.incident.device", "incident-001", "device-001", RelationshipType.LINKED_TO_INCIDENT),
            edge("rel.indicator.ip", "indicator-001", "ip-203.0.113.10", RelationshipType.HAS_INDICATOR),
            edge("rel.incident.indicator", "incident-001", "indicator-001", RelationshipType.GENERATED_ALERT),
            edge("rel.pattern.incident", "knowledge-pattern-account-takeover", "incident-001", RelationshipType.RELATED_TO),
            edge("rel.evidence.session", "evidence-001", "session-001", RelationshipType.HAS_EVIDENCE),
        ]
        return nodes, relationships

    def find_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def find_relationship(self, relationship_id: str) -> Optional[Relationship]:
        return self._relationships.get(relationship_id)

    def _neighbors(self, node_id: str, direction: str = "both", relationship_types: Sequence[RelationshipType] = ()):
        allowed = set(relationship_types)
        for target, edge in self._adjacency.get(node_id, []):
            if allowed and edge.relationship_type not in allowed:
                continue
            outgoing = edge.source_id == node_id
            if direction == "out" and not outgoing:
                continue
            if direction == "in" and outgoing:
                continue
            yield target, edge

    def find_neighbors(self, node_id: str, depth: int = 1, relationship_types=None, direction: str = "both", max_nodes: int = 1000) -> GraphNeighborhood:
        center = self._nodes[node_id]
        discovered = {node_id}
        queue = deque([(node_id, 0)])
        edges: dict[str, Relationship] = {}
        while queue and len(discovered) - 1 < max_nodes:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            for target, edge in self._neighbors(current, direction, relationship_types or ()):
                edges[edge.id] = edge
                if target not in discovered:
                    discovered.add(target)
                    queue.append((target, current_depth + 1))
                    if len(discovered) - 1 >= max_nodes:
                        break
        return GraphNeighborhood(center=center, nodes=[self._nodes[item] for item in discovered if item != node_id], relationships=list(edges.values()), depth=depth)

    def _component_ids(self, node_id: str) -> set[str]:
        seen = {node_id}
        queue = deque([node_id])
        while queue:
            current = queue.popleft()
            for target, _ in self._neighbors(current):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return seen

    def find_connected_nodes(self, node_id: str) -> GraphComponent:
        ids = self._component_ids(node_id)
        edges = [edge for edge in self._relationships.values() if edge.source_id in ids and edge.target_id in ids]
        risk = sum(self._nodes[item].risk_score for item in ids) / max(len(ids), 1)
        return GraphComponent(id=f"component:{node_id}", node_ids=sorted(ids), edge_count=len(edges), risk_score=round(risk, 2))

    def _path_edges(self, node_ids: list[str]) -> list[Relationship]:
        result = []
        for source, target in zip(node_ids, node_ids[1:]):
            edge = next((edge for candidate, edge in self._neighbors(source) if candidate == target), None)
            if edge:
                result.append(edge)
        return result

    def shortest_path(self, request: GraphPathRequest) -> Optional[GraphPath]:
        if request.source_id not in self._nodes or request.target_id not in self._nodes:
            return None
        queue = deque([request.source_id])
        parents: dict[str, Optional[str]] = {request.source_id: None}
        while queue:
            current = queue.popleft()
            if current == request.target_id:
                break
            for target, _ in self._neighbors(current, relationship_types=request.relationship_types):
                if target not in parents and len(self._reconstruct(parents, current)) < request.max_hops:
                    parents[target] = current
                    queue.append(target)
        if request.target_id not in parents:
            return None
        node_ids = self._reconstruct(parents, request.target_id)
        edges = self._path_edges(node_ids)
        return GraphPath(node_ids=node_ids, relationships=edges, total_hops=len(edges), total_risk=round(sum(self._nodes[item].risk_score for item in node_ids) / len(node_ids), 2))

    @staticmethod
    def _reconstruct(parents: dict[str, Optional[str]], node_id: str) -> list[str]:
        result = []
        current: Optional[str] = node_id
        while current is not None:
            result.append(current)
            current = parents.get(current)
        return list(reversed(result))

    def multi_hop(self, request: GraphExpandRequest) -> GraphTraversalResult:
        neighborhood = self.find_neighbors(request.node_id, request.depth, request.relationship_types, request.direction, request.max_nodes)
        node_ids = [request.node_id] + [node.id for node in neighborhood.nodes]
        return GraphTraversalResult(start_node_id=request.node_id, nodes=[self._nodes[item] for item in node_ids], relationships=neighborhood.relationships, depth=request.depth, truncated=len(node_ids) >= request.max_nodes)

    def breadth_first_search(self, node_id: str, depth: int = 1) -> GraphTraversalResult:
        return self.multi_hop(GraphExpandRequest(node_id=node_id, depth=depth))

    def depth_first_search(self, node_id: str, depth: int = 1) -> GraphTraversalResult:
        discovered = {node_id}
        edges: dict[str, Relationship] = {}

        def visit(current: str, remaining: int) -> None:
            if remaining <= 0:
                return
            for target, edge in self._neighbors(current):
                edges[edge.id] = edge
                if target not in discovered:
                    discovered.add(target)
                    visit(target, remaining - 1)

        visit(node_id, depth)
        return GraphTraversalResult(start_node_id=node_id, nodes=[self._nodes[item] for item in discovered], relationships=list(edges.values()), depth=depth)

    def _all_components(self) -> list[set[str]]:
        remaining = set(self._nodes)
        components = []
        while remaining:
            component = self._component_ids(next(iter(remaining)))
            components.append(component)
            remaining -= component
        return components

    def community(self, node_id: str) -> GraphCommunity:
        ids = self._component_ids(node_id)
        edges = [edge for edge in self._relationships.values() if edge.source_id in ids and edge.target_id in ids]
        possible = len(ids) * (len(ids) - 1) / 2
        return GraphCommunity(id=f"community:{node_id}", node_ids=sorted(ids), representative_node_id=max(ids, key=lambda item: self._nodes[item].risk_score), density=round(len(edges) / possible, 4) if possible else 0.0, risk_score=round(sum(self._nodes[item].risk_score for item in ids) / max(len(ids), 1), 2))

    def _centrality_all(self) -> dict[str, GraphCentrality]:
        count = max(len(self._nodes) - 1, 1)
        degrees = {node_id: len({target for target, _ in self._neighbors(node_id)}) for node_id in self._nodes}
        scores = {node_id: 1.0 / max(len(self._nodes), 1) for node_id in self._nodes}
        for _ in range(20):
            next_scores = {node_id: 0.15 / max(len(self._nodes), 1) for node_id in self._nodes}
            for node_id in self._nodes:
                neighbors = {target for target, _ in self._neighbors(node_id)}
                for target in neighbors:
                    next_scores[target] += 0.85 * scores[node_id] / max(len(neighbors), 1)
            scores = next_scores
        betweenness = {node_id: 0.0 for node_id in self._nodes}
        # Deterministic endpoint-excluded shortest-path participation.
        for source in self._nodes:
            for target in self._nodes:
                if source >= target or source == target:
                    continue
                path = self.shortest_path(GraphPathRequest(source_id=source, target_id=target, max_hops=max(len(self._nodes), 1)))
                if path:
                    for intermediary in path.node_ids[1:-1]:
                        betweenness[intermediary] += 1.0
        scale = max((len(self._nodes) - 1) * (len(self._nodes) - 2) / 2, 1)
        return {node_id: GraphCentrality(node_id=node_id, degree=degrees[node_id], degree_centrality=degrees[node_id] / count, betweenness_centrality=betweenness[node_id] / scale, pagerank=scores[node_id]) for node_id in self._nodes}

    def centrality(self, node_id: str) -> GraphCentrality:
        return self._centrality_all()[node_id]

    def blast_radius(self, node_id: str, depth: int = 3) -> GraphBlastRadius:
        result = self.multi_hop(GraphExpandRequest(node_id=node_id, depth=depth, max_nodes=10000))
        return GraphBlastRadius(source_id=node_id, nodes=result.nodes[1:], relationships=result.relationships, affected_node_count=len(result.nodes) - 1, max_depth=depth, risk_score=round(sum(node.risk_score for node in result.nodes) / max(len(result.nodes), 1), 2))

    def investigation_graph(self, investigation_id: str) -> GraphInvestigationCorrelation:
        matching = [node.id for node in self._nodes.values() if node.properties.get("investigation_id") == investigation_id or node.id == investigation_id]
        if not matching and investigation_id:
            matching = ["incident-001"] if investigation_id == "investigation-001" else []
        node_ids = set(matching)
        for node_id in list(node_ids):
            node_ids.update(self._component_ids(node_id))
        edges = [edge.id for edge in self._relationships.values() if edge.source_id in node_ids and edge.target_id in node_ids]
        return GraphInvestigationCorrelation(investigation_id=investigation_id, node_ids=sorted(node_ids), relationship_ids=edges, graph=GraphTraversalResult(start_node_id=matching[0], nodes=[self._nodes[item] for item in node_ids], relationships=[self._relationships[item] for item in edges], depth=1) if matching else None)

    def evidence_graph(self, node_id: str) -> GraphEvidenceCorrelation:
        links = []
        for edge in self._relationships.values():
            if node_id not in {edge.source_id, edge.target_id}:
                continue
            for evidence_id in edge.evidence_ids:
                links.append(GraphEvidenceLink(relationship_id=edge.id, evidence_id=evidence_id, source_id=edge.source_id, target_id=edge.target_id, relationship_type=edge.relationship_type, confidence=edge.confidence))
        return GraphEvidenceCorrelation(node_id=node_id, links=links, evidence_ids=sorted({link.evidence_id for link in links}))

    def timeline(self, node_id: str) -> GraphTimeline:
        events = [GraphTimelineEvent(timestamp=edge.observed_at, relationship_id=edge.id, relationship_type=edge.relationship_type, source_id=edge.source_id, target_id=edge.target_id, properties=edge.properties) for edge in self._relationships.values() if node_id in {edge.source_id, edge.target_id}]
        return GraphTimeline(node_id=node_id, events=sorted(events, key=lambda item: item.timestamp or datetime.min.replace(tzinfo=timezone.utc)))

    def search(self, request: GraphNodeSearchRequest) -> GraphNodeSearchResponse:
        nodes = list(self._nodes.values())
        if request.entity_type:
            nodes = [node for node in nodes if node.entity_type == request.entity_type]
        if request.labels:
            wanted = {label.casefold() for label in request.labels}
            nodes = [node for node in nodes if wanted.intersection(label.casefold() for label in node.labels)]
        if request.min_risk_score is not None:
            nodes = [node for node in nodes if node.risk_score >= request.min_risk_score]
        if request.query:
            query = request.query.casefold()
            nodes = [node for node in nodes if query in f"{node.id} {node.name} {node.entity_type.value} {node.properties}".casefold()]
        total = len(nodes)
        return GraphNodeSearchResponse(nodes=nodes[request.offset:request.offset + request.limit], total=total, offset=request.offset, limit=request.limit)

    def search_relationships(self, request: GraphRelationshipSearchRequest) -> List[Relationship]:
        edges = list(self._relationships.values())
        if request.source_id:
            edges = [edge for edge in edges if edge.source_id == request.source_id]
        if request.target_id:
            edges = [edge for edge in edges if edge.target_id == request.target_id]
        if request.relationship_type:
            edges = [edge for edge in edges if edge.relationship_type == request.relationship_type]
        return edges[request.offset:request.offset + request.limit]

    def subgraph(self, request: GraphSubgraphRequest) -> GraphTraversalResult:
        ids = {node_id for node_id in request.node_ids if node_id in self._nodes}
        if request.include_neighbors:
            for node_id in list(ids):
                ids.update(node.id for node in self.find_neighbors(node_id, request.depth).nodes)
        edges = [edge for edge in self._relationships.values() if edge.source_id in ids and edge.target_id in ids]
        return GraphTraversalResult(start_node_id=request.node_ids[0], nodes=[self._nodes[node_id] for node_id in sorted(ids)], relationships=edges, depth=request.depth)

    def statistics(self) -> GraphStatistics:
        by_entity = Counter(node.entity_type.value for node in self._nodes.values())
        by_relationship = Counter(edge.relationship_type.value for edge in self._relationships.values())
        return GraphStatistics(node_count=len(self._nodes), relationship_count=len(self._relationships), by_entity_type=dict(by_entity), by_relationship_type=dict(by_relationship), connected_components=len(self._all_components()), average_degree=round(2 * len(self._relationships) / max(len(self._nodes), 1), 4), high_risk_node_count=sum(node.risk_score >= 70 for node in self._nodes.values()))

    def metadata(self) -> GraphMetadata:
        return GraphMetadata(repository="in-memory", last_updated=datetime.now(timezone.utc))

    def similarity(self, source_id: str, target_id: str) -> GraphSimilarity:
        source_neighbors = {target for target, _ in self._neighbors(source_id)}
        target_neighbors = {target for target, _ in self._neighbors(target_id)}
        union = source_neighbors | target_neighbors
        shared = sorted(source_neighbors & target_neighbors)
        return GraphSimilarity(source_id=source_id, target_id=target_id, score=round(len(shared) / max(len(union), 1), 4), shared_neighbors=shared)

    def risk_propagation(self, source_id: str, hops: int = 3, decay: float = 0.5) -> RiskPropagation:
        scores = {source_id: self._nodes[source_id].risk_score}
        queue = deque([(source_id, 0)])
        while queue:
            current, distance = queue.popleft()
            if distance >= hops:
                continue
            for target, _ in self._neighbors(current):
                score = self._nodes[source_id].risk_score * (decay ** (distance + 1))
                if score > scores.get(target, 0):
                    scores[target] = round(score, 4)
                    queue.append((target, distance + 1))
        return RiskPropagation(source_id=source_id, node_scores=scores, hops=hops, decay=decay)
