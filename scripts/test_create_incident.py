#!/usr/bin/env python3
"""Standalone smoke test for creating a ServiceNow incident.

This script composes the ServiceNow capability using the existing Hermes
architecture and prints the terminal execution details for a single incident
creation request.
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv


def _bootstrap() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")
    load_dotenv(Path.home() / ".hermes" / ".env")
    sys.path.insert(0, str(repo_root))


def main() -> int:
    _bootstrap()
    logging.basicConfig(
        level=getattr(logging, os.getenv("SERVICENOW_LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    from plugins.servicenow_pipeline.incidents import IncidentService
    from plugins.servicenow_pipeline.models import IncidentRequest
    from plugins.servicenow_pipeline.payload_builder import PayloadBuilder
    from plugins.servicenow_pipeline.pipeline import ServiceNowPipeline
    from plugins.servicenow_pipeline.servicenow_client import ServiceNowClient, ServiceNowClientConfig
    from plugins.servicenow_pipeline.table_executor import TableExecutor
    from plugins.servicenow_pipeline.verifier import ExecutionVerifier
    from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now

    config = ServiceNowClientConfig(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL", ""),
        authentication_type=os.getenv("SERVICENOW_AUTHENTICATION_TYPE", "basic"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
        access_token=os.getenv("SERVICENOW_ACCESS_TOKEN"),
        timeout=float(os.getenv("SERVICENOW_TIMEOUT", "30") or 30),
        verify_ssl=str(os.getenv("SERVICENOW_VERIFY_SSL", "true")).strip().lower() not in {"0", "false", "no", "off"},
    )

    client = ServiceNowClient(config)
    client.authenticate()
    payload_builder = PayloadBuilder()
    table_executor = TableExecutor(client)
    incident_service = IncidentService(payload_builder=payload_builder, table_executor=table_executor)
    verifier = ExecutionVerifier()
    pipeline = ServiceNowPipeline(incident_service=incident_service, verifier=verifier)

    request = IncidentRequest(
        short_description="Hermes test incident",
        description="First incident smoke test created by the Hermes ServiceNow capability.",
        priority="3",
        urgency="3",
        impact="3",
        category="hardware",
        assignment_group="Network Team",
        caller="hermes",
    )

    try:
        correlation_id = new_correlation_id()
        start = now()
        execution_result = pipeline.execute_create_incident(request, correlation_id=correlation_id)
        verification_result = pipeline.verifier.verify_creation(execution_result, correlation_id=correlation_id)
        log_stage(
            logging.getLogger(__name__),
            stage="pipeline_completion",
            correlation_id=correlation_id,
            success=verification_result.verified,
            duration_ms=elapsed_ms(start),
            message="Smoke test completed",
            extra={
                "incident_number": execution_result.incident_number,
                "sys_id": execution_result.sys_id,
                "verified": verification_result.verified,
            },
        )
        print("Success:", verification_result.verified)
        print("Correlation ID:", correlation_id)
        print("Incident Number:", execution_result.incident_number or "")
        print("sys_id:", execution_result.sys_id or "")
        print("Execution Message:", execution_result.message)
        return 0 if verification_result.verified else 1
    except Exception as exc:
        print(f"Failure: {exc}")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
