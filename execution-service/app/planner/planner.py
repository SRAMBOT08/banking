from __future__ import annotations
from uuid import uuid5, NAMESPACE_URL
from ..models import AdapterOperation, CaseExecutionPlan, CaseFileInput, ExecutionAction, ExecutionStatus


class CaseExecutionPlanner:
    """Packages CaseFile recommendations; it does not infer or investigate."""
    def _operation(self, item: dict) -> AdapterOperation:
        raw = str(item.get('operation') or item.get('action_type') or 'CREATE_INCIDENT').upper()
        aliases = {'ADD_WORK_NOTES': 'ADD_WORK_NOTE', 'GET_STATUS': 'RETRIEVE_STATUS'}
        return AdapterOperation(aliases.get(raw, raw)) if raw in AdapterOperation.__members__ or aliases.get(raw) in AdapterOperation.__members__ else AdapterOperation.CREATE_INCIDENT

    def build(self, case_file: CaseFileInput, execution_id=None, created_by='system', source_hash='') -> CaseExecutionPlan:
        raw = case_file.recommendations.get('recommendations', case_file.recommendations.get('items', ()))
        items = [item for item in raw if isinstance(item, dict)] if isinstance(raw, (list, tuple)) else []
        items = sorted(items, key=lambda item: str(item.get('recommendation_id') or item.get('id') or item.get('title') or ''))
        action_ids = {str(item.get('recommendation_id') or item.get('id') or f'recommendation-{index + 1}'): uuid5(NAMESPACE_URL, f'{case_file.case_id}:{case_file.case_version}:action:{index}') for index, item in enumerate(items)}
        actions = []
        for index, item in enumerate(items):
            recommendation_id = str(item.get('recommendation_id') or item.get('id') or f'recommendation-{index + 1}')
            depends = tuple(action_ids[value] for value in item.get('depends_on', ()) if str(value) in action_ids)
            action = ExecutionAction(action_id=action_ids[recommendation_id], recommendation_id=recommendation_id, operation=self._operation(item), title=str(item.get('title') or item.get('name') or recommendation_id), description=str(item.get('description') or item.get('details') or ''), priority=max(0, min(100, int(item.get('priority', 100 - index)))), order=index + 1, dependencies=depends, payload={'case_id': str(case_file.case_id), 'investigation_id': case_file.investigation_id, 'tenant_id': case_file.tenant_id, 'recommendation': item})
            actions.append(action)
        if not actions:
            fallback = uuid5(NAMESPACE_URL, f'{case_file.case_id}:{case_file.case_version}:manual-review')
            actions = [ExecutionAction(action_id=fallback, recommendation_id='manual-review', operation=AdapterOperation.ADD_WORK_NOTE, title='Manual approval review', description='No executable recommendation was supplied in the CaseFile.', priority=1, order=1, payload={'case_id': str(case_file.case_id), 'investigation_id': case_file.investigation_id})]
        return CaseExecutionPlan(execution_id=execution_id or CaseExecutionPlan.stable_id(case_file.case_id, case_file.case_version), case_id=case_file.case_id, case_version=case_file.case_version, investigation_id=case_file.investigation_id, tenant_id=case_file.tenant_id, correlation_id=case_file.correlation_id, actions=tuple(actions), policy_decisions=(), approvals=(), status=ExecutionStatus.PLANNED, rollback_strategy=str(case_file.execution.get('rollback_strategy', 'manual_review')), created_at=__import__('datetime').datetime.now(__import__('datetime').timezone.utc), created_by=created_by, source_hash=source_hash)
