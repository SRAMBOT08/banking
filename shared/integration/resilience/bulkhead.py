from contextlib import contextmanager
from threading import BoundedSemaphore


class Bulkhead:
    def __init__(self, max_concurrency: int = 100):
        self._semaphore = BoundedSemaphore(max_concurrency)

    @contextmanager
    def acquire(self):
        acquired = self._semaphore.acquire(blocking=False)
        if not acquired:
            raise RuntimeError("integration bulkhead is full")
        try:
            yield
        finally:
            self._semaphore.release()
