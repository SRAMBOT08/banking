from typing import Any
from pydantic import Field
from .base_response import BaseIntegrationResponse
from .pagination import Pagination


class QueryResponse(BaseIntegrationResponse):
    items: list[Any] = Field(default_factory=list)
    pagination: Pagination | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
