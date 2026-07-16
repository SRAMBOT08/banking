from typing import Any
from pydantic import Field
from .base_request import BaseIntegrationRequest
from .pagination import Pagination


class QueryRequest(BaseIntegrationRequest):
    filters: dict[str, Any] = Field(default_factory=dict)
    sorting: list[str] = Field(default_factory=list)
    pagination: Pagination | None = None
    version: str | None = None
