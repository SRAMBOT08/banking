class VersionRegistry:
    def __init__(self, default: str = "v1"):
        self.default = default
        self._versions: dict[str, str] = {}

    def register(self, service: str, version: str) -> None:
        self._versions[service] = version

    def select(self, service: str, requested: str | None = None) -> str:
        return requested or self._versions.get(service, self.default)
