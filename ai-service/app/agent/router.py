from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .state import InvestigationState
from .planner import plan
from typing import Dict

router = APIRouter()


class StartRequest(BaseModel):
    investigation_id: str
    tenant_id: str


@router.post("/agent/start")
def start_investigation(req: StartRequest) -> Dict[str, str]:
    # Minimal entrypoint: plan a graph for the investigation. Actual execution is async and
    # wired into the application where Tools are injected.
    state = InvestigationState(investigation_id=req.investigation_id, tenant_id=req.tenant_id)
    plan_def = plan(state)
    return {"status": "planned", "investigation_id": req.investigation_id, "plan": str(plan_def)}
