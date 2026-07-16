from enum import Enum
from threading import Lock
from time import monotonic


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self._opened_at = 0.0
        self._lock = Lock()

    def allow_request(self) -> bool:
        with self._lock:
            if self.state is CircuitState.OPEN and monotonic() - self._opened_at >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            return self.state is not CircuitState.OPEN

    def record_success(self) -> None:
        with self._lock:
            self.failures = 0
            self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        with self._lock:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self._opened_at = monotonic()

    def before_call(self) -> None:
        if not self.allow_request():
            raise CircuitOpenError("integration circuit is open")
