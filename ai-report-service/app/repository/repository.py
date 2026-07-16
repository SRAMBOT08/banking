from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
from threading import RLock
from typing import Any
from uuid import UUID
from ..models import ReportFile


class ReportRepository(ABC):
    @abstractmethod
    def create(self, report: ReportFile) -> ReportFile: ...
    @abstractmethod
    def get(self, report_id: UUID) -> ReportFile: ...
    @abstractmethod
    def history(self, case_id: UUID, report_type: str | None = None) -> list[ReportFile]: ...
    @abstractmethod
    def search(self, filters: dict[str, Any]) -> list[ReportFile]: ...
    @abstractmethod
    def statistics(self) -> dict[str, int]: ...


class InMemoryReportRepository(ReportRepository):
    def __init__(self): self._items: dict[UUID, ReportFile] = {}; self._lock = RLock()
    def create(self, report: ReportFile) -> ReportFile:
        with self._lock:
            if report.report_id in self._items: raise ValueError('reports are immutable and cannot be overwritten')
            self._items[report.report_id] = deepcopy(report); return deepcopy(report)
    def get(self, report_id: UUID) -> ReportFile:
        with self._lock:
            if report_id not in self._items: raise KeyError(str(report_id))
            return deepcopy(self._items[report_id])
    def history(self, case_id: UUID, report_type: str | None = None) -> list[ReportFile]:
        with self._lock: values = list(self._items.values())
        return [deepcopy(x) for x in values if x.case_id == case_id and (report_type is None or x.report_type.value == report_type)]
    def search(self, filters: dict[str, Any]) -> list[ReportFile]:
        with self._lock: values = list(self._items.values())
        return [deepcopy(x) for x in values if (not filters.get('case_id') or str(x.case_id) == str(filters['case_id'])) and (not filters.get('report_type') or x.report_type.value == filters['report_type'])]
    def statistics(self) -> dict[str, int]:
        with self._lock: values = list(self._items.values())
        return {'report_count': len(values), 'case_count': len({x.case_id for x in values}), 'type_count': len({x.report_type for x in values})}
