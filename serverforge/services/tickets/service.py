"""Ticket creation, claiming, logging, closing, reopening, and transcript export."""

from uuid import UUID

import disnake

from serverforge.db.pool import Database


class TicketService:
    """Manage support ticket lifecycle."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def create(self, guild: disnake.Guild, opener: disnake.Member, subject: str) -> disnake.TextChannel:
        """Create a ticket channel."""
        category = disnake.utils.get(guild.categories, name="support") or await guild.create_category("support")
        channel = await guild.create_text_channel(f"ticket-{opener.name}"[:90], category=category, topic=subject, reason="ServerForge ticket opened")
        await channel.set_permissions(opener, read_messages=True, send_messages=True)
        await self._database.execute("INSERT INTO tickets (guild_id, channel_id, opener_id, status, subject) VALUES ($1, $2, $3, 'open', $4)", guild.id, channel.id, opener.id, subject)
        return channel

    async def claim(self, channel: disnake.TextChannel, staff: disnake.Member) -> None:
        """Claim a ticket."""
        await self._database.execute("UPDATE tickets SET claimed_by = $1, updated_at = now() WHERE channel_id = $2", staff.id, channel.id)

    async def close(self, channel: disnake.TextChannel, transcript: str) -> None:
        """Close a ticket and store transcript text."""
        await self._database.execute("UPDATE tickets SET status = 'closed', transcript = $1, updated_at = now() WHERE channel_id = $2", transcript, channel.id)
        if channel.guild is not None:
            overwrite = channel.overwrites_for(channel.guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(channel.guild.default_role, overwrite=overwrite, reason="ServerForge ticket closed")

    async def reopen(self, channel: disnake.TextChannel) -> None:
        """Reopen a closed ticket."""
        await self._database.execute("UPDATE tickets SET status = 'open', updated_at = now() WHERE channel_id = $1", channel.id)

    async def export_transcript(self, ticket_id: UUID) -> str:
        """Return a stored transcript."""
        row = await self._database.fetchrow("SELECT transcript FROM tickets WHERE id = $1", ticket_id)
        if row is None:
            raise LookupError("ticket not found")
        return str(row["transcript"] or "")
