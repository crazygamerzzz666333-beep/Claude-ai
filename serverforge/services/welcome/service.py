"""Welcome message, embeds, images, GIFs, auto-role, DM, and placeholders."""

from typing import Any

import disnake

from serverforge.db.pool import Database


class WelcomeService:
    """Render and dispatch welcome experiences."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def config(self, guild_id: int) -> dict[str, Any]:
        """Return welcome configuration."""
        row = await self._database.fetchrow("SELECT welcome_config FROM guild_settings WHERE guild_id = $1", guild_id)
        return dict(row["welcome_config"]) if row else {}

    async def handle_join(self, member: disnake.Member) -> None:
        """Apply auto roles and send welcome messages for a joining member."""
        config = await self.config(member.guild.id)
        role_id = config.get("auto_role_id")
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role is not None:
                await member.add_roles(role, reason="ServerForge welcome auto role")
        message = self.render(str(config.get("message", "Welcome {member} to {server}!")), member)
        channel_id = config.get("channel_id")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if isinstance(channel, disnake.TextChannel):
                embed = disnake.Embed(description=message, colour=disnake.Colour.blurple()) if config.get("embed", True) else None
                await channel.send(content=None if embed else message, embed=embed)
        if config.get("dm", False):
            await member.send(message)

    def render(self, template: str, member: disnake.Member) -> str:
        """Render custom placeholders."""
        return template.format(member=member.mention, member_name=member.display_name, server=member.guild.name, member_count=member.guild.member_count)
