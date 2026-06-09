"""AI design commands."""

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class AICog(BaseCog):
    """Natural language server builder commands."""

    @commands.slash_command(name="forge", description="Ask ServerForge AI to design or modify this server.", default_member_permissions=disnake.Permissions(manage_guild=True))
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def forge_slash(self, inter: disnake.ApplicationCommandInteraction, prompt: str) -> None:
        """Generate and apply a server plan from a prompt."""
        guild = await self.ensure_guild_inter(inter)
        await self.container.security.require_manage_guild(inter.author)  # type: ignore[arg-type]
        await inter.response.defer(ephemeral=True)
        plan = await self.container.ai.plan(prompt, guild.name)
        result = await self.container.builder.apply_plan(guild, plan, inter.author.id)
        await self.log_command(guild.id, "forge", inter.author.id)
        await inter.followup.send(f"Applied `{plan.theme}` plan: {result}. Suggestions: {'; '.join(plan.suggestions) or 'None'}", ephemeral=True)

    @commands.command(name="forge", help="Ask ServerForge AI to design or modify this server.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def forge_prefix(self, ctx: commands.Context, *, prompt: str) -> None:
        """Prefix variant of forge."""
        guild = await self.ensure_guild_ctx(ctx)
        plan = await self.container.ai.plan(prompt, guild.name)
        result = await self.container.builder.apply_plan(guild, plan, ctx.author.id)
        await self.log_command(guild.id, "forge", ctx.author.id)
        await ctx.reply(f"Applied `{plan.theme}` plan: {result}", mention_author=False)


def setup(bot: commands.Bot) -> None:
    """Load cog."""
    bot.add_cog(AICog(bot))  # type: ignore[arg-type]
