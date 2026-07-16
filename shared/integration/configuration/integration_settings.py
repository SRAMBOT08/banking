from dataclasses import dataclass, field


@dataclass(frozen=True)
class IntegrationSettings:
    timeout_seconds: float = 10.0
    retry_max_attempts: int = 3
    retry_base_delay: float = 0.1
    retry_max_delay: float = 5.0
    service_urls: dict[str, str] = field(default_factory=dict)
    api_version: str = "v1"
