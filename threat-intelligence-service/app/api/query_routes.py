from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.query.models import ThreatSearchRequest
from app.query.service import ThreatQueryService


def create_query_router(query_service: ThreatQueryService) -> APIRouter:
    router = APIRouter(prefix="/api/v1/threat", tags=["threat-query"])

    @router.get("/statistics")
    async def statistics():
        return query_service.statistics()

    @router.get("/metadata")
    async def metadata():
        return query_service.metadata()

    @router.get("/validation")
    async def validation():
        return query_service.validate()

    @router.get("/pattern/{pattern}")
    async def pattern(pattern: str, version: Optional[str] = Query(default=None)):
        item = query_service.find_pattern(pattern, version)
        if item is None:
            raise HTTPException(status_code=404, detail="threat pattern not found")
        return item

    @router.get("/indicator/{indicator}")
    async def indicator(indicator: str):
        item = query_service.find_indicator(indicator)
        if item is None:
            raise HTTPException(status_code=404, detail="threat indicator not found")
        return item

    @router.post("/search")
    async def search(request: ThreatSearchRequest):
        return query_service.search(request)

    @router.get("/{threat_id}")
    async def threat(threat_id: str):
        item = query_service.find_threat(threat_id)
        if item is None:
            raise HTTPException(status_code=404, detail="threat not found")
        return item

    return router
