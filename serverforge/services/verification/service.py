"""Button, CAPTCHA, and auto-role verification service."""

import secrets

import disnake
from redis.asyncio import Redis

from serverforge.db.pool import Database


class VerificationService:
    """Verify members through buttons or CAPTCHA codes."""

    def __init__(self, database: Database, redis: Redis) -> None:
        self._database = database
        self._redis = redis

    async def issue_captcha(self, guild_id: int, user_id: int) -> str:
        """Create a short CAPTCHA code."""
        code = secrets.token_hex(3).upper()
        await self._redis.setex(f"captcha:{guild_id}:{user_id}", 600, code)
        return code

    async def verify_captcha(self, member: disnake.Member, code: str) -> bool:
        """Verify a CAPTCHA code and grant verification role."""
        key = f"captcha:{member.guild.id}:{member.id}"
        expected = await self._redis.get(key)
        if expected is None:
            return False
        decoded = expected.decode() if isinstance(expected, bytes) else str(expected)
        if decoded.upper() != code.upper():
            return False
        await self._redis.delete(key)
        await self.grant_role(member)
        return True

    async def grant_role(self, member: disnake.Member) -> None:
        """Grant the configured verification role."""
        row = await self._database.fetchrow("SELECT verification_config FROM guild_settings WHERE guild_id = $1", member.guild.id)
        role_id = dict(row["verification_config"]).get("role_id") if row else None
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role is not None:
                await member.add_roles(role, reason="ServerForge verification")
