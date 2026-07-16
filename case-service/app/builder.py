from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from .audit import AuditManager
from .exceptions import ContextValidationError
from .models import *
from .normalization import CaseNormalizer
from .provenance import ProvenanceManager
from .repository import CaseRepository
from .validation import ContextValidator
from .versioning import CaseVersionManager


class CaseBuilder:
    """Deterministic context-to-case packaging pipeline."""
    def __init__(self, repository: CaseRepository, validator: ContextValidator | None = None, normalizer: CaseNormalizer | None = None, provenance: ProvenanceManager | None = None, versions: CaseVersionManager | None = None, audit: AuditManager | None = None):
        self.repository, self.validator, self.normalizer = repository, validator or ContextValidator(), normalizer or CaseNormalizer()
        self.provenance, self.versions, self.audit = provenance or ProvenanceManager(), versions or CaseVersionManager(), audit or AuditManager()

    def _data(self, context: Any) -> dict[str, Any]: return context.model_dump(mode='python') if hasattr(context, 'model_dump') else dict(context)
    def _section(self, data: dict[str, Any], name: str) -> dict[str, Any]:
        value = data.get(name, {})
        return value if isinstance(value, dict) else {}
    def _refs(self, provenance: tuple[ProvenanceReference, ...], *terms: str) -> tuple[ProvenanceReference, ...]:
        return tuple(item for item in provenance if any(term in item.source_service.lower() or term in (item.source_path or '').lower() for term in terms))

    def build(self, context: Any, *, created_by: str = 'system', case_id: UUID | None = None, change_summary: str = 'case build') -> CaseFile:
        self.validator.validate(context)
        data = self._data(context); metadata = data['metadata']; case_id = case_id or uuid4()
        refs = self.provenance.from_context(context)
        evidence = self._section(data, 'evidence_context'); threat = self._section(data, 'threat_context'); knowledge = self._section(data, 'knowledge_context'); graph = self._section(data, 'graph_context'); historical = self._section(data, 'historical_context')
        timeline = tuple(data.get('timeline') or [])
        recommendations = tuple(data.get('recommendations') or [])
        confidence_sources = tuple(item if isinstance(item, dict) else {} for item in (data.get('confidence_sources') or []))
        execution_metadata = dict(data.get('execution_metadata') or {})
        context_metadata = dict(data.get('context_metadata') or {})
        decision = dict(context_metadata.get('decision') or execution_metadata.get('decision') or {})
        existing = None
        try: existing = self.repository.get(case_id)
        except Exception: pass
        version_number = existing.version.version + 1 if existing else 1
        now = datetime.now(timezone.utc)
        case_metadata = CaseMetadata(case_id=case_id, investigation_id=str(metadata['investigation_id']), tenant_id=str(metadata['tenant_id']), workflow_id=metadata.get('workflow_id'), correlation_id=str(metadata['correlation_id']), title=f"Investigation {metadata['investigation_id']}", severity=str(context_metadata.get('severity', 'unknown')), created_at=now, created_by=created_by, source_services=tuple(sorted({item.source_service for item in refs})), tags=tuple(sorted(set(context_metadata.get('tags', [])))))
        evidence_items = self.normalizer.items(evidence); threat_items = self.normalizer.items(threat); knowledge_items = self.normalizer.items(knowledge); graph_items = self.normalizer.items(graph); history_items = self.normalizer.items(historical)
        summary = f'Packaged {len(evidence_items)} evidence, {len(threat_items)} threat, {len(graph_items)} graph, and {len(history_items)} historical findings.'
        audit_provisional = self.audit.build(case_id=case_id, version=version_number, metadata=metadata, provenance=refs, created_by=created_by, execution_metadata=execution_metadata)
        case = CaseFile(case_id=case_id, metadata=case_metadata, executive_summary=ExecutiveSummary(title=case_metadata.title, description=summary, risk_level=case_metadata.severity, key_findings=tuple(item.get('name', item.get('action', 'finding')) for item in threat_items[:10]), provenance=self._refs(refs, 'threat', 'evidence')), technical_summary=TechnicalSummary(title='Technical investigation summary', description=summary, risk_level=case_metadata.severity, indicators=tuple(evidence_items[:20]), provenance=refs), timeline=TimelineSection(events=timeline, items=timeline, summary=f'{len(timeline)} timeline events', provenance=refs), evidence=EvidenceSection(items=evidence_items, summary=f'{len(evidence_items)} evidence records', provenance=self._refs(refs, 'evidence')), threat=ThreatSection(items=threat_items, summary=f'{len(threat_items)} threat findings', mitre_mapping=tuple(data.get('mitre_mapping') or []), fraud_classification=tuple(data.get('fraud_patterns') or []), provenance=self._refs(refs, 'threat')), knowledge=KnowledgeSection(items=knowledge_items, summary=f'{len(knowledge_items)} knowledge records', provenance=self._refs(refs, 'knowledge')), graph=GraphSection(items=graph_items, relationships=tuple(data.get('graph_relationships') or graph_items), summary=f'{len(graph_items)} graph records', provenance=self._refs(refs, 'graph')), historical=HistoricalSection(items=history_items, similar_cases=tuple(data.get('historical_similar_cases') or history_items), summary=f'{len(history_items)} historical records', provenance=self._refs(refs, 'memory', 'histor')), hypotheses=HypothesisSection(hypotheses=tuple(data.get('hypotheses') or []), summary='Hypotheses as supplied by the completed investigation', provenance=refs), confidence=ConfidenceSection(sources=confidence_sources, final_score=context_metadata.get('final_confidence'), summary='Source confidence values preserved without recalculation', provenance=refs), decision=DecisionSection(decision=decision, decision_version=context_metadata.get('decision_version'), summary='Decision as supplied by the completed investigation', provenance=refs), recommendations=RecommendationSection(recommendations=recommendations, summary=f'{len(recommendations)} recommendations', provenance=refs), execution=ExecutionSection(plan=dict(execution_metadata.get('plan') or {}), execution_metadata=execution_metadata, summary='Execution metadata preserved as an immutable snapshot', provenance=refs), references=ReferenceSection(references=[{'source_service': item.source_service, 'source_id': item.source_id, 'source_path': item.source_path} for item in refs], provenance=refs), attachments=AttachmentSection(provenance=refs), audit=audit_provisional, version=VersionMetadata(version=version_number, version_id=uuid4(), created_at=now, created_by=created_by, parent_version=existing.version.version if existing else None, change_summary=change_summary, content_hash='pending'), statistics=CaseStatistics(event_count=len(timeline), evidence_count=len(evidence_items), threat_count=len(threat_items), hypothesis_count=len(data.get('hypotheses') or []), recommendation_count=len(recommendations), provenance_count=len(refs)), context_metadata=context_metadata)
        version = self.versions.create(case=case, version=version_number, created_by=created_by, parent_version=existing.version.version if existing else None, change_summary=change_summary)
        case = case.model_copy(update={'version': version})
        return self.repository.create(case) if existing is None else self.repository.create_version(case)
