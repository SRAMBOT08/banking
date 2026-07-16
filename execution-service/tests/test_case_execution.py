from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from app.adapter import ExecutionAdapter, AdapterResult
from app.main import create_app
from app.models.case_execution import AdapterOperation, ExecutionAction, CaseFileInput, ExecutionStatus
from app.policy import CasePolicyEngine
from app.repository import CaseExecutionRepository

CASE_ID = '00000000-0000-0000-0000-000000000010'

def case(severity='low'):
    return {'case_id': CASE_ID, 'metadata': {'investigation_id': 'inv-1', 'tenant_id': 'tenant-1', 'correlation_id': 'corr-1', 'severity': severity, 'title': 'Case'}, 'recommendations': {'recommendations': [{'recommendation_id': 'rec-2', 'title': 'Update incident', 'operation': 'UPDATE_INCIDENT', 'priority': 50}, {'recommendation_id': 'rec-1', 'title': 'Create incident', 'operation': 'CREATE_INCIDENT', 'priority': 90}]}, 'decision': {}, 'execution': {'rollback_strategy': 'restore previous state'}, 'version': {'version': 1}, 'audit': {}}

class FakeAdapter(ExecutionAdapter):
    def supports(self, operation): return True
    async def execute(self, execution_id, action): return AdapterResult(action_id=str(action.action_id), response={'result': {'number': 'INC001'}})

def test_planning_is_deterministic_and_casefile_only():
    app = create_app(); first = app.state.case_execution_service.create(case()); second_app = create_app(); second = second_app.state.case_execution_service.create(case())
    assert first.execution_id == second.execution_id
    assert [a.recommendation_id for a in first.actions] == ['rec-1', 'rec-2']
    assert first.status == ExecutionStatus.APPROVED
    with pytest.raises(Exception): first.status = ExecutionStatus.FAILED

def test_policy_outcomes():
    policy = CasePolicyEngine(); item = CaseFileInput.model_validate(case('high'))
    assert policy.evaluate(item, __import__('app.models.case_execution', fromlist=['ExecutionAction']).ExecutionAction(action_id=UUID('00000000-0000-0000-0000-000000000011'), recommendation_id='r', operation=AdapterOperation.CREATE_INCIDENT, title='x', description='x', order=1)).requires_approval
    assert policy.evaluate(CaseFileInput.model_validate(case('critical')), __import__('app.models.case_execution', fromlist=['ExecutionAction']).ExecutionAction(action_id=UUID('00000000-0000-0000-0000-000000000012'), recommendation_id='r', operation=AdapterOperation.CREATE_INCIDENT, title='x', description='x', order=1)).outcome.value == 'DENIED'

@pytest.mark.asyncio
async def test_execution_requires_approval_and_adapter():
    app = create_app(); waiting = app.state.case_execution_service.create(case('high'))
    assert waiting.status == ExecutionStatus.WAITING_APPROVAL
    app.state.case_execution_service.adapter = FakeAdapter()
    with pytest.raises(ValueError): await app.state.case_execution_service.execute(waiting.execution_id)

def test_repository_audit_isolated_and_hashed():
    app = create_app(); plan = app.state.case_execution_service.create(case())
    audit = app.state.case_execution_repository.audit(plan.execution_id)
    assert audit[0].record_hash and audit[0].previous_hash == ''
    assert app.state.case_execution_repository.get(plan.execution_id).case_id == UUID(CASE_ID)

def test_api_endpoints():
    client = TestClient(create_app()); response = client.post('/api/v1/executions', json={'case_file': case()})
    assert response.status_code == 201
    execution_id = response.json()['execution_id']
    assert client.get(f'/api/v1/executions/{execution_id}').status_code == 200
    assert client.get(f'/api/v1/executions/{execution_id}/status').status_code == 200
    assert client.get('/api/v1/executions/history').status_code == 200
    assert client.get('/api/v1/executions/statistics').json()['execution_count'] == 1
