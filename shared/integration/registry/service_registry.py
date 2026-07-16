from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceDefinition:
    name: str
    base_url: str
    version: str = "v1"


class ServiceRegistry:
    DEFAULTS = ("evidence", "threat", "knowledge", "graph", "memory", "ai", "execution")

    def __init__(self, services: dict[str, ServiceDefinition] | None = None):
        self._services = dict(services or {})
        for name in self.DEFAULTS:
            self._services.setdefault(name, ServiceDefinition(name=name, base_url=""))

    def register(self, definition: ServiceDefinition) -> None:
        self._services[definition.name] = definition

    def get(self, name: str) -> ServiceDefinition:
        return self._services[name]

    def discover(self, name: str) -> str:
        return self.get(name).base_url

    def names(self) -> tuple[str, ...]:
        return tuple(self._services)
