from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field


class CreateExecutionRequest(BaseModel):
    case_file: dict
    created_by: str = Field(default='system', min_length=1)


class ApprovalRequest(BaseModel):
    approver: str = Field(min_length=1)
    reason: str = ''


def create_case_router() -> APIRouter:
    router = APIRouter(prefix='/api/v1/executions', tags=['case-executions'])
    @router.post('', status_code=201)
    async def create(request: Request, payload: CreateExecutionRequest):
        try: return request.app.state.case_execution_service.create(payload.case_file, payload.created_by)
        except (ValueError, KeyError) as exc: raise HTTPException(422, str(exc)) from exc
    @router.get('/history')
    async def history(request: Request, tenant_id: str | None = None, status: str | None = None):
        return request.app.state.case_execution_repository.search({'tenant_id': tenant_id, 'status': status})
    @router.get('/statistics')
    async def statistics(request: Request): return request.app.state.case_execution_repository.statistics()
    @router.post('/{execution_id}/approve')
    async def approve(request: Request, execution_id: UUID, payload: ApprovalRequest):
        try: return request.app.state.case_execution_service.approve(execution_id, payload.approver, payload.reason)
        except KeyError as exc: raise HTTPException(404, 'execution not found') from exc
        except ValueError as exc: raise HTTPException(409, str(exc)) from exc
    @router.get('/{execution_id}')
    async def get_execution(request: Request, execution_id: UUID):
        try: return request.app.state.case_execution_service.get(execution_id)
        except KeyError as exc: raise HTTPException(404, 'execution not found') from exc
    @router.get('/{execution_id}/status')
    async def get_status(request: Request, execution_id: UUID):
        try: return request.app.state.case_execution_service.status(execution_id)
        except KeyError as exc: raise HTTPException(404, 'execution not found') from exc
    return router
