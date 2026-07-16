from __future__ import annotations
import hashlib, json
from copy import deepcopy
from threading import RLock
from uuid import UUID, uuid4
from ..models import ApprovalRecord, AuditRecord, CaseExecutionPlan, ExecutionStatusView


class CaseExecutionRepository:
    def __init__(self): self._plans = {}; self._approvals = {}; self._audits = []; self._lock = RLock()
    def create(self, plan: CaseExecutionPlan) -> CaseExecutionPlan:
        with self._lock:
            if plan.execution_id in self._plans: raise ValueError('execution already exists; plans are immutable')
            self._plans[plan.execution_id] = deepcopy(plan); self._approvals[plan.execution_id] = tuple(plan.approvals); return deepcopy(plan)
    def get(self, execution_id: UUID) -> CaseExecutionPlan:
        with self._lock:
            if execution_id not in self._plans: raise KeyError(str(execution_id))
            return deepcopy(self._plans[execution_id])
    def update(self, plan: CaseExecutionPlan) -> CaseExecutionPlan:
        with self._lock:
            if plan.execution_id not in self._plans: raise KeyError(str(plan.execution_id))
            self._plans[plan.execution_id] = deepcopy(plan); self._approvals[plan.execution_id] = tuple(plan.approvals); return deepcopy(plan)
    def list(self, case_id: UUID | None = None) -> list[CaseExecutionPlan]:
        with self._lock: values = list(self._plans.values())
        return [deepcopy(item) for item in values if case_id is None or item.case_id == case_id]
    def add_audit(self, execution_id: UUID, case_id: UUID, correlation_id: str, event_type: str, actor: str, details: dict) -> AuditRecord:
        with self._lock:
            previous = self._audits[-1].record_hash if self._audits else ''
            payload = {'execution_id': str(execution_id), 'case_id': str(case_id), 'correlation_id': correlation_id, 'event_type': event_type, 'actor': actor, 'details': details, 'previous_hash': previous}
            digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
            record = AuditRecord(audit_id=uuid4(), occurred_at=__import__('datetime').datetime.now(__import__('datetime').timezone.utc), record_hash=digest, **payload)
            self._audits.append(record); return deepcopy(record)
    def audit(self, execution_id: UUID | None = None) -> list[AuditRecord]:
        with self._lock: return [deepcopy(item) for item in self._audits if execution_id is None or item.execution_id == execution_id]
    def search(self, filters: dict) -> list[CaseExecutionPlan]: return [item for item in self.list() if (not filters.get('tenant_id') or item.tenant_id == filters['tenant_id']) and (not filters.get('status') or item.status.value == filters['status'])]
    def statistics(self) -> dict[str, int]:
        plans = self.list(); return {'execution_count': len(plans), 'action_count': sum(len(p.actions) for p in plans), 'audit_count': len(self._audits)}
