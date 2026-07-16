from __future__ import annotations
import pytest
from integration.harness import ContractViolation, run_scenario
from app.models import ScenarioName

SCENARIOS = (
    ScenarioName.CREDENTIAL_STUFFING,
    ScenarioName.ACCOUNT_TAKEOVER,
    ScenarioName.MONEY_MULE,
    ScenarioName.INSIDER_THREAT,
    ScenarioName.RANSOMWARE,
)


@pytest.mark.parametrize('scenario', SCENARIOS)
def test_complete_deterministic_investigation_pipeline(scenario):
    result = run_scenario(scenario, seed=77)
    assert result.artifacts['simulator']
    assert result.artifacts['aggregated_context']['evidence_context']['items']
    assert result.artifacts['aggregated_context']['threat_context']['items']
    assert result.artifacts['aggregated_context']['knowledge_context']
    assert result.artifacts['aggregated_context']['graph_context']['relationships']
    assert result.artifacts['case_file']['case_id'] == result.case_id
    assert result.artifacts['report']['traceability'] == [result.case_id]
    assert result.artifacts['execution']['case_id'] == result.case_id
    assert result.artifacts['servicenow']['status'] == 'created'
    assert len(result.stages) == 14
    assert all(stage.failures == 0 for stage in result.stages)
    assert all(stage.correlation_id == result.correlation_id for stage in result.stages)


def test_pipeline_replay_is_deterministic_at_contract_level():
    first = run_scenario(SCENARIOS[0], seed=101)
    second = run_scenario(SCENARIOS[0], seed=101)
    assert first.correlation_id == second.correlation_id
    assert first.investigation_id == second.investigation_id
    assert first.case_id == second.case_id
    assert first.artifacts['case_file']['version']['content_hash'] == second.artifacts['case_file']['version']['content_hash']


def test_contract_validation_rejects_missing_identity():
    from integration.harness import _require
    with pytest.raises(ContractViolation): _require({'event_id': 'x'}, 'event_id', 'correlation_id', 'tenant_id')
