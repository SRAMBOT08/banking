from __future__ import annotations
from fastapi import APIRouter, HTTPException, Request
from app.schemas.api import ChatRequest, ReasonRequest, ReportRequest
from app.services.snapshot_client import InvestigationSnapshotClient
from app.reports.generator import ReportGenerator

router = APIRouter()


async def resolve_snapshot(request: Request, payload: ReasonRequest):
    if payload.snapshot is not None:
        return payload.snapshot
    if not payload.investigation_id or payload.snapshot_version is None:
        raise HTTPException(status_code=422, detail="snapshot or investigation_id and snapshot_version is required")
    return await request.app.state.snapshot_client.get(payload.investigation_id, payload.snapshot_version)


@router.get("/health")
async def health(request: Request):
    return {"status": "ok", "service": request.app.state.settings.service_name}


@router.get("/models")
async def models(request: Request):
    provider = request.app.state.provider
    return {"provider": request.app.state.settings.llm_provider, "models": [provider.model_name]}


@router.post("/reason")
async def reason(request: Request, payload: ReasonRequest):
    try:
        snapshot = await resolve_snapshot(request, payload)
        return await request.app.state.service.reason(snapshot, payload.reasoning_type)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/summarize")
async def summarize(request: Request, payload: ReasonRequest):
    payload.reasoning_type = payload.reasoning_type or "executive_summary"
    snapshot = await resolve_snapshot(request, payload)
    return await request.app.state.service.reason(snapshot, payload.reasoning_type)


@router.post("/report")
async def report(request: Request, payload: ReportRequest):
    snapshot = await resolve_snapshot(request, payload)
    context = request.app.state.service.context(snapshot)
    return ReportGenerator().generate(context, payload.report_type, payload.format)


@router.post("/chat")
async def chat(request: Request, payload: ChatRequest):
    snapshot = await resolve_snapshot(request, payload)
    return await request.app.state.service.reason(snapshot, "chat", payload.message)


@router.get("/history/{investigation_id}")
async def history(request: Request, investigation_id: str):
    return {"investigation_id": investigation_id, "items": request.app.state.conversation.list(investigation_id)}


@router.get("/history")
async def history_required_id(request: Request, investigation_id: str):
    return {"investigation_id": investigation_id, "items": request.app.state.conversation.list(investigation_id)}


@router.get("/metrics")
async def metrics(request: Request):
    result = request.app.state.metrics.snapshot()
    result["cache_hits"] = request.app.state.cache.hits
    result["cache_misses"] = request.app.state.cache.misses
    return result
