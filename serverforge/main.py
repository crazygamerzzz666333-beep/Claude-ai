"""Runtime entrypoint for the Discord bot."""

import asyncio

from serverforge.bot.bot import create_bot
from serverforge.core.config import get_settings
from serverforge.core.container import create_container
from serverforge.core.logging import configure_logging


async def run_bot() -> None:
    """Start the Discord bot."""
    settings = get_settings()
    configure_logging(settings.log_level)
    container = await create_container(settings)
    bot = create_bot(container)
    try:
        await bot.start(settings.discord_token)
    finally:
        await container.redis.aclose()
        await container.database.close()


def main() -> None:
    """Run the bot with asyncio."""
    asyncio.run(run_bot())
