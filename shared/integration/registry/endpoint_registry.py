from dataclasses import dataclass


@dataclass(frozen=True)
class EndpointDefinition:
    service: str
    name: str
    method: str
    path: str
    version: str = "v1"


class EndpointRegistry:
    def __init__(self, endpoints: list[EndpointDefinition] | None = None):
        self._endpoints = {(item.service, item.name, item.version): item for item in endpoints or []}

    def register(self, endpoint: EndpointDefinition) -> None:
        self._endpoints[(endpoint.service, endpoint.name, endpoint.version)] = endpoint

    def get(self, service: str, name: str, version: str = "v1") -> EndpointDefinition:
        return self._endpoints[(service, name, version)]
