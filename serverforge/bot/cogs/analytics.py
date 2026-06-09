"""Analytics commands."""

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class AnalyticsCog(BaseCog):
    """Server growth and activity analytics commands."""

    @commands.slash_command(name="analytics", description="View server analytics.", default_member_permissions=disnake.Permissions(manage_guild=True))
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def analytics_slash(self, inter: disnake.ApplicationCommandInteraction) -> None:
        guild = await self.ensure_guild_inter(inter)
        summary = await self.container.analytics.summary(guild.id)
        await inter.response.send_message(str(summary) if summary else "No analytics collected yet.", ephemeral=True)

    @commands.command(name="analytics", help="View server analytics.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def analytics_prefix(self, ctx: commands.Context) -> None:
        guild = await self.ensure_guild_ctx(ctx)
        summary = await self.container.analytics.summary(guild.id)
        await ctx.reply(str(summary) if summary else "No analytics collected yet.", mention_author=False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AnalyticsCog(bot))  # type: ignore[arg-type]
