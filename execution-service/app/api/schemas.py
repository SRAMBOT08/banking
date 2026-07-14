from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CreatePlanRequest(BaseModel):
    payload: Dict[str, Any]


class ApproveTaskRequest(BaseModel):
    task_id: str
    approver: str
    reason: str = "approved"


class CancelTaskRequest(BaseModel):
    task_id: str
    reason: str = "cancelled"


class RetryTaskRequest(BaseModel):
    task_id: str
    reason: str = "retry requested"


class ReplayRequest(BaseModel):
    plan_id: str


class PatchTaskRequest(BaseModel):
    state: Optional[str] = None
    expected_result: Dict[str, Any] = Field(default_factory=dict)
    observed_result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
