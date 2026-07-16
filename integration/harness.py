from __future__ import annotations
import hashlib, json, sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL

ROOT = Path(__file__).parents[1]
SIMULATOR = ROOT / 'event-simulator'
if str(SIMULATOR) not in sys.path: sys.path.insert(0, str(SIMULATOR))
from app.engine import ScenarioEngine
from app.models import ScenarioName


@dataclass
class StageMetric:
    name: str
    started_at: datetime
    completed_at: datetime
    records: int
    retries: int = 0
    failures: int = 0
    correlation_id: str = ''
    investigation_id: str = ''
    case_id: str = ''
    execution_id: str = ''
    report_id: str = ''
    kafka_message_id: str = ''
    @property
    def latency_ms(self) -> float: return (self.completed_at - self.started_at).total_seconds() * 1000


@dataclass
class IntegrationResult:
    scenario: str
    tenant_id: str
    correlation_id: str
    investigation_id: str
    case_id: str
    execution_id: str
    report_id: str
    service_now_ticket: str
    stages: list[StageMetric] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)


class ContractViolation(ValueError): pass


def _require(payload: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if not payload.get(key)]
    if missing: raise ContractViolation(f'missing contract fields: {missing}')


def _stage(result, name, count, fn, **ids):
    start = datetime.now(timezone.utc); value = fn(); end = datetime.now(timezone.utc)
    result.stages.append(StageMetric(name, start, end, count if isinstance(count, int) else len(value), **ids))
    return value


def run_scenario(scenario: ScenarioName, *, tenant_id='integration-bank', seed=2026) -> IntegrationResult:
    events = ScenarioEngine().run([scenario], tenant_id=tenant_id, start=datetime(2026, 1, 1, tzinfo=timezone.utc), seed=seed, noise_ratio=0.25)
    if not events: raise AssertionError('simulator produced no events')
    first = events[0]; correlation_id, investigation_id = str(first.correlation_id), str(first.investigation_id)
    result = IntegrationResult(scenario.value, tenant_id, correlation_id, investigation_id, str(uuid5(NAMESPACE_URL, f'case:{investigation_id}')), str(uuid5(NAMESPACE_URL, f'execution:{investigation_id}:1')), str(uuid5(NAMESPACE_URL, f'report:{investigation_id}:1')), f'INC-{investigation_id[-8:].upper()}')
    _require(first.model_dump(mode='json'), 'event_id', 'correlation_id', 'tenant_id', 'timestamp', 'ingestion_timestamp')
    result.artifacts['simulator'] = _stage(result, 'event-simulator', len(events), lambda: [event.model_dump(mode='json') for event in events], correlation_id=correlation_id, investigation_id=investigation_id, kafka_message_id=str(first.event_id))
    kafka_events = _stage(result, 'kafka', len(events), lambda: result.artifacts['simulator'], correlation_id=correlation_id, investigation_id=investigation_id, kafka_message_id=str(first.event_id))
    normalized = _stage(result, 'ingestion', len(kafka_events), lambda: _normalize(events), correlation_id=correlation_id, investigation_id=investigation_id, kafka_message_id=str(first.event_id))
    evidence = _stage(result, 'evidence', len(normalized), lambda: _evidence(normalized), correlation_id=correlation_id, investigation_id=investigation_id)
    threat = _stage(result, 'threat-intelligence', 1, lambda: _threat(scenario, evidence), correlation_id=correlation_id, investigation_id=investigation_id)
    knowledge = _stage(result, 'knowledge', 1, lambda: {'pattern': scenario.value, 'controls': ['MFA', 'transaction-monitoring']}, correlation_id=correlation_id, investigation_id=investigation_id)
    graph = _stage(result, 'graph', len(evidence['entities']), lambda: {'nodes': evidence['entities'], 'relationships': evidence['relationships']}, correlation_id=correlation_id, investigation_id=investigation_id)
    memory = _stage(result, 'memory', 1, lambda: {'similar_cases': [], 'historical_outcome': 'not_available'}, correlation_id=correlation_id, investigation_id=investigation_id)
    context = _stage(result, 'aggregator', 1, lambda: {'metadata': {'investigation_id': investigation_id, 'tenant_id': tenant_id, 'correlation_id': correlation_id, 'workflow_id': f'wf-{investigation_id[:8]}'}, 'evidence_context': evidence, 'threat_context': threat, 'knowledge_context': knowledge, 'graph_context': graph, 'historical_context': memory, 'timeline': normalized, 'provenance': [{'source_service': 'evidence-intelligence-service', 'source_id': str(first.event_id), 'correlation_id': correlation_id}], 'context_metadata': {'severity': 'high', 'tags': [scenario.value]}, 'execution_metadata': {}}, correlation_id=correlation_id, investigation_id=investigation_id)
    agent = _stage(result, 'investigation-agent', 1, lambda: {'hypotheses': [{'id': 'hyp-1', 'statement': f'{scenario.value} activity is present in supplied telemetry'}], 'confidence_sources': [{'source': 'evidence', 'score': 0.8}], 'final_confidence': 0.8, 'decision': {'action': 'require_review'}}, correlation_id=correlation_id, investigation_id=investigation_id)
    context.update(agent); context['recommendations'] = [{'recommendation_id': 'rec-1', 'title': 'Create incident', 'description': f'Record {scenario.value} investigation', 'operation': 'CREATE_INCIDENT', 'priority': 80}]; context['mitre_mapping'] = ['T1078']
    case_file = _stage(result, 'case-builder', 1, lambda: _case_file(result, context), correlation_id=correlation_id, investigation_id=investigation_id, case_id=result.case_id)
    report = _stage(result, 'ai-report-service', 1, lambda: _report(result, case_file), correlation_id=correlation_id, investigation_id=investigation_id, case_id=result.case_id, report_id=result.report_id)
    execution = _stage(result, 'execution-service', 1, lambda: _execution(result, case_file), correlation_id=correlation_id, investigation_id=investigation_id, case_id=result.case_id, execution_id=result.execution_id)
    snow = _stage(result, 'servicenow-adapter', 1, lambda: {'ticket': result.service_now_ticket, 'status': 'created', 'mock': True}, correlation_id=correlation_id, investigation_id=investigation_id, case_id=result.case_id, execution_id=result.execution_id)
    result.artifacts.update({'aggregated_context': context, 'case_file': case_file, 'report': report, 'execution': execution, 'servicenow': snow})
    return result


