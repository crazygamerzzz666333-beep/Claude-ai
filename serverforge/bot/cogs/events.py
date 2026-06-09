"""Discord event logging, protections, welcome, and analytics listeners."""

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class EventCog(BaseCog):
    """Integrated event listeners for logs, analytics, and security protections."""

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member) -> None:
        await self.container.logs.record(member.guild.id, "member_join", {"member": member.id}, target_id=member.id)
        await self.container.analytics.track(member.guild.id, "member_join", {"member_count": member.guild.member_count}, actor_id=member.id)
        await self.container.welcome.handle_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member) -> None:
        await self.container.logs.record(member.guild.id, "member_leave", {"member": member.id}, target_id=member.id)
        await self.container.analytics.track(member.guild.id, "member_leave", {"member_count": member.guild.member_count}, actor_id=member.id)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.guild is None or message.author.bot:
            return
        await self.container.analytics.track(message.guild.id, "message", {"length": len(message.content)}, actor_id=message.author.id, channel_id=message.channel.id)
        if self.container.moderation.contains_link(message.content):
            allowed = await self.container.rate_limiter.allow(f"links:{message.guild.id}:{message.author.id}", 3, 60)
            if not allowed:
                await message.delete()
                await self.container.logs.record(message.guild.id, "anti_link", {"channel": message.channel.id}, message.author.id)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel) -> None:
        await self.container.logs.record(channel.guild.id, "channel_create", {"channel": channel.id, "name": channel.name})

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: disnake.Role) -> None:
        await self.container.logs.record(role.guild.id, "role_create", {"role": role.id, "name": role.name})

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState) -> None:
        await self.container.logs.record(member.guild.id, "voice_activity", {"before": getattr(before.channel, "id", None), "after": getattr(after.channel, "id", None)}, actor_id=member.id)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventCog(bot))  # type: ignore[arg-type]
