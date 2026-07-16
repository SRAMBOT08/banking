from __future__ import annotations
from typing import Any
from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .builder import CaseBuilder
from .exceptions import CaseBuilderError


class BuildCaseRequest(BaseModel):
    context: dict[str, Any]
    created_by: str = Field(default='system', min_length=1)
    case_id: UUID | None = None
    change_summary: str = 'case build'


def create_api_router(builder: CaseBuilder) -> APIRouter:
    router = APIRouter(prefix='/api/v1/cases', tags=['case-builder'])
    @router.post('/build', status_code=201)
    async def build_case(request: BuildCaseRequest):
        try: return builder.build(request.context, created_by=request.created_by, case_id=request.case_id, change_summary=request.change_summary)
        except CaseBuilderError as exc: raise HTTPException(400, str(exc)) from exc
    return router
