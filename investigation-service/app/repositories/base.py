from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.investigation import Investigation


class InvestigationRepository(ABC):
    """Repository interface for Investigation aggregate.

    All implementations must provide these methods.
    """

    @abstractmethod
    def save(self, investigation: Investigation) -> Investigation:
        """Persist an investigation. Returns the saved instance."""
        ...

    @abstractmethod
    def get(self, investigation_id: str) -> Optional[Investigation]:
        """Retrieve a single investigation by ID."""
        ...

    @abstractmethod
    def list_all(self) -> List[Investigation]:
        """List all investigations (used for admin/debug)."""
        ...

    @abstractmethod
    def find_by_correlation(self, correlation_id: str) -> List[Investigation]:
        """Find investigations by correlation ID."""
        ...

    @abstractmethod
    def find_by_tenant(self, tenant_id: str, limit: int = 100, offset: int = 0) -> List[Investigation]:
        """Find investigations by tenant ID with pagination."""
        ...

    @abstractmethod
    def delete(self, investigation_id: str) -> bool:
        """Delete an investigation. Returns True if deleted."""
        ...