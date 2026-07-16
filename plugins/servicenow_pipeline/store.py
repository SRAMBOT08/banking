"""Durable state scaffold for the ServiceNow pipeline."""

from __future__ import annotations

import os
from typing import Any, Optional
from pathlib import Path

from hermes_constants import get_hermes_home


DEFAULT_SERVICENOW_PIPELINE_STORE_FILENAME = "servicenow_pipeline_store.json"


def resolve_teams_pipeline_store_path(path: str | Path | None = None) -> Path:
    """Resolve the ServiceNow pipeline store path.

    The helper keeps the runtime import-compatible with the Teams integration
    pattern while using a ServiceNow-specific on-disk location.
    """

    if path is not None:
        explicit = str(path).strip()
        if explicit:
            return Path(explicit)

    env_path = os.getenv("SERVICENOW_PIPELINE_STORE_PATH", "").strip()
    if env_path:
        return Path(env_path)

    return get_hermes_home() / DEFAULT_SERVICENOW_PIPELINE_STORE_FILENAME


class ServiceNowPipelineStore:
    """Placeholder persistence layer for future ServiceNow pipeline state."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        """Load pipeline state."""
        raise NotImplementedError("ServiceNow store loading is not implemented yet.")

    def save(self, state: dict[str, Any]) -> None:
        """Save pipeline state."""
        raise NotImplementedError("ServiceNow store saving is not implemented yet.")

    def get_job(self, job_id: str) -> Optional[dict[str, Any]]:
        """Fetch a stored job."""
        raise NotImplementedError("ServiceNow job lookup is not implemented yet.")

    def upsert_job(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Persist a job record."""
        raise NotImplementedError("ServiceNow job persistence is not implemented yet.")
