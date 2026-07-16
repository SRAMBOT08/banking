from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Optional
from .state import InvestigationState, WorkflowStatus


class CheckpointManager:
    def __init__(self):
        self._store: Dict[str, InvestigationState] = {}
        self._metadata: Dict[str, Dict] = {}

    def create_checkpoint(self, state: InvestigationState, reason: str = "workflow") -> str:
        checkpoint_id = InvestigationState.new_checkpoint_id()
        state.add_checkpoint(checkpoint_id)
        self._store[checkpoint_id] = state.snapshot()
        self._metadata[checkpoint_id] = {"investigation_id": state.investigation_id, "node": state.current_node, "reason": reason, "created_at": datetime.now(timezone.utc).isoformat(), "status": "paused"}
        return checkpoint_id

    def restore_checkpoint(self, investigation_id: str) -> Optional[InvestigationState]:
        candidates = [(key, value) for key, value in self._store.items() if value.investigation_id == investigation_id]
        if not candidates:
            return None
        checkpoint_id, state = candidates[-1]
        state = state.snapshot()
        state.add_history({"event": "checkpoint_restored", "checkpoint_id": checkpoint_id})
        self._metadata[checkpoint_id]["status"] = "restored"
        return state

    def resume(self, checkpoint_id: str) -> InvestigationState:
        state = self._store[checkpoint_id].snapshot()
        self._metadata[checkpoint_id]["status"] = "resumed"
        state.add_history({"event": "checkpoint_resumed", "checkpoint_id": checkpoint_id})
        return state

    def pause(self, state: InvestigationState) -> str:
        return self.create_checkpoint(state, "pause")

    def retry(self, state: InvestigationState, reason: str) -> InvestigationState:
        state.record_retry(reason)
        return state

    def rollback(self, state: InvestigationState, checkpoint_id: Optional[str] = None) -> InvestigationState:
        checkpoint_id = checkpoint_id or state.checkpoint_id
        if not checkpoint_id or checkpoint_id not in self._store:
            raise KeyError("No checkpoint available for rollback")
        restored = self._store[checkpoint_id].snapshot()
        restored.transition(WorkflowStatus.ROLLED_BACK, "checkpoint_manager") if restored.workflow_status != WorkflowStatus.ROLLED_BACK else None
        restored.add_history({"event": "rollback", "checkpoint_id": checkpoint_id})
        return restored

    def metadata(self, checkpoint_id: str) -> Dict:
        return dict(self._metadata[checkpoint_id])
