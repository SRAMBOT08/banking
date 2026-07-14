from __future__ import annotations
from typing import Any
import httpx
from app.config.settings import Settings
from app.models.snapshot_contract import SnapshotDocument


class InvestigationSnapshotClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.client = client

    async def get(self, investigation_id: str, version: int) -> SnapshotDocument:
        url = f"{self.settings.investigation_service_url}/investigations/{investigation_id}/snapshots/{version}"
        owns_client = self.client is None
        client = self.client or httpx.AsyncClient(timeout=self.settings.timeout_seconds)
        try:
            response = await client.get(url)
            response.raise_for_status()
            return SnapshotDocument.model_validate(response.json())
        finally:
            if owns_client:
                await client.aclose()
