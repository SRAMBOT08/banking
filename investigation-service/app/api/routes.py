from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.investigation import InvestigationState
from app.config.settings import settings
from datetime import datetime, timezone
from app.schemas.platform import (InvestigationListResponse, TimelineResponse, MemoryResponse, GraphResponse,
                                  ReplayResponse, TransitionRequest, MetricsResponse, ContextResponse, HealthResponse,
                                  RecommendationsResponse, MissingEvidenceResponse)
from app.models.investigation import Investigation
from app.models.snapshot import InvestigationSnapshot, SnapshotDiff, SnapshotHistory
from pydantic import BaseModel

router = APIRouter()
_manager = None
_context = None
_replay = None
_metrics = None
_publisher = None
_snapshots = None


def configure(manager, context_builder, replay_engine, metrics_engine, publisher=None, snapshot_manager=None):
    global _manager, _context, _replay, _metrics, _publisher, _snapshots
    _manager, _context, _replay, _metrics, _publisher, _snapshots = manager, context_builder, replay_engine, metrics_engine, publisher, snapshot_manager


class SnapshotCreateRequest(BaseModel):
    reason: str = "manual"
    created_by: str = "investigation-service"


def _publish_transition(investigation):
    if _publisher is None:
        return
    timestamp = datetime.now(timezone.utc).isoformat()
    _publisher.publish_investigation(settings.updated_topic, "INVESTIGATION_UPDATED", investigation, timestamp)
    if investigation.state == InvestigationState.CLOSED:
        _publisher.publish_investigation(settings.closed_topic, "INVESTIGATION_CLOSED", investigation, timestamp)
        publish_completed = getattr(_publisher, "publish_completed", None)
        if publish_completed:
            context = _context.build(investigation)
            try:
                snapshot = _snapshots.latest(investigation.investigation_id)
            except (KeyError, AttributeError):
                snapshot = None
            publish_completed(settings.completed_topic, investigation, context, snapshot)
    elif investigation.state == InvestigationState.ESCALATED:
        _publisher.publish_investigation(settings.escalated_topic, "INVESTIGATION_ESCALATED", investigation, timestamp)


def _get(investigation_id: str):
    item = _manager.repository.get(investigation_id)
    if item is None:
        raise HTTPException(status_code=404, detail="investigation not found")
    return item


@router.get("/health", response_model=HealthResponse)
async def health() -> dict:
    return {"status": "ok", "service": "investigation-service"}


@router.get("/live")
async def live() -> dict:
    return {"status": "ok", "service": "investigation-service"}


@router.get("/ready")
async def ready() -> dict:
    return {"status": "ready", "service": "investigation-service",
            "configured": _manager is not None and _publisher is not None}


@router.get("/metrics", response_model=MetricsResponse)
@router.get("/api/v1/metrics", response_model=MetricsResponse)
async def metrics():
    return _metrics.snapshot(_manager.list_all())


@router.get("/investigations", response_model=InvestigationListResponse)
@router.get("/api/v1/investigations", response_model=InvestigationListResponse)
async def list_investigations():
    return {"investigations": _manager.list_all()}


@router.get("/investigations/{investigation_id}", response_model=Investigation)
@router.get("/api/v1/investigations/{investigation_id}", response_model=Investigation)
async def get_investigation(investigation_id: str):
    return _get(investigation_id)


@router.get("/investigations/{investigation_id}/timeline", response_model=TimelineResponse)
@router.get("/api/v1/investigations/{investigation_id}/timeline", response_model=TimelineResponse)
async def timeline(investigation_id: str):
    item = _get(investigation_id)
    return {"investigation_id": investigation_id, "events": item.timeline.events}


@router.get("/investigations/{investigation_id}/memory", response_model=MemoryResponse)
@router.get("/api/v1/investigations/{investigation_id}/memory", response_model=MemoryResponse)
async def memory(investigation_id: str):
    _get(investigation_id)
    return {"investigation_id": investigation_id, "events": _manager.memory.list(investigation_id)}


@router.get("/investigations/{investigation_id}/graph", response_model=GraphResponse)
@router.get("/api/v1/investigations/{investigation_id}/graph", response_model=GraphResponse)
async def graph(investigation_id: str):
    context = _context.build(_get(investigation_id))
    return {"investigation_id": investigation_id, "graph": context.investigation_graph}


@router.get("/investigations/{investigation_id}/context", response_model=ContextResponse)
@router.get("/api/v1/investigations/{investigation_id}/context", response_model=ContextResponse)
async def context(investigation_id: str):
    return _context.build(_get(investigation_id))


