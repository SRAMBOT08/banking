from typing import Any


def serialize_json(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: serialize_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_json(item) for item in value]
    return value
