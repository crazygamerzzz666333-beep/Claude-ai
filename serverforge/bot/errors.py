"""Centralized bot error handling."""

import disnake
from disnake.ext import commands

from serverforge.core.localization import translate
from serverforge.core.logging import get_logger

LOGGER = get_logger(__name__)


async def handle_command_error(ctx: commands.Context | disnake.ApplicationCommandInteraction, error: Exception) -> None:
    """Handle prefix and slash command errors consistently."""
    await LOGGER.aerror("command_error", error=str(error), command=getattr(ctx, "command", None))
    message = translate("error.permissions") if isinstance(error, (commands.MissingPermissions, PermissionError)) else str(error)
    if isinstance(error, commands.CommandOnCooldown):
        message = translate("error.cooldown")
    if isinstance(ctx, disnake.ApplicationCommandInteraction):
        if ctx.response.is_done():
            await ctx.followup.send(message, ephemeral=True)
        else:
            await ctx.response.send_message(message, ephemeral=True)
    else:
        await ctx.reply(message, mention_author=False)
