import random


def backoff_delay(attempt: int, base: float = 0.1, maximum: float = 5.0, jitter: float = 0.0) -> float:
    delay = min(maximum, base * (2 ** max(0, attempt - 1)))
    return max(0.0, delay + (random.uniform(0, jitter) if jitter else 0.0))
