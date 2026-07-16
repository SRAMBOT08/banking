from dataclasses import dataclass, field
from typing import Callable, Type
from .backoff import backoff_delay


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    strategy: str = "exponential"
    base_delay: float = 0.1
    max_delay: float = 5.0
    jitter: float = 0.0
    retryable_exceptions: tuple[Type[BaseException], ...] = field(default_factory=tuple)

    def should_retry(self, exc: BaseException, attempt: int) -> bool:
        return attempt < self.max_attempts and (not self.retryable_exceptions or isinstance(exc, self.retryable_exceptions))

    def delay(self, attempt: int) -> float:
        if self.strategy == "fixed":
            return min(self.max_delay, self.base_delay)
        return backoff_delay(attempt, self.base_delay, self.max_delay, self.jitter)


class FixedRetryPolicy(RetryPolicy):
    def __init__(self, **kwargs):
        super().__init__(strategy="fixed", **kwargs)


class ExponentialBackoffRetryPolicy(RetryPolicy):
    def __init__(self, **kwargs):
        super().__init__(strategy="exponential", **kwargs)
