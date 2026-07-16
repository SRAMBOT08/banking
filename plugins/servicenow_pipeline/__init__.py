"""ServiceNow pipeline plugin integration.

This package exposes the CLI-facing plugin registration and keeps the runtime
composition entrypoints available for Hermes to wire at startup.
"""

from __future__ import annotations

from plugins.servicenow_pipeline.cli import register_cli


def register(ctx) -> None:
    """Register the ServiceNow pipeline capability surface.

    TODO: wire the real ServiceNow capability once execution logic exists.
    """
    ctx.register_cli_command(
        name="servicenow-pipeline",
        help="ServiceNow pipeline scaffold",
        setup_fn=register_cli,
        handler_fn=lambda args: 0,
        description="Placeholder CLI surface for the future ServiceNow pipeline.",
    )
