"""Premium entitlement and feature flag service."""

from datetime import UTC, datetime
from typing import Any

from serverforge.db.pool import Database


class PremiumService:
    """Resolve premium users, premium guilds, and feature flags."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def guild_features(self, guild_id: int) -> dict[str, Any]:
        """Return active guild feature flags."""
        row = await self._database.fetchrow("SELECT feature_flags, expires_at FROM premium_guilds WHERE guild_id = $1", guild_id)
        if row is None:
            return {}
        expires_at = row["expires_at"]
        if expires_at is not None and expires_at < datetime.now(UTC):
            return {}
        return dict(row["feature_flags"])

    async def enabled(self, guild_id: int, feature: str) -> bool:
        """Return whether a premium feature is enabled for a guild."""
        features = await self.guild_features(guild_id)
        return bool(features.get(feature))
