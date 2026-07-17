"""ServiceNow pipeline plugin integration.

This package exposes the CLI-facing plugin registration and keeps the runtime
composition entrypoints available for Hermes to wire at startup.
"""

from __future__ import annotations

from plugins.servicenow_pipeline.cli import register_cli
from plugins.servicenow_pipeline.tools import (
    SERVICENOW_CREATE_INCIDENT_SCHEMA,
    check_servicenow_requirements,
    handle_servicenow_create_incident,
)


def register(ctx) -> None:
    """Register the ServiceNow pipeline capability surface."""
    ctx.register_tool(
        name="servicenow_create_incident",
        toolset="servicenow",
        schema=SERVICENOW_CREATE_INCIDENT_SCHEMA,
        handler=handle_servicenow_create_incident,
        check_fn=check_servicenow_requirements,
        emoji="🎫",
    )

    ctx.register_cli_command(
        name="servicenow-pipeline",
        help="ServiceNow pipeline scaffold",
        setup_fn=register_cli,
        handler_fn=lambda args: 0,
        description="Placeholder CLI surface for the future ServiceNow pipeline.",
    )

