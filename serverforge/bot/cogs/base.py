"""Shared cog utilities."""

import disnake
from disnake.ext import commands

from serverforge.bot.bot import ServerForgeBot
from serverforge.bot.errors import handle_command_error
from serverforge.core.localization import translate


class BaseCog(commands.Cog):
    """Base cog with helpers for permissions, cooldown logging, and responses."""

    def __init__(self, bot: ServerForgeBot) -> None:
        self.bot = bot
        self.container = bot.container

    async def cog_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, error: Exception) -> None:
        """Handle slash command errors for every cog."""
        await handle_command_error(inter, error)

    async def ensure_guild_inter(self, inter: disnake.ApplicationCommandInteraction) -> disnake.Guild:
        """Return the guild or raise for DM usage."""
        if inter.guild is None:
            raise commands.NoPrivateMessage(translate("error.guild_only"))
        return inter.guild

    async def ensure_guild_ctx(self, ctx: commands.Context) -> disnake.Guild:
        """Return the guild or raise for DM usage."""
        if ctx.guild is None:
            raise commands.NoPrivateMessage(translate("error.guild_only"))
        return ctx.guild

    async def log_command(self, guild_id: int, command: str, actor_id: int) -> None:
        """Persist command usage."""
        await self.container.logs.record(guild_id, "command", {"command": command}, actor_id=actor_id)
