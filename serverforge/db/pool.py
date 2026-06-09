"""Async PostgreSQL connection pool."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg


class Database:
    """Thin wrapper around an asyncpg pool."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Open the database pool."""
        self.pool = await asyncpg.create_pool(dsn=self._dsn, min_size=1, max_size=10)

    async def close(self) -> None:
        """Close the database pool."""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        """Acquire a database connection."""
        if self.pool is None:
            raise RuntimeError("database pool is not connected")
        async with self.pool.acquire() as connection:
            yield connection

    async def execute(self, sql: str, *args: object) -> str:
        """Execute a statement."""
        async with self.acquire() as connection:
            return await connection.execute(sql, *args)

    async def fetch(self, sql: str, *args: object) -> list[asyncpg.Record]:
        """Fetch rows."""
        async with self.acquire() as connection:
            return list(await connection.fetch(sql, *args))

    async def fetchrow(self, sql: str, *args: object) -> asyncpg.Record | None:
        """Fetch a single row."""
        async with self.acquire() as connection:
            return await connection.fetchrow(sql, *args)
