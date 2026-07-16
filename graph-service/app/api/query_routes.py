from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from ..query.models import *
from ..query.service import GraphQueryService


def create_query_router(service: GraphQueryService) -> APIRouter:
    router = APIRouter(prefix="/api/v1/graph", tags=["graph-query"])

    @router.get("/node/{node_id}", response_model=GraphNode)
    def node(node_id: str):
        result = service.find_node(node_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")
        return result

    @router.get("/node/{node_id}/neighbors", response_model=GraphNeighborhood)
    def neighbors(node_id: str, depth: int = Query(1, ge=1, le=10), direction: str = Query("both", pattern="^(in|out|both)$"), max_nodes: int = Query(1000, ge=1, le=10000)):
        try:
            return service.neighborhood(node_id, depth=depth, direction=direction, max_nodes=max_nodes)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")

    @router.get("/node/{node_id}/timeline", response_model=GraphTimeline)
    def timeline(node_id: str):
        if service.find_node(node_id) is None:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")
        return service.timeline(node_id)

    @router.get("/relationship/{relationship_id}", response_model=Relationship)
    def relationship(relationship_id: str):
        result = service.find_relationship(relationship_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"graph relationship not found: {relationship_id}")
        return result

    @router.get("/path", response_model=GraphPath)
    def path(source_id: str, target_id: str, max_hops: int = Query(6, ge=1, le=20)):
        result = service.shortest_path(GraphPathRequest(source_id=source_id, target_id=target_id, max_hops=max_hops))
        if result is None:
            raise HTTPException(status_code=404, detail="no graph path found")
        return result

    @router.get("/community/{node_id}", response_model=GraphCommunity)
    def community(node_id: str):
        try:
            return service.community_detection(node_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")

    @router.get("/component/{node_id}", response_model=GraphComponent)
    def component(node_id: str):
        try:
            return service.connected_component(node_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")

    @router.get("/blast-radius/{node_id}", response_model=GraphBlastRadius)
    def blast_radius(node_id: str, depth: int = Query(3, ge=1, le=10)):
        try:
            return service.blast_radius(node_id, depth)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")

    @router.get("/investigation/{investigation_id}", response_model=GraphInvestigationCorrelation)
    def investigation(investigation_id: str):
        return service.investigation_correlation(investigation_id)

    @router.get("/evidence/{node_id}", response_model=GraphEvidenceCorrelation)
    def evidence(node_id: str):
        if service.find_node(node_id) is None:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")
        return service.evidence_correlation(node_id)

    @router.get("/centrality/{node_id}", response_model=GraphCentrality)
    def centrality(node_id: str):
        try:
            return service.centrality(node_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"graph node not found: {node_id}")

    @router.get("/statistics", response_model=GraphStatistics)
    def statistics():
        return service.statistics()

    @router.get("/metadata", response_model=GraphMetadata)
    def metadata():
        return service.metadata()

    @router.post("/search", response_model=GraphNodeSearchResponse)
    def search(request: GraphNodeSearchRequest):
        return service.entity_lookup(request)

    @router.post("/relationships/search", response_model=list[Relationship])
    def search_relationships(request: GraphRelationshipSearchRequest):
        return service.relationships(request)

    @router.post("/expand", response_model=GraphTraversalResult)
    def expand(request: GraphExpandRequest):
        try:
            return service.expand(request)
        except KeyError:
            # A graph expansion over an entity not yet materialized in the
            # repository is a valid empty read result for Agent graph analysis.
            return GraphTraversalResult(start_node_id=request.node_id, depth=request.depth)

    @router.post("/subgraph", response_model=GraphTraversalResult)
    def subgraph(request: GraphSubgraphRequest):
        return service.subgraph(request)

    @router.post("/risk-propagation", response_model=RiskPropagation)
    def risk_propagation(source_id: str, hops: int = Query(3, ge=1, le=10), decay: float = Query(0.5, ge=0.0, le=1.0)):
        try:
            return service.risk_propagation(source_id, hops, decay)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"graph node not found: {source_id}")

    return router
