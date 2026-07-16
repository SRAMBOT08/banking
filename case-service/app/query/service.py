from __future__ import annotations
from uuid import UUID
from ..models import CaseFile, CaseStatistics
from ..repository import CaseRepository
from .models import CaseSearchQuery, CaseSearchResult


class CaseQueryService:
    def __init__(self, repository: CaseRepository): self.repository = repository
    def get_case(self, case_id: UUID, version: int | None = None) -> CaseFile: return self.repository.get(case_id, version)
    def versions(self, case_id: UUID) -> list[CaseFile]: return list(self.repository.versions(case_id))
    def history(self, case_id: UUID) -> list[dict]: return [case.version.model_dump(mode='json') for case in self.repository.versions(case_id)]
    def audit(self, case_id: UUID) -> list: return list(self.repository.audit(case_id))
    def timeline(self, case_id: UUID) -> list[dict]: return list(self.repository.get(case_id).timeline.events)
    def search(self, query: CaseSearchQuery) -> CaseSearchResult:
        items = self.repository.search(query.model_dump(exclude_none=True))
        return CaseSearchResult(items=items, total=len(items))
    def statistics(self) -> CaseStatistics: return self.repository.statistics()
