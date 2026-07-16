from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.query_routes import create_query_router
from app.query.in_memory import InMemoryGraphRepository
from app.query.models import GraphExpandRequest, GraphNodeSearchRequest, GraphPathRequest, RelationshipType
from app.query.service import GraphQueryService


def repo():
    return InMemoryGraphRepository()


def test_repository_supports_paths_neighbors_components_and_timeline():
    graph = repo()
    neighborhood = graph.find_neighbors("ip-203.0.113.10", depth=1)
    assert {node.id for node in neighborhood.nodes} >= {"user-001", "device-001", "device-002"}
    path = graph.shortest_path(GraphPathRequest(source_id="account-001", target_id="indicator-001"))
    assert path and path.total_hops == 2
    assert graph.find_connected_nodes("account-001").edge_count >= 10
    assert graph.timeline("account-001").events
    assert graph.evidence_graph("account-001").evidence_ids == ["evidence-001"]


def test_deterministic_algorithms_return_typed_results():
    graph = repo()
    traversal = graph.multi_hop(GraphExpandRequest(node_id="account-001", depth=2))
    assert "incident-001" in {node.id for node in traversal.nodes}
    community = graph.community("account-001")
    assert "account-001" in community.node_ids
    centrality = graph.centrality("ip-203.0.113.10")
    assert centrality.degree >= 3
    assert graph.blast_radius("account-001", depth=2).affected_node_count > 0
    assert graph.risk_propagation("incident-001").node_scores["incident-001"] == 90.0
    assert graph.search(GraphNodeSearchRequest(entity_type="device")).total == 2
    assert graph.search_relationships(__import__("app.query.models", fromlist=["GraphRelationshipSearchRequest"]).GraphRelationshipSearchRequest(relationship_type=RelationshipType.USES_DEVICE))


def test_query_api_is_read_only_and_exposes_required_operations():
    service = GraphQueryService(repo())
    app = FastAPI()
    app.include_router(create_query_router(service))
    client = TestClient(app)
    assert client.get("/api/v1/graph/node/account-001").status_code == 200
    assert client.get("/api/v1/graph/node/account-001/neighbors?depth=2").json()["depth"] == 2
    assert client.get("/api/v1/graph/path?source_id=account-001&target_id=indicator-001").json()["total_hops"] == 2
    assert client.get("/api/v1/graph/community/account-001").status_code == 200
    assert client.get("/api/v1/graph/component/account-001").status_code == 200
    assert client.get("/api/v1/graph/blast-radius/account-001").status_code == 200
    assert client.get("/api/v1/graph/statistics").json()["node_count"] == 15
    assert client.post("/api/v1/graph/search", json={"entity_type": "device"}).json()["total"] == 2
    assert client.post("/api/v1/graph/expand", json={"node_id": "account-001", "depth": 2}).status_code == 200
    assert client.post("/api/v1/graph/subgraph", json={"node_ids": ["account-001", "incident-001"]}).status_code == 200
    assert client.post("/api/v1/graph/node/account-001", json={}).status_code == 405
    assert client.get("/api/v1/graph/node/unknown").status_code == 404
