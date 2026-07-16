from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ..query.models import *
from ..query.service import InvestigationMemoryQueryService


def create_query_router(service: InvestigationMemoryQueryService) -> APIRouter:
    router = APIRouter(prefix="/api/v1/memory", tags=["investigation-memory"])

    @router.get("/investigation/{investigation_id}", response_model=InvestigationRecord)
    def investigation(investigation_id: str):
        result = service.lookup(investigation_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"completed investigation not found: {investigation_id}")
        return result

    @router.get("/similar/{investigation_id}", response_model=InvestigationSimilarity)
    def similar(investigation_id: str, limit: int = Query(10, ge=1, le=100)):
        return service.similarity(SimilarityRequest(investigation_id=investigation_id, limit=limit))

    @router.get("/timeline/{entity_id}", response_model=InvestigationTimeline)
    def timeline(entity_id: str, timeline_type: str = "entity"):
        return service.timeline(entity_id, timeline_type)

    @router.get("/statistics", response_model=InvestigationStatistics)
    def statistics():
        return service.statistics()

    @router.get("/metadata", response_model=MemoryMetadata)
    def metadata():
        return service.metadata()

    @router.get("/outcome/{investigation_id}", response_model=InvestigationOutcome)
    def outcome(investigation_id: str):
        result = service.outcome(investigation_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"outcome not found: {investigation_id}")
        return result

    @router.get("/resolution/{investigation_id}", response_model=ResolutionPattern)
    def resolution(investigation_id: str):
        result = service.resolution(investigation_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"resolution not found: {investigation_id}")
        return result

    @router.get("/lessons/{investigation_id}", response_model=LessonsLearned)
    def lessons(investigation_id: str):
        result = service.lessons(investigation_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"lessons not found: {investigation_id}")
        return result

    @router.get("/related/{investigation_id}", response_model=list[InvestigationSummary])
    def related(investigation_id: str):
        return service.related(investigation_id)

    @router.get("/evidence/{investigation_id}", response_model=list[HistoricalEvidence])
    def evidence(investigation_id: str):
        return service.historical_evidence(investigation_id)

    @router.get("/threat/{investigation_id}", response_model=list[HistoricalThreat])
    def threat(investigation_id: str):
        return service.historical_threat(investigation_id)

    @router.get("/knowledge/{investigation_id}", response_model=list[HistoricalKnowledge])
    def knowledge(investigation_id: str):
        return service.historical_knowledge(investigation_id)

    @router.get("/graph/{investigation_id}", response_model=list[HistoricalGraph])
    def graph(investigation_id: str):
        return service.historical_graph(investigation_id)

    @router.post("/search", response_model=InvestigationSearchResponse)
    def search(request: InvestigationSearchRequest):
        return service.search(request)

    @router.post("/similarity", response_model=InvestigationSimilarity)
    def similarity(request: SimilarityRequest):
        return service.similarity(request)

    return router
