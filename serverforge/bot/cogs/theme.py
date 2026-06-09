"""Theme and font commands."""

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class ThemeCog(BaseCog):
    """Theme engine and Unicode font commands."""

    @commands.slash_command(name="theme", description="Apply a server theme.", default_member_permissions=disnake.Permissions(manage_guild=True))
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def theme_slash(self, inter: disnake.ApplicationCommandInteraction, theme: str) -> None:
        guild = await self.ensure_guild_inter(inter)
        await inter.response.defer(ephemeral=True)
        plan = self.container.themes.build_theme(theme, guild.name)
        result = await self.container.builder.apply_plan(guild, plan, inter.author.id)
        await inter.followup.send(f"Applied `{theme}` theme: {result}", ephemeral=True)

    @commands.command(name="theme", help="Apply a server theme.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def theme_prefix(self, ctx: commands.Context, theme: str) -> None:
        guild = await self.ensure_guild_ctx(ctx)
        plan = self.container.themes.build_theme(theme, guild.name)
        result = await self.container.builder.apply_plan(guild, plan, ctx.author.id)
        await ctx.reply(f"Applied `{theme}` theme: {result}", mention_author=False)

    @commands.command(name="font", help="Preview a Unicode font style.")
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def font_prefix(self, ctx: commands.Context, style: str, *, text: str) -> None:
        await ctx.reply(self.container.fonts.transform(text, style), mention_author=False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ThemeCog(bot))  # type: ignore[arg-type]
