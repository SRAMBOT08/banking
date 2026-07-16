from __future__ import annotations
from typing import Any
from .base_tool_client import BaseToolClient


class BaseQueryClient(BaseToolClient):
    def get(self, path: str, *, params: dict[str, Any] | None = None, response_mapper=None, cancel_event=None, **kwargs):
        return self.request("GET", path, response_mapper=response_mapper, cancel_event=cancel_event, params=params, **kwargs)

    def post(self, path: str, *, request: Any = None, response_mapper=None, cancel_event=None, **kwargs):
        return self.request("POST", path, request=request, response_mapper=response_mapper, cancel_event=cancel_event, **kwargs)

    def search(self, path: str, request: Any = None, *, response_mapper=None, cancel_event=None, **kwargs):
        return self.post(path, request=request, response_mapper=response_mapper, cancel_event=cancel_event, **kwargs)