def _normalize(events):
    seen = set(); output = []
    for event in events:
        item = event.model_dump(mode='json'); event_id = item['event_id']
        if event_id in seen: continue
        seen.add(event_id); item['normalized'] = True; output.append(item)
    return output


def _evidence(events):
    entities = [{'id': f"{event['source_id']}:{event['sequence']}", 'type': event['event_type'], 'event_id': event['event_id']} for event in events]
    relationships = [{'from': entities[i - 1]['id'], 'to': entity['id'], 'type': 'OBSERVED_BEFORE'} for i, entity in enumerate(entities) if i]
    return {'items': [{'event_id': event['event_id'], 'action': event['payload'].get('action')} for event in events], 'entities': entities, 'relationships': relationships}


def _threat(scenario, evidence): return {'items': [{'pattern_name': scenario.value, 'matched_evidence': [item['event_id'] for item in evidence['items']], 'deterministic': True}], 'mitre_mapping': ['T1078']}

def _case_file(result, context):
    return {'case_id': result.case_id, 'metadata': {'case_id': result.case_id, **context['metadata'], 'title': f'{result.scenario} investigation', 'severity': 'high'}, 'executive_summary': {'title': result.scenario, 'description': 'Deterministic integration case'}, 'technical_summary': {'title': 'Technical summary'}, 'timeline': {'events': context['timeline'], 'items': context['timeline']}, 'evidence': context['evidence_context'], 'threat': context['threat_context'], 'knowledge': context['knowledge_context'], 'graph': context['graph_context'], 'historical': context['historical_context'], 'hypotheses': {'hypotheses': context['hypotheses']}, 'confidence': {'sources': context['confidence_sources'], 'final_score': context['final_confidence']}, 'decision': {'decision': context['decision']}, 'recommendations': {'recommendations': context['recommendations']}, 'execution': {}, 'references': {}, 'attachments': {}, 'audit': {'provenance': context['provenance']}, 'version': {'version': 1, 'content_hash': hashlib.sha256(json.dumps(context, sort_keys=True, default=str).encode()).hexdigest()}, 'statistics': {}, 'context_metadata': context.get('context_metadata', {})}

def _report(result, case_file): return {'report_id': result.report_id, 'case_id': result.case_id, 'case_version': 1, 'traceability': [result.case_id], 'format': 'markdown', 'content': f'# {case_file["metadata"]["title"]}\n\n## Traceability\n{result.case_id}'}
def _execution(result, case_file): return {'execution_id': result.execution_id, 'case_id': result.case_id, 'case_version': 1, 'status': 'APPROVED', 'actions': [{'operation': 'CREATE_INCIDENT', 'payload': {'case_id': result.case_id}}], 'audit': {'policy_decision': 'ALLOWED'}}
