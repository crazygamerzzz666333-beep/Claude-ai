"""Disnake bot factory and lifecycle hooks."""

import disnake
from disnake.ext import commands

from serverforge.bot.errors import handle_command_error
from serverforge.core.container import Container
from serverforge.core.logging import get_logger
from serverforge.db.migrations import run_migrations

LOGGER = get_logger(__name__)
COGS = (
    "serverforge.bot.cogs.ai",
    "serverforge.bot.cogs.templates",
    "serverforge.bot.cogs.backups",
    "serverforge.bot.cogs.moderation",
    "serverforge.bot.cogs.tickets",
    "serverforge.bot.cogs.welcome",
    "serverforge.bot.cogs.analytics",
    "serverforge.bot.cogs.theme",
    "serverforge.bot.cogs.events",
)


class ServerForgeBot(commands.Bot):
    """ServerForge AI Discord bot."""

    def __init__(self, container: Container) -> None:
        intents = disnake.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.reactions = True
        super().__init__(command_prefix=container.settings.bot_prefix, intents=intents, help_command=None)
        self.container = container

    async def setup_hook(self) -> None:
        """Run migrations and load cogs before connecting."""
        await run_migrations(self.container.database)
        for cog in COGS:
            self.load_extension(cog)
        await LOGGER.ainfo("bot_setup_complete", cogs=len(COGS))

    async def on_ready(self) -> None:
        """Log readiness."""
        await LOGGER.ainfo("bot_ready", user=str(self.user), guilds=len(self.guilds))

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handle prefix command errors."""
        await handle_command_error(ctx, error)


def create_bot(container: Container) -> ServerForgeBot:
    """Create a configured bot instance."""
    return ServerForgeBot(container)
