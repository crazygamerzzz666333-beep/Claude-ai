"""Template commands."""

from uuid import UUID

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog
from serverforge.services.models import Visibility


class TemplateCog(BaseCog):
    """Save, load, export, import, and marketplace template commands."""

    @commands.slash_command(name="template", description="Manage ServerForge templates.", default_member_permissions=disnake.Permissions(manage_guild=True))
    async def template(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Template command group."""

    @template.sub_command(name="save", description="Save the current server as a template.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def save_slash(self, inter: disnake.ApplicationCommandInteraction, name: str, visibility: str = "private") -> None:
        guild = await self.ensure_guild_inter(inter)
        await inter.response.defer(ephemeral=True)
        plan = await self.container.ai.plan("custom", guild.name)
        template_id = await self.container.templates.save(inter.author.id, name, "Saved from Discord", plan, guild.id, Visibility(visibility))
        await self.log_command(guild.id, "template save", inter.author.id)
        await inter.followup.send(f"Saved template `{template_id}`.", ephemeral=True)

    @template.sub_command(name="load", description="Load a template into this server.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def load_slash(self, inter: disnake.ApplicationCommandInteraction, template_id: str) -> None:
        guild = await self.ensure_guild_inter(inter)
        await inter.response.defer(ephemeral=True)
        plan = await self.container.templates.load(UUID(template_id))
        result = await self.container.builder.apply_plan(guild, plan, inter.author.id)
        await inter.followup.send(f"Loaded template: {result}", ephemeral=True)

    @commands.command(name="template-save", help="Save the current server as a template.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def save_prefix(self, ctx: commands.Context, name: str, visibility: str = "private") -> None:
        guild = await self.ensure_guild_ctx(ctx)
        plan = await self.container.ai.plan("custom", guild.name)
        template_id = await self.container.templates.save(ctx.author.id, name, "Saved from Discord", plan, guild.id, Visibility(visibility))
        await ctx.reply(f"Saved template `{template_id}`.", mention_author=False)

    @commands.command(name="marketplace", help="Show public marketplace templates.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def marketplace_prefix(self, ctx: commands.Context) -> None:
        rows = await self.container.templates.marketplace()
        await ctx.reply("\n".join(f"{row['id']} - {row['name']}" for row in rows) or "No marketplace templates yet.", mention_author=False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(TemplateCog(bot))  # type: ignore[arg-type]
