"""Welcome and verification commands."""

import disnake
from disnake.ext import commands

from serverforge.bot.cogs.base import BaseCog


class WelcomeCog(BaseCog):
    """Welcome and verification management commands."""

    @commands.slash_command(name="verify", description="Complete CAPTCHA verification.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def verify_slash(self, inter: disnake.ApplicationCommandInteraction, code: str) -> None:
        if not isinstance(inter.author, disnake.Member):
            raise TypeError("verification requires a guild member")
        verified = await self.container.verification.verify_captcha(inter.author, code)
        await inter.response.send_message("Verified." if verified else "Invalid CAPTCHA.", ephemeral=True)

    @commands.command(name="captcha", help="Issue a CAPTCHA code for verification testing.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def captcha_prefix(self, ctx: commands.Context) -> None:
        guild = await self.ensure_guild_ctx(ctx)
        code = await self.container.verification.issue_captcha(guild.id, ctx.author.id)
        await ctx.author.send(f"Your ServerForge verification code is `{code}`.")
        await ctx.reply("I sent your verification code by DM.", mention_author=False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(WelcomeCog(bot))  # type: ignore[arg-type]
