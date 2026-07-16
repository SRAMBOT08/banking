"""Shared observability helpers for the ServiceNow pipeline."""

from __future__ import annotations

import json
import logging
import time
import traceback
import uuid
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping


def new_correlation_id() -> str:
    """Return a stable request/correlation identifier."""
    return uuid.uuid4().hex


def now() -> float:
    """Return a monotonic timestamp for duration measurement."""
    return time.perf_counter()


def elapsed_ms(start: float) -> float:
    """Convert a perf-counter start time into elapsed milliseconds."""
    return (time.perf_counter() - start) * 1000.0


def _mask_value(key: str, value: Any) -> Any:
    sensitive_keys = {"password", "pass", "token", "access_token", "authorization", "secret", "api_key"}
    if any(s in str(key).lower() for s in sensitive_keys):
        return "***"
    return value


def sanitize_mapping(data: Mapping[str, Any] | None) -> dict[str, Any]:
    """Recursively mask common secrets from a mapping."""
    if not isinstance(data, Mapping):
        return {}
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, Mapping):
            result[str(key)] = sanitize_mapping(value)
        elif isinstance(value, list):
            result[str(key)] = [
                sanitize_mapping(item) if isinstance(item, Mapping) else _mask_value(str(key), item)
                for item in value
            ]
        else:
            result[str(key)] = _mask_value(str(key), value)
    return result


def sanitize_payload(payload: Any) -> Any:
    """Sanitize dataclass or mapping payloads for logging."""
    if payload is None:
        return None
    if is_dataclass(payload):
        return sanitize_mapping(asdict(payload))
    if isinstance(payload, Mapping):
        return sanitize_mapping(payload)
    return payload


def sanitize_response(response: Any) -> Any:
    """Sanitize response payloads for logging."""
    if isinstance(response, Mapping):
        return sanitize_mapping(response)
    if isinstance(response, list):
        return [sanitize_response(item) for item in response]
    return response


def log_stage(
    logger: logging.Logger,
    *,
    stage: str,
    correlation_id: str,
    success: bool,
    duration_ms: float,
    message: str = "",
    error: Exception | None = None,
    extra: Mapping[str, Any] | None = None,
    level: int | None = None,
) -> None:
    """Emit a structured stage log with safe metadata only."""
    payload: dict[str, Any] = {
        "stage": stage,
        "correlation_id": correlation_id,
        "success": success,
        "duration_ms": round(duration_ms, 2),
    }
    if message:
        payload["message"] = message
    if extra:
        payload.update(dict(extra))
    if error is not None:
        payload["error_type"] = type(error).__name__
        payload["error_message"] = str(error)
        payload["stack_trace"] = traceback.format_exc()

    log_level = level if level is not None else (logging.INFO if success else logging.ERROR)
    logger.log(log_level, "ServiceNow trace: %s", json.dumps(payload, default=str, sort_keys=True))

