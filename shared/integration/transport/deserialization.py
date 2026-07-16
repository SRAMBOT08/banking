from typing import Any, Type, TypeVar

T = TypeVar("T")


def deserialize_model(value: Any, model: Type[T]) -> T:
    if hasattr(model, "model_validate"):
        return model.model_validate(value)
    return model(value)
