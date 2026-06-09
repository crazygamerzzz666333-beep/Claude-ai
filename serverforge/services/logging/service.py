"""Persistent guild activity logging service."""

from typing import Any

from serverforge.db.pool import Database


class GuildLogService:
    """Store message, role, channel, member, voice, and moderation logs."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def record(self, guild_id: int, log_type: str, payload: dict[str, Any], actor_id: int | None = None, target_id: int | None = None) -> None:
        """Persist a log entry."""
        await self._database.execute(
            "INSERT INTO logs (guild_id, actor_id, target_id, log_type, payload) VALUES ($1, $2, $3, $4, $5::jsonb)",
            guild_id,
            actor_id,
            target_id,
            log_type,
            payload,
        )
