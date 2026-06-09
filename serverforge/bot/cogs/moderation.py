"""Moderation commands."""

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class ModerationCog(BaseCog):
    """Ban, kick, timeout, warn, lockdown, anti-spam, anti-link, and anti-raid commands."""

    @commands.slash_command(name="mod", description="Moderate and protect the server.", default_member_permissions=disnake.Permissions(moderate_members=True))
    async def mod(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Moderation command group."""

    @mod.sub_command(name="warn", description="Warn a member.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def warn_slash(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str) -> None:
        await self.container.moderation.warn(member, inter.author, reason)  # type: ignore[arg-type]
        await inter.response.send_message(f"Warned {member.mention}.", ephemeral=True)

    @mod.sub_command(name="timeout", description="Timeout a member.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def timeout_slash(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, minutes: int, reason: str) -> None:
        await self.container.moderation.timeout(member, inter.author, minutes, reason)  # type: ignore[arg-type]
        await inter.response.send_message(f"Timed out {member.mention}.", ephemeral=True)

    @mod.sub_command(name="lockdown", description="Lock all text channels.")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def lockdown_slash(self, inter: disnake.ApplicationCommandInteraction, reason: str) -> None:
        guild = await self.ensure_guild_inter(inter)
        count = await self.container.moderation.lockdown(guild, inter.author, reason)  # type: ignore[arg-type]
        await inter.response.send_message(f"Locked {count} channels.", ephemeral=True)

    @commands.command(name="warn", help="Warn a member.")
    @commands.has_permissions(moderate_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def warn_prefix(self, ctx: commands.Context, member: disnake.Member, *, reason: str) -> None:
        await self.container.moderation.warn(member, ctx.author, reason)  # type: ignore[arg-type]
        await ctx.reply(f"Warned {member.mention}.", mention_author=False)

    @commands.command(name="lockdown", help="Lock all text channels.")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def lockdown_prefix(self, ctx: commands.Context, *, reason: str) -> None:
        guild = await self.ensure_guild_ctx(ctx)
        count = await self.container.moderation.lockdown(guild, ctx.author, reason)  # type: ignore[arg-type]
        await ctx.reply(f"Locked {count} channels.", mention_author=False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ModerationCog(bot))  # type: ignore[arg-type]
