from dataclasses import dataclass


@dataclass(frozen=True)
class TimeoutConfig:
    connect: float = 5.0
    read: float = 10.0
    write: float = 10.0
    pool: float = 5.0
    overall: float | None = None
