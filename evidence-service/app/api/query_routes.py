from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.query.models import EvidenceQueryRequest
from app.query.service import EvidenceQueryService


def create_query_router(query_service: EvidenceQueryService) -> APIRouter:
    router = APIRouter(prefix="/api/v1/evidence", tags=["evidence-query"])

    @router.get("/statistics")
    async def statistics():
        return query_service.statistics()

    @router.post("/search")
    async def search(request: EvidenceQueryRequest):
        return query_service.search(request)

    @router.get("/{evidence_id}")
    async def get_evidence(evidence_id: str):
        item = query_service.get_evidence(evidence_id)
        if item is None:
            raise HTTPException(status_code=404, detail="evidence not found")
        return item

    @router.get("/entity/{entity_id}")
    async def get_entity(entity_id: str):
        item = query_service.get_entity(entity_id)
        if item is None:
            raise HTTPException(status_code=404, detail="entity not found")
        return item

    @router.get("/entity/{entity_id}/evidence")
    async def get_entity_evidence(entity_id: str):
        return {"entity_id": entity_id, "items": query_service.get_by_entity(entity_id)}

    @router.get("/{evidence_id}/relationships")
    async def get_relationships(evidence_id: str):
        if query_service.get_evidence(evidence_id) is None:
            raise HTTPException(status_code=404, detail="evidence not found")
        return {"evidence_id": evidence_id, "relationships": query_service.get_relationships(evidence_id)}

    @router.get("/{evidence_id}/timeline")
    async def get_timeline(
        evidence_id: str,
        start_time: Optional[datetime] = Query(default=None),
        end_time: Optional[datetime] = Query(default=None),
    ):
        if query_service.get_evidence(evidence_id) is None:
            raise HTTPException(status_code=404, detail="evidence not found")
        return query_service.get_timeline(EvidenceQueryRequest(query=evidence_id, start_time=start_time, end_time=end_time))

    @router.get("/{evidence_id}/metadata")
    async def get_metadata(evidence_id: str):
        item = query_service.get_metadata(evidence_id)
        if item is None:
            raise HTTPException(status_code=404, detail="evidence not found")
        return item

    @router.get("/{evidence_id}/validation")
    async def validation(evidence_id: str):
        item = query_service.validate(evidence_id)
        if item is None:
            raise HTTPException(status_code=404, detail="evidence not found")
        return item

    return router
