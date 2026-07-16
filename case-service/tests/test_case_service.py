from datetime import datetime, timezone
from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from app.builder import CaseBuilder
from app.exceptions import ContextValidationError, ImmutableVersionError
from app.models import CaseFile
from app.query.models import CaseSearchQuery
from app.query.service import CaseQueryService
from app.repository import InMemoryCaseRepository
from app.versioning import CaseVersionManager
from app.main import app


def context(investigation='inv-1', severity='high', final_confidence=.8):
    return {'metadata': {'investigation_id': investigation, 'tenant_id': 'tenant-1', 'workflow_id': 'wf-1', 'correlation_id': 'corr-1'}, 'evidence_context': {'items': [{'id': 'ev-1', 'type': 'login'}]}, 'threat_context': {'items': [{'id': 'th-1', 'name': 'account takeover'}]}, 'knowledge_context': {'items': [{'id': 'kn-1', 'name': 'pattern'}]}, 'graph_context': {'items': [{'id': 'rel-1', 'source': 'user-1', 'target': 'acct-1'}]}, 'historical_context': {'items': [{'id': 'old-1', 'similarity': .8}]}, 'timeline': [{'timestamp': '2026-01-01T08:00:00Z', 'action': 'login'}], 'hypotheses': [{'id': 'hyp-1'}], 'confidence_sources': [{'source': 'evidence', 'score': .8}], 'recommendations': [{'action': 'review'}], 'mitre_mapping': ['T1078'], 'fraud_patterns': ['account_takeover'], 'context_metadata': {'severity': severity, 'final_confidence': final_confidence, 'decision': {'action': 'require_review'}}, 'execution_metadata': {'plan': {'status': 'planned'}} , 'provenance': [{'source_id': 'ev-1', 'originating_service': 'evidence-intelligence-service', 'fact_type': 'evidence', 'fact_id': 'ev-1', 'investigation_id': investigation, 'correlation_id': 'corr-1'}, {'source_id': 'th-1', 'originating_service': 'threat-intelligence-service', 'fact_type': 'threat', 'fact_id': 'th-1', 'investigation_id': investigation, 'correlation_id': 'corr-1'}]}


def test_builder_packages_context_without_recalculation():
    repository = InMemoryCaseRepository()
    case = CaseBuilder(repository).build(context(), created_by='analyst')
    assert isinstance(case, CaseFile)
    assert case.metadata.investigation_id == 'inv-1'
    assert case.threat.mitre_mapping == ('T1078',)
    assert case.confidence.final_score == .8
    assert case.decision.decision['action'] == 'require_review'
    assert len(case.audit.provenance) == 2
    with pytest.raises(Exception): case.metadata = case.metadata


def test_versions_are_append_only_and_comparable():
    repository = InMemoryCaseRepository(); builder = CaseBuilder(repository)
    first = builder.build(context(), case_id=UUID('00000000-0000-0000-0000-000000000001'))
    second = builder.build(context('inv-1', 'critical', .9), case_id=first.case_id, change_summary='updated severity')
    assert first.version.version == 1 and second.version.version == 2
    assert len(repository.versions(first.case_id)) == 2
    with pytest.raises(ImmutableVersionError): repository.create_version(first)
    diff = CaseVersionManager().compare(first, second)
    assert diff['changed'] is True


def test_query_filters_and_statistics():
    repository = InMemoryCaseRepository(); builder = CaseBuilder(repository)
    builder.build(context('inv-a')); builder.build(context('inv-b', 'low', .2))
    service = CaseQueryService(repository)
    assert service.search(CaseSearchQuery(severity='high')).total == 1
    assert service.search(CaseSearchQuery(min_confidence=.5)).total == 1
    assert service.statistics().evidence_count == 2


def test_api_build_and_read_endpoints():
    client = TestClient(app)
    response = client.post('/api/v1/cases/build', json={'context': context(), 'created_by': 'api-test'})
    assert response.status_code == 201
    case_id = response.json()['case_id']
    assert client.get(f'/api/v1/cases/{case_id}').status_code == 200
    assert client.get(f'/api/v1/cases/{case_id}/history').status_code == 200
    assert client.get('/api/v1/cases/statistics').status_code == 200


def test_invalid_context_is_rejected():
    with pytest.raises(ContextValidationError): CaseBuilder(InMemoryCaseRepository()).build({'metadata': {}})
