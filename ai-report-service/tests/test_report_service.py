from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from app.context_builder import ContextBuilder
from app.guardrails import GuardrailError, Guardrails
from app.main import create_app
from app.models import CaseFileDocument, ReportFormat, ReportRequest, ReportType
from app.prompt_builder import PromptBuilder
from app.providers import DeterministicNIMProvider
from app.repository import InMemoryReportRepository
from app.validator import ReportValidationError, ReportValidator

CASE_ID = '00000000-0000-0000-0000-000000000001'

def case_file():
    return {'case_id': CASE_ID, 'metadata': {'investigation_id': 'inv-1', 'tenant_id': 'tenant-1', 'correlation_id': 'corr-1', 'title': 'Test case'}, 'evidence': {'items': [{'id': 'ev-1'}]}, 'version': {'version': 1}, 'audit': {'provenance': [{'source_service': 'evidence'}]}}

def test_context_builder_is_report_specific():
    case = CaseFileDocument.model_validate(case_file())
    context = ContextBuilder().build(case, ReportType.EXECUTIVE)
    assert 'evidence' not in context
    assert 'decision' in context

def test_prompt_and_guardrails_are_deterministic():
    case = CaseFileDocument.model_validate(case_file())
    prompt = PromptBuilder().build(case, ReportType.TECHNICAL)
    assert prompt == PromptBuilder().build(case, ReportType.TECHNICAL)
    Guardrails().validate_prompt(prompt)
    with pytest.raises(GuardrailError): Guardrails(10).validate_prompt(prompt)

def test_validator_rejects_missing_sections():
    with pytest.raises(ReportValidationError): ReportValidator().validate('## Purpose', CaseFileDocument.model_validate(case_file()))

@pytest.mark.asyncio
async def test_generation_and_append_only_repository():
    repository = InMemoryReportRepository(); app = create_app(DeterministicNIMProvider())
    report = await app.state.service.generate(ReportRequest(case_file=case_file(), report_type=ReportType.EXECUTIVE, output_format=ReportFormat.MARKDOWN))
    assert report.case_id == UUID(CASE_ID)
    assert repository.statistics()['report_count'] == 0
    stored = app.state.repository.get(report.report_id)
    assert stored.content == report.content
    assert len(app.state.repository.history(report.case_id)) == 1

def test_api_end_to_end():
    client = TestClient(create_app(DeterministicNIMProvider()))
    response = client.post('/api/v1/reports', json={'case_file': case_file(), 'report_type': 'compliance_summary', 'output_format': 'html'})
    assert response.status_code == 201
    report_id = response.json()['report_id']; case_id = response.json()['case_id']
    assert client.get(f'/api/v1/reports/{report_id}').status_code == 200
    assert client.get(f'/api/v1/reports/case/{case_id}/history').status_code == 200
    assert client.get('/api/v1/reports/statistics').json()['report_count'] == 1
