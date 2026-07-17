"""Runtime wiring for the ServiceNow capability.

This module provides a long-lived ServiceNow runtime that is created once at
startup (either during gateway initialization or CLI startup) and reused for
all tool invocations. This follows Hermes' native lifecycle where expensive
resources are initialized once and shared across the process lifetime.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from plugins.servicenow_pipeline.incidents import IncidentService
from plugins.servicenow_pipeline.payload_builder import PayloadBuilder
from plugins.servicenow_pipeline.pipeline import ServiceNowPipeline
from plugins.servicenow_pipeline.servicenow_client import (
    ServiceNowClient,
    ServiceNowClientConfig,
)
from plugins.servicenow_pipeline.store import ServiceNowPipelineStore, resolve_teams_pipeline_store_path
from plugins.servicenow_pipeline.table_executor import TableExecutor
from plugins.servicenow_pipeline.verifier import ExecutionVerifier
from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now
from plugins.servicenow_pipeline.models import IncidentRequest, VerificationResult

logger = logging.getLogger(__name__)

# Module-level singleton for the ServiceNow runtime.
# Initialized once at startup via bind_gateway_runtime() or bind_cli_runtime().
_runtime: Optional[ServiceNowPipeline] = None
_runtime_error: Optional[str] = None
_runtime_config: dict[str, Any] = {}


def _read_section(config: Any, *keys: str) -> dict[str, Any]:
    current = config
    for key in keys:
        if not isinstance(current, dict):
            return {}
        current = current.get(key)
    return dict(current or {}) if isinstance(current, dict) else {}


def build_pipeline_runtime_config(gateway_config: Any) -> dict[str, Any]:
    """Build ServiceNow runtime configuration from Hermes config state.

    The runtime only reads configuration; it does not validate credentials or
    contact ServiceNow.
    """
    if isinstance(gateway_config, dict):
        config = gateway_config
    else:
        config = {}
        if gateway_config is not None:
            for key in ("servicenow_pipeline", "servicenow", "integrations"):
                value = getattr(gateway_config, key, None)
                if value is not None:
                    config[key] = value
            platforms = getattr(gateway_config, "platforms", None)
            if platforms is not None:
                config["platforms"] = platforms

    return dict(
        _read_section(config, "servicenow_pipeline")
        or _read_section(config, "servicenow")
        or _read_section(config, "integrations", "servicenow")
    )


def _build_client_config(runtime_config: dict[str, Any]) -> ServiceNowClientConfig:
    client_cfg = runtime_config.get("client")
    if isinstance(client_cfg, ServiceNowClientConfig):
        return client_cfg
    if isinstance(client_cfg, dict):
        return ServiceNowClientConfig(**client_cfg)
    return ServiceNowClientConfig(
        instance_url=str(runtime_config.get("instance_url") or "").strip(),
        authentication_type=str(runtime_config.get("authentication_type") or "none").strip().lower(),
        username=runtime_config.get("username"),
        password=runtime_config.get("password"),
        access_token=runtime_config.get("access_token"),
        timeout=float(runtime_config.get("timeout", 30.0) or 30.0),
        verify_ssl=bool(runtime_config.get("verify_ssl", True)),
        retry_policy=runtime_config.get("retry_policy") or {},
    )


def _create_pipeline() -> ServiceNowPipeline:
    """Create a fully wired ServiceNow pipeline with all dependencies."""
    client_config = _build_client_config(_runtime_config)
    client = ServiceNowClient(client_config)
    table_executor = TableExecutor(client)
    payload_builder = PayloadBuilder()
    incident_service = IncidentService(
        payload_builder=payload_builder,
        table_executor=table_executor,
    )
    verifier = ExecutionVerifier()

    pipeline = ServiceNowPipeline(
        incident_service=incident_service,
        verifier=verifier,
    )
    return pipeline


def _bind_runtime_internal(config: Any) -> bool:
    """Internal method to bind the runtime. Used by both gateway and CLI binders."""
    global _runtime, _runtime_error, _runtime_config

    if _runtime is not None:
        return True

    try:
        _runtime_config = build_pipeline_runtime_config(config)
        correlation_id = new_correlation_id()
        start = now()
        runtime = _create_pipeline()
        log_stage(
            logger,
            stage="runtime_initialization",
            correlation_id=correlation_id,
            success=True,
            duration_ms=elapsed_ms(start),
            extra={"component": "servicenow_pipeline"},
        )
        _runtime = runtime
        _runtime_error = None
        logger.info("ServiceNow pipeline runtime initialized")
        return True
    except Exception as exc:
        _runtime_error = str(exc)
        logger.warning("ServiceNow pipeline runtime unavailable: %s", exc)
        log_stage(
            logger,
            stage="runtime_initialization",
            correlation_id=new_correlation_id(),
            success=False,
            duration_ms=elapsed_ms(now()),
            error=exc,
            extra={"component": "servicenow_pipeline"},
        )
        return False


def bind_gateway_runtime(gateway: Any) -> bool:
    """Bind the ServiceNow runtime into a gateway-owned integration slot.

    This mirrors the Teams runtime composition pattern but remains inert if the
    gateway does not expose a compatible ServiceNow integration surface.
    """
    gateway_config = getattr(gateway, "config", None)
    bound = _bind_runtime_internal(gateway_config)
    if bound:
        gateway._servicenow_pipeline_runtime = _runtime
        gateway._servicenow_pipeline_runtime_error = None
        logger.info("ServiceNow pipeline runtime bound to gateway")
    else:
        gateway._servicenow_pipeline_runtime_error = _runtime_error
    return bound


def bind_cli_runtime(config: Any) -> bool:
    """Bind the ServiceNow runtime for CLI mode.

    Called during CLI startup after plugins are discovered.
    """
    bound = _bind_runtime_internal(config)
    if bound:
        logger.info("ServiceNow pipeline runtime bound to CLI")
    return bound


def get_runtime() -> ServiceNowPipeline:
    """Get the initialized ServiceNow runtime.

    Returns:
        The singleton ServiceNowPipeline instance.

    Raises:
        RuntimeError: If the runtime has not been initialized.
    """
    if _runtime is None:
        raise RuntimeError(
            "ServiceNow runtime not initialized. Call bind_gateway_runtime() "
            "or bind_cli_runtime() first."
        )
    return _runtime


def get_runtime_error() -> Optional[str]:
    """Get the last runtime initialization error, if any."""
    return _runtime_error


def is_runtime_ready() -> bool:
    """Check if the runtime is initialized and ready."""
    return _runtime is not None


def create_incident(request: IncidentRequest) -> VerificationResult:
    """Create a ServiceNow incident using the singleton runtime.

    This is the primary entry point for tool handlers. It delegates to the
    runtime's execute() method which orchestrates the full pipeline including
    verification.

    Args:
        request: The incident request to create.

    Returns:
        VerificationResult with verified status, message, and incident identifiers.
    """
    runtime = get_runtime()
    return runtime.execute(request)