"""Normalized data models for the ServiceNow pipeline.

These dataclasses define the internal contract between the planner, pipeline,
table executor, and verification layers. They are intentionally free of
networking and execution logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class IncidentRequest:
    """Internal business request produced by the planner.

    This is the canonical upstream contract for the ServiceNow pipeline. It is
    designed to hold planner output before any ServiceNow-specific payload
    normalization occurs.
    """

    short_description: str
    description: str
    priority: Optional[str] = None
    urgency: Optional[str] = None
    impact: Optional[str] = None
    category: Optional[str] = None
    assignment_group: Optional[str] = None
    caller: Optional[str] = None


@dataclass(frozen=True, slots=True)
class IncidentPayload:
    """Normalized payload ready for the table executor.

    This model closely mirrors the eventual ServiceNow request body while
    remaining internal to Hermes. It is the bridge between business request
    semantics and execution transport semantics.
    """

    table: str
    short_description: str
    description: str
    priority: Optional[str] = None
    urgency: Optional[str] = None
    impact: Optional[str] = None
    category: Optional[str] = None
    assignment_group: Optional[str] = None
    caller: Optional[str] = None


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Outcome produced by the table executor.

    The pipeline uses this as the executor-to-verifier handoff and as the
    terminal result when no verification layer is involved.
    """

    success: bool
    message: str
    incident_number: Optional[str] = None
    sys_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """Verification outcome for a completed ServiceNow execution.

    This is the final guardrail result that determines whether the pipeline
    considers the incident creation path confirmed.
    """

    verified: bool
    message: str