@router.get("/investigations/{investigation_id}/replay", response_model=ReplayResponse)
@router.get("/api/v1/investigations/{investigation_id}/replay", response_model=ReplayResponse)
async def replay(investigation_id: str, event_type: str | None = None):
    item = _get(investigation_id)
    return {"investigation_id": investigation_id, "investigation": _replay.replay(item, event_type), "events": _replay.events(investigation_id, event_type)}


@router.get("/investigations/{investigation_id}/recommendations", response_model=RecommendationsResponse)
@router.get("/api/v1/investigations/{investigation_id}/recommendations", response_model=RecommendationsResponse)
async def recommendations(investigation_id: str):
    return {"investigation_id": investigation_id, "recommendations": _get(investigation_id).investigation_plan}


@router.get("/investigations/{investigation_id}/missing-evidence", response_model=MissingEvidenceResponse)
@router.get("/api/v1/investigations/{investigation_id}/missing-evidence", response_model=MissingEvidenceResponse)
async def missing_evidence(investigation_id: str):
    return {"investigation_id": investigation_id, "missing_evidence": _get(investigation_id).missing_evidence}


@router.get("/investigations/{investigation_id}/snapshots", response_model=list[InvestigationSnapshot])
@router.get("/api/v1/investigations/{investigation_id}/snapshots", response_model=list[InvestigationSnapshot])
async def list_snapshots(investigation_id: str):
    _get(investigation_id)
    return _snapshots.list(investigation_id)


@router.get("/investigations/{investigation_id}/snapshots/latest", response_model=InvestigationSnapshot)
@router.get("/api/v1/investigations/{investigation_id}/snapshots/latest", response_model=InvestigationSnapshot)
async def latest_snapshot(investigation_id: str):
    _get(investigation_id)
    try:
        return _snapshots.latest(investigation_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="snapshot not found")


@router.get("/investigations/{investigation_id}/snapshots/diff", response_model=SnapshotDiff)
@router.get("/api/v1/investigations/{investigation_id}/snapshots/diff", response_model=SnapshotDiff)
async def snapshot_diff(investigation_id: str, from_version: int, to_version: int):
    _get(investigation_id)
    try:
        return _snapshots.diff(investigation_id, from_version, to_version)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/investigations/{investigation_id}/snapshots/{version}/context", response_model=InvestigationSnapshot)
@router.get("/api/v1/investigations/{investigation_id}/snapshots/{version}/context", response_model=InvestigationSnapshot)
async def snapshot_context(investigation_id: str, version: int):
    return await get_snapshot(investigation_id, version)


@router.get("/investigations/{investigation_id}/snapshots/{version}", response_model=InvestigationSnapshot)
@router.get("/api/v1/investigations/{investigation_id}/snapshots/{version}", response_model=InvestigationSnapshot)
async def get_snapshot(investigation_id: str, version: int):
    _get(investigation_id)
    try:
        return _snapshots.get(investigation_id, version)
    except KeyError:
        raise HTTPException(status_code=404, detail="snapshot not found")


@router.post("/investigations/{investigation_id}/snapshots", response_model=InvestigationSnapshot)
@router.post("/api/v1/investigations/{investigation_id}/snapshots", response_model=InvestigationSnapshot)
async def create_snapshot(investigation_id: str, request: SnapshotCreateRequest):
    try:
        investigation = _get(investigation_id)
        return _snapshots.create(investigation, reason=request.reason, created_by=request.created_by,
                                 related_investigations=_manager.list_all())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/investigations/{investigation_id}/transition", response_model=Investigation)
@router.post("/api/v1/investigations/{investigation_id}/transition", response_model=Investigation)
async def transition_investigation(investigation_id: str, request: TransitionRequest):
    try:
        result = _manager.transition(investigation_id, request.state)
        _publish_transition(result)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="investigation not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/investigations/{investigation_id}/close", response_model=Investigation)
@router.post("/api/v1/investigations/{investigation_id}/close", response_model=Investigation)
async def close_investigation(investigation_id: str):
    try:
        result = _manager.close(investigation_id)
        _publish_transition(result)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="investigation not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/investigations/{investigation_id}/reopen", response_model=Investigation)
@router.post("/api/v1/investigations/{investigation_id}/reopen", response_model=Investigation)
async def reopen_investigation(investigation_id: str):
    try:
        result = _manager.reopen(investigation_id)
        _publish_transition(result)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="investigation not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
