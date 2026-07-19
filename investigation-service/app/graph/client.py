"""Neo4j graph client and connection management."""
from __future__ import annotations

from __future__ import annotations
from typing import Optional

import asyncio
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config.settings import settings


class GraphManager:
    """Manages Neo4j driver lifecycle."""

    def __init__(self):
        self._driver: Optional[AsyncDriver] = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the Neo4j driver."""
        async with self._lock:
            if self._driver is not None:
                return

            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_pool_size=50,
                connection_acquisition_timeout=30,
            )
            # Verify connectivity
            await self._driver.verify_connectivity()

    async def close(self) -> None:
        """Close the Neo4j driver."""
        async with self._lock:
            if self._driver:
                await self._driver.close()
                self._driver = None

    def get_driver(self) -> Optional[AsyncDriver]:
        """Get the Neo4j driver instance."""
        return self._driver

    @property
    def is_connected(self) -> bool:
        """Check if driver is connected."""
        return self._driver is not None


# Global instance
graph_manager = GraphManager()