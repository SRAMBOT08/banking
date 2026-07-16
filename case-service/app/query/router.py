from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from ..exceptions import CaseNotFoundError
from .models import CaseSearchQuery
from .service import CaseQueryService


def create_query_router(service: CaseQueryService) -> APIRouter:
    router = APIRouter(prefix='/api/v1/cases', tags=['cases'])
    def call(function, *args):
        try: return function(*args)
        except CaseNotFoundError as exc: raise HTTPException(404, str(exc)) from exc
    @router.get('/statistics')
    async def statistics(): return service.statistics()
    @router.get('/search')
    async def search(query: CaseSearchQuery = Query()): return service.search(query)
    @router.get('/{case_id}')
    async def get_case(case_id: UUID, version: int | None = None): return call(service.get_case, case_id, version)
    @router.get('/{case_id}/versions')
    async def versions(case_id: UUID): return call(service.versions, case_id)
    @router.get('/{case_id}/history')
    async def history(case_id: UUID): return call(service.history, case_id)
    @router.get('/{case_id}/audit')
    async def audit(case_id: UUID): return call(service.audit, case_id)
    @router.get('/{case_id}/timeline')
    async def timeline(case_id: UUID): return call(service.timeline, case_id)
    return router
