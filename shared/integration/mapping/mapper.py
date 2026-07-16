from typing import Any, Generic, TypeVar
from ..exceptions import MappingException

T = TypeVar("T")


class Mapper(Generic[T]):
    def map(self, value: Any) -> T:
        raise NotImplementedError


class CallableMapper(Mapper[T]):
    def __init__(self, function):
        self.function = function

    def map(self, value: Any) -> T:
        try:
            return self.function(value)
        except Exception as exc:
            raise MappingException("integration response mapping failed", cause=exc) from exc
