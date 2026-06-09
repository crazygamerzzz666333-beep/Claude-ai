"""Backup, restore, undo, redo, history, and comparison service."""

from typing import Any
from uuid import UUID

import disnake

from serverforge.db.pool import Database
from serverforge.services.models import BackupSnapshot


class BackupService:
    """Manage guild snapshots and recovery workflows."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def snapshot_guild(self, guild: disnake.Guild, actor_id: int | None, reason: str) -> UUID:
        """Create and store a guild backup snapshot."""
        snapshot = BackupSnapshot(
            guild_id=guild.id,
            name=guild.name,
            channels=[self._channel_payload(channel) for channel in guild.channels],
            roles=[self._role_payload(role) for role in guild.roles if not role.is_default()],
            emojis=[{"id": emoji.id, "name": emoji.name, "url": str(emoji.url)} for emoji in guild.emojis],
            settings={"verification_level": str(guild.verification_level), "default_notifications": str(guild.default_notifications)},
        )
        row = await self._database.fetchrow(
            "INSERT INTO backups (guild_id, actor_id, reason, snapshot) VALUES ($1, $2, $3, $4::jsonb) RETURNING id",
            guild.id,
            actor_id,
            reason,
            snapshot.model_dump(mode="json"),
        )
        backup_id = UUID(str(row["id"]))
        await self._history(guild.id, backup_id, "create", actor_id, {"reason": reason})
        return backup_id

    async def restore_partial(self, guild: disnake.Guild, backup_id: UUID, sections: list[str], actor_id: int) -> dict[str, Any]:
        """Record a partial restore request and return selected snapshot data."""
        row = await self._database.fetchrow("SELECT snapshot FROM backups WHERE id = $1 AND guild_id = $2", backup_id, guild.id)
        if row is None:
            raise LookupError("backup not found")
        snapshot = dict(row["snapshot"])
        selected = {section: snapshot.get(section) for section in sections}
        await self._history(guild.id, backup_id, "restore", actor_id, {"sections": sections})
        return selected

    async def compare(self, guild: disnake.Guild, backup_id: UUID, actor_id: int) -> dict[str, int]:
        """Compare current guild counts with a backup."""
        row = await self._database.fetchrow("SELECT snapshot FROM backups WHERE id = $1 AND guild_id = $2", backup_id, guild.id)
        if row is None:
            raise LookupError("backup not found")
        snapshot = dict(row["snapshot"])
        result = {"channel_delta": len(guild.channels) - len(snapshot.get("channels", [])), "role_delta": len(guild.roles) - len(snapshot.get("roles", [])), "emoji_delta": len(guild.emojis) - len(snapshot.get("emojis", []))}
        await self._history(guild.id, backup_id, "compare", actor_id, result)
        return result

    async def latest(self, guild_id: int) -> UUID | None:
        """Return the latest backup ID for a guild."""
        row = await self._database.fetchrow("SELECT id FROM backups WHERE guild_id = $1 ORDER BY created_at DESC LIMIT 1", guild_id)
        return UUID(str(row["id"])) if row else None

    async def _history(self, guild_id: int, backup_id: UUID, action: str, actor_id: int | None, details: dict[str, Any]) -> None:
        await self._database.execute("INSERT INTO backup_history (guild_id, backup_id, action, actor_id, details) VALUES ($1, $2, $3, $4, $5::jsonb)", guild_id, backup_id, action, actor_id, details)

    def _channel_payload(self, channel: disnake.abc.GuildChannel) -> dict[str, Any]:
        return {"id": channel.id, "name": channel.name, "type": str(channel.type), "position": channel.position, "category_id": getattr(channel, "category_id", None)}

    def _role_payload(self, role: disnake.Role) -> dict[str, Any]:
        return {"id": role.id, "name": role.name, "permissions": role.permissions.value, "color": role.color.value, "position": role.position, "hoist": role.hoist, "mentionable": role.mentionable}
