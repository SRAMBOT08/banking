from typing import Any
from ..exceptions import IntegrationValidationError


def validate_request(value: Any, model=None) -> Any:
    if model is None:
        return value
    try:
        return model.model_validate(value) if hasattr(model, "model_validate") else model(value)
    except Exception as exc:
        raise IntegrationValidationError("integration request validation failed", cause=exc) from exc
