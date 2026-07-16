from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from threading import RLock
from typing import Any
from uuid import UUID
from .exceptions import CaseNotFoundError, ImmutableVersionError
from .models import AuditEntry, CaseFile, CaseHistory, CaseStatistics, VersionMetadata


class CaseRepository(ABC):
    @abstractmethod
    def create(self, case: CaseFile) -> CaseFile: ...
    @abstractmethod
    def create_version(self, case: CaseFile) -> CaseFile: ...
    @abstractmethod
    def get(self, case_id: UUID, version: int | None = None) -> CaseFile: ...
    @abstractmethod
    def versions(self, case_id: UUID) -> tuple[CaseFile, ...]: ...
    @abstractmethod
    def audit(self, case_id: UUID) -> tuple[AuditEntry, ...]: ...
    @abstractmethod
    def search(self, filters: dict[str, Any]) -> list[CaseFile]: ...
    @abstractmethod
    def statistics(self) -> CaseStatistics: ...


class InMemoryCaseRepository(CaseRepository):
    def __init__(self): self._cases: dict[UUID, list[CaseFile]] = {}; self._lock = RLock()
    def _clone(self, case: CaseFile) -> CaseFile: return CaseFile.model_validate(deepcopy(case.model_dump(mode='python')))
    def create(self, case: CaseFile) -> CaseFile:
        with self._lock:
            if case.case_id in self._cases: raise ImmutableVersionError(f'case already exists: {case.case_id}')
            self._cases[case.case_id] = [self._clone(case)]
            return self._clone(case)
    def create_version(self, case: CaseFile) -> CaseFile:
        with self._lock:
            history = self._cases.get(case.case_id)
            if not history: raise CaseNotFoundError(str(case.case_id))
            if case.version.version <= history[-1].version.version: raise ImmutableVersionError('versions cannot be overwritten')
            history.append(self._clone(case)); return self._clone(case)
    def get(self, case_id: UUID, version: int | None = None) -> CaseFile:
        with self._lock:
            history = self._cases.get(case_id)
            if not history: raise CaseNotFoundError(str(case_id))
            selected = history[-1] if version is None else next((item for item in history if item.version.version == version), None)
            if selected is None: raise CaseNotFoundError(f'{case_id}@{version}')
            return self._clone(selected)
    def versions(self, case_id: UUID) -> tuple[CaseFile, ...]:
        with self._lock:
            if case_id not in self._cases: raise CaseNotFoundError(str(case_id))
            return tuple(self._clone(item) for item in self._cases[case_id])
    def audit(self, case_id: UUID) -> tuple[AuditEntry, ...]:
        return tuple(entry for case in self.versions(case_id) for entry in case.audit.entries)
    def search(self, filters: dict[str, Any]) -> list[CaseFile]:
        with self._lock: cases = [history[-1] for history in self._cases.values()]
        def match(case: CaseFile) -> bool:
            metadata = case.metadata
            if filters.get('investigation_id') and metadata.investigation_id != filters['investigation_id']: return False
            if filters.get('customer_id') and metadata.customer_id != filters['customer_id']: return False
            if filters.get('severity') and metadata.severity != filters['severity']: return False
            if filters.get('decision') and case.decision.decision.get('action') != filters['decision']: return False
            if filters.get('min_confidence') is not None and (case.confidence.final_score or 0) < float(filters['min_confidence']): return False
            if filters.get('from_date') and metadata.created_at < filters['from_date']: return False
            if filters.get('to_date') and metadata.created_at > filters['to_date']: return False
            return True
        return [self._clone(case) for case in cases if match(case)]
    def statistics(self) -> CaseStatistics:
        cases = [history[-1] for history in self._cases.values()]
        return CaseStatistics(event_count=sum(len(case.timeline.events) for case in cases), evidence_count=sum(len(case.evidence.items) for case in cases), threat_count=sum(len(case.threat.items) for case in cases), hypothesis_count=sum(len(case.hypotheses.hypotheses) for case in cases), recommendation_count=sum(len(case.recommendations.recommendations) for case in cases), provenance_count=sum(len(case.audit.provenance) for case in cases))
