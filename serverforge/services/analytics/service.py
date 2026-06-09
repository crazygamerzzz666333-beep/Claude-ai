"""Server analytics collection and reporting."""

from typing import Any

from serverforge.db.pool import Database


class AnalyticsService:
    """Track server growth, member activity, channel activity, and role statistics."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def track(self, guild_id: int, event_type: str, metadata: dict[str, Any], actor_id: int | None = None, channel_id: int | None = None, role_id: int | None = None) -> None:
        """Record an analytics event."""
        await self._database.execute(
            "INSERT INTO analytics_events (guild_id, actor_id, event_type, channel_id, role_id, metadata) VALUES ($1, $2, $3, $4, $5, $6::jsonb)",
            guild_id,
            actor_id,
            event_type,
            channel_id,
            role_id,
            metadata,
        )

    async def summary(self, guild_id: int) -> dict[str, int]:
        """Return aggregate counts for a guild."""
        rows = await self._database.fetch(
            "SELECT event_type, COUNT(*) AS count FROM analytics_events WHERE guild_id = $1 GROUP BY event_type",
            guild_id,
        )
        return {str(row["event_type"]): int(row["count"]) for row in rows}
