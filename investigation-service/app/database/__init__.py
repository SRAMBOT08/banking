"""Database connection manager."""
from __future__ import annotations

import asyncpg
from app.config.settings import settings

class DatabaseManager:
    """Manages PostgreSQL connection pool."""
    
    def __init__(self):
        self._pool: asyncpg.Pool | None = None
    
    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")
        return self._pool
    
    async def initialize(self) -> None:
        """Initialize the connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=1,
                max_size=settings.database_pool_size,
                timeout=settings.database_pool_timeout,
                command_timeout=60,
            )
    
    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


db_manager = DatabaseManager()