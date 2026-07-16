from __future__ import annotations
from uuid import UUID
from ..repository import ReportRepository


class ReportQueryService:
    def __init__(self, repository: ReportRepository): self.repository = repository
    def get(self, report_id: UUID): return self.repository.get(report_id)
    def history(self, case_id: UUID, report_type: str | None = None): return self.repository.history(case_id, report_type)
    def search(self, filters: dict): return self.repository.search(filters)
    def statistics(self): return self.repository.statistics()
