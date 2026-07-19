from __future__ import annotations

from app.repositories.investigation_repository import InMemoryInvestigationRepository
from app.repositories.base import InvestigationRepository
from app.repositories.postgres_repository import PostgresInvestigationRepository

__all__ = [
    "InMemoryInvestigationRepository",
    "InvestigationRepository",
    "PostgresInvestigationRepository",
]