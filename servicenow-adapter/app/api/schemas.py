from __future__ import annotations

from pydantic import BaseModel

from app.models import ExecutionResult, ExecutionTask


class DryRunRequest(BaseModel):
    task: ExecutionTask


class DryRunResponse(BaseModel):
    preview: dict


class ExecuteRequest(BaseModel):
    task: ExecutionTask


class ExecuteResponse(BaseModel):
    result: ExecutionResult
