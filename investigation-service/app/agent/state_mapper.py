"""Map Investigation domain model to InvestigationState for LangGraph execution."""
from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from app.models.investigation import Investigation, InvestigationState as InvestigationDomainState
from app.agent.state import InvestigationState, WorkflowStatus
from app.core.logger import get_logger

logger = get_logger("state_mapper")


class StateMapper:
    """Converts between Investigation domain model and InvestigationState for LangGraph."""

    @staticmethod
    def to_agent_state(investigation: Investigation, tenant_id: str) -> InvestigationState:
        """Convert Investigation domain model to InvestigationState for LangGraph execution."""
        state = InvestigationState.new(investigation.investigation_id, tenant_id)
        state.workflow_status = WorkflowStatus.COLLECTING_EVIDENCE
        state.evidence = [ev.model_dump() for ev in investigation.evidence]
        state.hypotheses = [h.model_dump() for h in investigation.hypotheses]
        state.confidence_breakdown = {
            "score": investigation.confidence.score,
            "factors": investigation.confidence.factors,
        }
        state.recommendations = [r.model_dump() for r in investigation.investigation_plan]
        state.missing_evidence = [me.model_dump() for me in investigation.missing_evidence]
        state.metadata = {
            "investigation_id": investigation.investigation_id,
            "tenant_id": tenant_id,
            "source_state": investigation.state.value,
            "correlation_ids": investigation.metadata.correlation_ids,
            "severity": getattr(investigation, "severity", "medium"),
            "priority": investigation.priority.value if investigation.priority else "medium",
        }
        state.add_history({
            "event": "agent_state_initialized",
            "source": "candidate_pipeline",
            "investigation_id": investigation.investigation_id,
            "hypothesis_count": len(investigation.hypotheses),
            "evidence_count": len(investigation.evidence),
        })
        logger.info("state_mapped_to_agent", extra={
            "investigation_id": investigation.investigation_id,
            "hypotheses": len(investigation.hypotheses),
            "evidence": len(investigation.evidence),
        })
        return state

    @staticmethod
    def from_agent_state(agent_state: InvestigationState, investigation: Investigation) -> Investigation:
        """Update Investigation domain model from completed InvestigationState."""
        now = datetime.now(timezone.utc).isoformat()
        investigation.metadata.updated_at = datetime.now(timezone.utc)
        investigation.explanation = agent_state.ai_summary or investigation.explanation
        if agent_state.selected_hypothesis:
            selected_id = agent_state.selected_hypothesis.get("pattern_name")
            if selected_id:
                matching = [h for h in investigation.hypotheses if h.pattern_name == selected_id]
                if matching:
                    matching[0].confidence = agent_state.final_confidence or matching[0].confidence

        if agent_state.final_confidence is not None:
            investigation.confidence.score = agent_state.final_confidence
        
        execution_plan = agent_state.execution_plan or {}
        if execution_plan:
            investigation.next_action = execution_plan.get("description", investigation.next_action)
        
        # Map WorkflowStatus to InvestigationState
        status_mapping = {
            WorkflowStatus.COMPLETED: InvestigationDomainState.CLOSED,
            WorkflowStatus.FAILED: InvestigationDomainState.ANALYZING,  # Re-attempt analysis
            WorkflowStatus.ROLLED_BACK: InvestigationDomainState.ANALYZING,  # Back to analysis
        }
        
        new_state = status_mapping.get(agent_state.workflow_status, investigation.state)
        investigation.state = new_state
        
        logger.info("state_mapped_from_agent", extra={
            "investigation_id": investigation.investigation_id,
            "final_workflow_status": agent_state.workflow_status.value,
            "final_investigation_state": new_state.value,
            "final_confidence": agent_state.final_confidence,
            "duration_ms": sum(
                (exec.duration_ms or 0) for exec in agent_state.node_executions
            ),
        })
        return investigation
