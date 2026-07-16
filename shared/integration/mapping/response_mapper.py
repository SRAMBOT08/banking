from typing import Any, Type, TypeVar
from .mapper import Mapper
from ..transport.deserialization import deserialize_model

T = TypeVar("T")


class ResponseMapper(Mapper[T]):
    def __init__(self, model: Type[T] | None = None, function=None):
        self.model = model
        self.function = function

    def map(self, value: Any) -> T:
        if self.function:
            return self.function(value)
        return deserialize_model(value, self.model) if self.model else value
