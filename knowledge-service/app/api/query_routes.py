from __future__ import annotations
from typing import Callable
from fastapi import APIRouter, HTTPException, Query
from app.query.models import KnowledgeSearchRequest
from app.query.service import KnowledgeQueryService


def create_query_router(service: KnowledgeQueryService) -> APIRouter:
    router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge-query"])

    def required(getter: Callable, identifier: str):
        item = getter(identifier)
        if item is None: raise HTTPException(status_code=404, detail="knowledge item not found")
        return item

    @router.post("/search")
    async def search(request: KnowledgeSearchRequest): return service.search(request)
    @router.get("/statistics")
    async def statistics(): return service.statistics()
    @router.get("/metadata")
    async def metadata(): return service.metadata()
    @router.get("/validation")
    async def validation(): return service.validate()
    @router.get("/pattern/{item_id}")
    async def pattern(item_id: str): return required(service.find_pattern, item_id)
    @router.get("/mitre/technique/{item_id}")
    async def technique(item_id: str): return required(service.find_technique, item_id)
    @router.get("/mitre/tactic/{item_id}")
    async def tactic(item_id: str): return required(service.find_tactic, item_id)
    @router.get("/playbook/{item_id}")
    async def playbook(item_id: str): return required(service.find_playbook, item_id)
    @router.get("/fraud/{item_id}")
    async def fraud(item_id: str): return required(service.find_fraud_pattern, item_id)
    @router.get("/control/{item_id}")
    async def control(item_id: str): return required(service.find_control, item_id)
    @router.get("/recommendation/{item_id}")
    async def recommendation(item_id: str): return required(service.find_recommendation, item_id)
    @router.get("/detection/{item_id}")
    async def detection(item_id: str): return required(service.find_detection_rule, item_id)
    @router.get("/indicator/{item_id}")
    async def indicator(item_id: str): return required(service.find_indicator, item_id)
    @router.get("/quantum/{item_id}")
    async def quantum(item_id: str): return required(service.find_quantum_pattern, item_id)
    @router.get("/relationship/{relationship_id}")
    async def relationship(relationship_id: str): return required(service.find_relationship, relationship_id)
    @router.get("/relationship/item/{item_id}")
    async def item_relationships(item_id: str): return {"items": service.relationships(item_id)}
    @router.get("/version/{item_id}")
    async def versions(item_id: str): return {"items": service.versions(item_id)}
    @router.get("/similar/{item_id}")
    async def similar(item_id: str, limit: int = Query(default=10, ge=1, le=100)): return {"items": service.similar(item_id, limit)}
    @router.get("/{item_id}")
    async def item(item_id: str): return required(service.find_item, item_id)
    return router
