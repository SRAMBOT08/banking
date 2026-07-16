from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


QueryRequestT = TypeVar("QueryRequestT", bound=BaseModel)
QueryResultT = TypeVar("QueryResultT", bound=BaseModel)


class Pagination(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class BaseQueryModels:
    """Namespace for shared query model conventions."""


class BaseQueryRepository(ABC, Generic[QueryRequestT, QueryResultT]):
    """Read-only repository marker shared by CQRS query services."""

    @abstractmethod
    def search(self, request: QueryRequestT) -> QueryResultT:
        raise NotImplementedError()


class BaseQueryService(Generic[QueryRequestT, QueryResultT]):
    def __init__(self, repository: BaseQueryRepository[QueryRequestT, QueryResultT]):
        self.repository = repository

    def search(self, request: QueryRequestT) -> QueryResultT:
        return self.repository.search(request)


class BaseQueryRouter:
    """Small dependency-injection helper for read-only service routers."""

    def __init__(self, service: BaseQueryService):
        self.service = service
