from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from ..models import ReportRequest
from ..service import ReportService
from ..query import ReportQueryService


def create_router(service: ReportService, query: ReportQueryService) -> APIRouter:
    router = APIRouter(prefix='/api/v1/reports', tags=['reports'])
    @router.post('', status_code=201)
    async def generate(request: ReportRequest):
        try:
            return await service.generate(request)
        except (ValueError, KeyError) as exc:
            raise HTTPException(422, str(exc)) from exc
    @router.get('/statistics')
    async def statistics(): return query.statistics()
    @router.get('/search')
    async def search(case_id: UUID | None = None, report_type: str | None = None): return query.search({'case_id': case_id, 'report_type': report_type})
    @router.get('/{report_id}')
    async def get_report(report_id: UUID):
        try: return query.get(report_id)
        except KeyError as exc: raise HTTPException(404, 'report not found') from exc
    @router.get('/case/{case_id}/history')
    async def history(case_id: UUID, report_type: str | None = Query(default=None)): return query.history(case_id, report_type)
    return router
