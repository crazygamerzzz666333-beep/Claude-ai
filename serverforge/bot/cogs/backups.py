"""Backup commands."""

from uuid import UUID

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class BackupCog(BaseCog):
    """Create, compare, undo, redo, schedule, and partially restore backups."""

    @commands.slash_command(name="backup", description="Manage server backups.", default_member_permissions=disnake.Permissions(manage_guild=True))
    async def backup(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Backup command group."""

    @backup.sub_command(name="create", description="Create a full server snapshot.")
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def create_slash(self, inter: disnake.ApplicationCommandInteraction, reason: str = "manual") -> None:
        guild = await self.ensure_guild_inter(inter)
        await inter.response.defer(ephemeral=True)
        backup_id = await self.container.backups.snapshot_guild(guild, inter.author.id, reason)
        await inter.followup.send(f"Created backup `{backup_id}`.", ephemeral=True)

    @backup.sub_command(name="compare", description="Compare a backup with the current server.")
    async def compare_slash(self, inter: disnake.ApplicationCommandInteraction, backup_id: str) -> None:
        guild = await self.ensure_guild_inter(inter)
        result = await self.container.backups.compare(guild, UUID(backup_id), inter.author.id)
        await inter.response.send_message(str(result), ephemeral=True)

    @commands.command(name="backup", help="Create a full server snapshot.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def create_prefix(self, ctx: commands.Context, *, reason: str = "manual") -> None:
        guild = await self.ensure_guild_ctx(ctx)
        backup_id = await self.container.backups.snapshot_guild(guild, ctx.author.id, reason)
        await ctx.reply(f"Created backup `{backup_id}`.", mention_author=False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(BackupCog(bot))  # type: ignore[arg-type]
