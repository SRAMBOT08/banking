"""Runtime wiring for the ServiceNow capability.

This module mirrors the Teams runtime pattern at the composition boundary:
it builds a ready-to-use pipeline instance from injected dependencies and
keeps all business logic outside the runtime layer.
"""

from __future__ import annotations

import logging
from typing import Any

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

logger = logging.getLogger(__name__)


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


def build_pipeline_runtime(gateway: Any) -> ServiceNowPipeline:
    """Create a fully wired ServiceNow pipeline runtime.

    The runtime composes the dependency chain only. It does not execute any
    ServiceNow workflow and does not expose REST or business logic.
    """
    correlation_id = new_correlation_id()
    start = now()
    gateway_config = getattr(gateway, "config", None)
    try:
        runtime_config = build_pipeline_runtime_config(gateway_config)
        client_config = _build_client_config(runtime_config)
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
        log_stage(
            logger,
            stage="runtime_initialization",
            correlation_id=correlation_id,
            success=True,
            duration_ms=elapsed_ms(start),
            extra={"component": "servicenow_pipeline"},
        )
        return pipeline
    except Exception as exc:
        log_stage(
            logger,
            stage="runtime_initialization",
            correlation_id=correlation_id,
            success=False,
            duration_ms=elapsed_ms(start),
            error=exc,
            extra={"component": "servicenow_pipeline"},
        )
        raise


def bind_gateway_runtime(gateway: Any) -> bool:
    """Bind the ServiceNow runtime into a gateway-owned integration slot.

    This mirrors the Teams runtime composition pattern but remains inert if the
    gateway does not expose a compatible ServiceNow integration surface.
    """
    if getattr(gateway, "_servicenow_pipeline_runtime", None) is not None:
        return True

    try:
        runtime = build_pipeline_runtime(gateway)
    except Exception as exc:
        gateway._servicenow_pipeline_runtime_error = str(exc)
        logger.warning("ServiceNow pipeline runtime unavailable: %s", exc)
        return False

    gateway._servicenow_pipeline_runtime = runtime
    gateway._servicenow_pipeline_runtime_error = None
    logger.info("ServiceNow pipeline runtime bound")
    return True
