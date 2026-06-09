"""Ticket commands."""

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class TicketCog(BaseCog):
    """Ticket open, claim, close, reopen, and transcript commands."""

    @commands.slash_command(name="ticket", description="Manage support tickets.")
    async def ticket(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Ticket command group."""

    @ticket.sub_command(name="open", description="Open a support ticket.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def open_slash(self, inter: disnake.ApplicationCommandInteraction, subject: str) -> None:
        guild = await self.ensure_guild_inter(inter)
        channel = await self.container.tickets.create(guild, inter.author, subject)  # type: ignore[arg-type]
        await inter.response.send_message(f"Opened {channel.mention}.", ephemeral=True)

    @ticket.sub_command(name="claim", description="Claim the current ticket.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def claim_slash(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if not isinstance(inter.channel, disnake.TextChannel):
            raise TypeError("ticket commands require a text channel")
        await self.container.tickets.claim(inter.channel, inter.author)  # type: ignore[arg-type]
        await inter.response.send_message("Ticket claimed.", ephemeral=True)

    @commands.command(name="ticket", help="Open a support ticket.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ticket_prefix(self, ctx: commands.Context, *, subject: str) -> None:
        guild = await self.ensure_guild_ctx(ctx)
        channel = await self.container.tickets.create(guild, ctx.author, subject)  # type: ignore[arg-type]
        await ctx.reply(f"Opened {channel.mention}.", mention_author=False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(TicketCog(bot))  # type: ignore[arg-type]
