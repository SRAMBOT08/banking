from typing import Any, Mapping, Protocol


class IntegrationClient(Protocol):
    def request(self, method: str, path: str, **kwargs) -> Mapping[str, Any]:
        ...


class ToolClient(Protocol):
    def execute(self, operation: Any, request: dict[str, Any], cancel_event: Any = None) -> Mapping[str, Any]:
        ...
