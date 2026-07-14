from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas import DryRunRequest, DryRunResponse, ExecuteRequest, ExecuteResponse

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    return (await request.app.state.health_service.check()).model_dump(mode="json")


@router.post("/dry-run", response_model=DryRunResponse)
async def dry_run(request: Request, payload: DryRunRequest):
    try:
        preview = request.app.state.adapter_service.dry_run(payload.task)
        return DryRunResponse(preview=preview)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/execute", response_model=ExecuteResponse)
async def execute(request: Request, payload: ExecuteRequest):
    result = await request.app.state.adapter_service.process_task(payload.task)
    if not result.success:
        raise HTTPException(status_code=502, detail=result.model_dump(mode="json"))
    return ExecuteResponse(result=result)
