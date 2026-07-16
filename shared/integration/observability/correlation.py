from contextvars import ContextVar
from uuid import uuid4

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    value = _correlation_id.get()
    return value or str(uuid4())


def set_correlation_id(value: str) -> None:
    _correlation_id.set(value)
