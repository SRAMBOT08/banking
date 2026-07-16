from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID
from .models import AuditEntry, CaseFile, CaseStatistics


class CaseStorage(ABC):
    """Storage port; persistence details never leak into builders or queries."""
    @abstractmethod
    def put_case(self, case: CaseFile) -> CaseFile: ...
    @abstractmethod
    def get_case(self, case_id: UUID, version: int | None = None) -> CaseFile: ...
    @abstractmethod
    def list_versions(self, case_id: UUID) -> tuple[CaseFile, ...]: ...
    @abstractmethod
    def list_audit(self, case_id: UUID) -> tuple[AuditEntry, ...]: ...
    @abstractmethod
    def search_cases(self, filters: dict[str, Any]) -> list[CaseFile]: ...
    @abstractmethod
    def get_statistics(self) -> CaseStatistics: ...
