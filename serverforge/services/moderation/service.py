"""Moderation, anti-spam, anti-link, and anti-raid service."""

from datetime import timedelta

import disnake

from serverforge.db.pool import Database
from serverforge.services.logging.service import GuildLogService


class ModerationService:
    """Execute moderation actions and protections."""

    def __init__(self, database: Database, logs: GuildLogService) -> None:
        self._database = database
        self._logs = logs

    async def ban(self, member: disnake.Member, moderator: disnake.Member, reason: str) -> None:
        """Ban a member."""
        await member.ban(reason=reason, delete_message_days=0)
        await self._logs.record(member.guild.id, "moderation_ban", {"reason": reason}, moderator.id, member.id)

    async def kick(self, member: disnake.Member, moderator: disnake.Member, reason: str) -> None:
        """Kick a member."""
        await member.kick(reason=reason)
        await self._logs.record(member.guild.id, "moderation_kick", {"reason": reason}, moderator.id, member.id)

    async def timeout(self, member: disnake.Member, moderator: disnake.Member, minutes: int, reason: str) -> None:
        """Timeout a member."""
        await member.timeout(duration=timedelta(minutes=minutes), reason=reason)
        await self._logs.record(member.guild.id, "moderation_timeout", {"minutes": minutes, "reason": reason}, moderator.id, member.id)

    async def warn(self, member: disnake.Member, moderator: disnake.Member, reason: str) -> None:
        """Warn a member."""
        await self._database.execute("INSERT INTO warnings (guild_id, user_id, moderator_id, reason) VALUES ($1, $2, $3, $4)", member.guild.id, member.id, moderator.id, reason)
        await self._logs.record(member.guild.id, "moderation_warn", {"reason": reason}, moderator.id, member.id)

    async def lockdown(self, guild: disnake.Guild, moderator: disnake.Member, reason: str) -> int:
        """Lock text channels by disabling send messages for the default role."""
        count = 0
        for channel in guild.text_channels:
            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(guild.default_role, overwrite=overwrite, reason=reason)
            count += 1
        await self._logs.record(guild.id, "moderation_lockdown", {"channels": count, "reason": reason}, moderator.id)
        return count

    def contains_link(self, content: str) -> bool:
        """Return whether message content contains a link."""
        lowered = content.lower()
        return "http://" in lowered or "https://" in lowered or "discord.gg/" in lowered
