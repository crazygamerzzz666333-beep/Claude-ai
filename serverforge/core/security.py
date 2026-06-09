"""Cross-cutting security validation and dangerous-action confirmation state."""

import secrets

import disnake
from redis.asyncio import Redis


class SecurityService:
    """Validate permissions and issue confirmations for destructive operations."""

    def __init__(self, redis: Redis, dangerous_action_ttl_seconds: int) -> None:
        self._redis = redis
        self._ttl = dangerous_action_ttl_seconds

    async def require_manage_guild(self, member: disnake.Member) -> None:
        """Raise if the member cannot manage the guild."""
        if not member.guild_permissions.manage_guild:
            raise PermissionError("manage_guild permission is required")

    async def require_moderator(self, member: disnake.Member) -> None:
        """Raise if the member cannot moderate members."""
        if not (member.guild_permissions.moderate_members or member.guild_permissions.administrator):
            raise PermissionError("moderation permission is required")

    async def create_confirmation(self, guild_id: int, user_id: int, action: str) -> str:
        """Create a one-time confirmation token for a dangerous action."""
        token = secrets.token_urlsafe(16)
        key = f"confirm:{guild_id}:{user_id}:{token}"
        await self._redis.setex(key, self._ttl, action)
        return token

    async def consume_confirmation(self, guild_id: int, user_id: int, token: str, action: str) -> bool:
        """Consume and validate a confirmation token."""
        key = f"confirm:{guild_id}:{user_id}:{token}"
        value = await self._redis.get(key)
        if value is None:
            return False
        await self._redis.delete(key)
        decoded = value.decode() if isinstance(value, bytes) else str(value)
        return decoded == action
