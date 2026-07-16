from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas import (
    ApproveTaskRequest,
    CancelTaskRequest,
    CreatePlanRequest,
    PatchTaskRequest,
    ReplayRequest,
    RetryTaskRequest,
)

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    return {"status": "ok", "service": request.app.state.settings.service_name}


@router.get("/ready")
async def ready(request: Request):
    return {"status": "ready", "service": request.app.state.settings.service_name}


@router.get("/live")
async def live(request: Request):
    return {"status": "ok", "service": request.app.state.settings.service_name}


@router.get("/execution/plans")
async def list_plans(request: Request):
    return {"plans": [plan.model_dump(mode="json") for plan in request.app.state.repository.list_plans()]}


@router.post("/execution/plans")
async def create_plan(request: Request, payload: CreatePlanRequest):
    plan, decisions, approvals = request.app.state.platform.create_plan(payload.payload)
    request.app.state.publisher.publish_plan_created(plan.model_dump(mode="json"), plan.plan_id)
    for decision in decisions:
        request.app.state.publisher.publish_policy_checked(decision.model_dump(mode="json"), plan.plan_id)
    for approval in approvals:
        request.app.state.publisher.publish_awaiting_approval(approval.model_dump(mode="json"), plan.plan_id)
    if not approvals:
        request.app.state.publisher.publish_ready(plan.model_dump(mode="json"), plan.plan_id)
    return {
        "plan": plan.model_dump(mode="json"),
        "policy_decisions": [item.model_dump(mode="json") for item in decisions],
        "approvals": [item.model_dump(mode="json") for item in approvals],
    }


@router.get("/execution/tasks")
async def list_tasks(request: Request, plan_id: str | None = None):
    tasks = request.app.state.repository.list_tasks(plan_id)
    return {"tasks": [task.model_dump(mode="json") for task in tasks]}


@router.patch("/execution/tasks/{task_id}")
async def patch_task(request: Request, task_id: str, payload: PatchTaskRequest):
    try:
        task, verification = request.app.state.platform.patch_task(
            task_id,
            state=payload.state,
            expected_result=payload.expected_result,
            observed_result=payload.observed_result,
            error=payload.error,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
    request.app.state.publisher.publish_started(task.model_dump(mode="json"), task.task_id)
    if task.state.value == "COMPLETED":
        request.app.state.publisher.publish_completed(task.model_dump(mode="json"), task.task_id)
    elif task.state.value == "FAILED":
        request.app.state.publisher.publish_failed(task.model_dump(mode="json"), task.task_id)
    elif task.state.value == "CANCELLED":
        request.app.state.publisher.publish_cancelled(task.model_dump(mode="json"), task.task_id)
    if verification:
        request.app.state.publisher.publish_verified(verification.model_dump(mode="json"), task.task_id)
    return {"task": task.model_dump(mode="json"), "verification": verification.model_dump(mode="json") if verification else None}


@router.post("/execution/approve")
async def approve_task(request: Request, payload: ApproveTaskRequest):
    try:
        task = request.app.state.platform.approve_task(payload.task_id, payload.approver, payload.reason)
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
    request.app.state.publisher.publish_approved(task.model_dump(mode="json"), task.task_id)
    return {"task": task.model_dump(mode="json")}


@router.post("/execution/cancel")
async def cancel_task(request: Request, payload: CancelTaskRequest):
    try:
        task = request.app.state.platform.cancel_task(payload.task_id, payload.reason)
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
    request.app.state.publisher.publish_cancelled(task.model_dump(mode="json"), task.task_id)
    return {"task": task.model_dump(mode="json")}


@router.post("/execution/retry")
async def retry_task(request: Request, payload: RetryTaskRequest):
    try:
        task = request.app.state.platform.retry_task(payload.task_id, payload.reason)
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    request.app.state.publisher.publish_ready(task.model_dump(mode="json"), task.task_id)
    return {"task": task.model_dump(mode="json")}


@router.post("/execution/replay")
async def replay(request: Request, payload: ReplayRequest):
    tasks = request.app.state.platform.replay_plan(payload.plan_id)
    return {"tasks": [task.model_dump(mode="json") for task in tasks]}


@router.get("/execution/status")
async def status(request: Request):
    return {"statistics": request.app.state.platform.statistics().model_dump(mode="json")}


@router.get("/execution/audit")
async def audit(request: Request):
    records = request.app.state.repository.list_audit()
    return {"audit": [record.model_dump(mode="json") for record in records]}


@router.get("/execution/history")
async def history(request: Request, plan_id: str | None = None):
    return request.app.state.repository.get_history(plan_id)


@router.get("/execution/metrics")
async def metrics(request: Request):
    return request.app.state.repository.metrics().model_dump(mode="json")
