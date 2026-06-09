"""Discord server builder for applying plans safely."""

from collections.abc import Iterable
from typing import Any

import disnake

from serverforge.services.analytics.service import AnalyticsService
from serverforge.services.logging.service import GuildLogService
from serverforge.services.models import ChannelKind, ServerPlan


class ServerBuilder:
    """Apply categories, channels, roles, permissions, and ordering to Discord guilds."""

    def __init__(self, analytics: AnalyticsService, logs: GuildLogService) -> None:
        self._analytics = analytics
        self._logs = logs

    async def apply_plan(self, guild: disnake.Guild, plan: ServerPlan, actor_id: int) -> dict[str, int]:
        """Apply a server plan to a guild and return mutation counts."""
        role_count = await self._apply_roles(guild, plan.roles)
        category_by_name = await self._apply_categories(guild, plan)
        channel_count = await self._apply_channels(guild, plan, category_by_name)
        await self._reorder(guild, plan)
        payload = {"roles": role_count, "categories": len(category_by_name), "channels": channel_count, "theme": plan.theme}
        await self._logs.record(guild.id, "server_builder", payload, actor_id=actor_id)
        await self._analytics.track(guild.id, "server_builder_apply", payload, actor_id=actor_id)
        return payload

    async def clone_category(self, source: disnake.CategoryChannel, name: str) -> disnake.CategoryChannel:
        """Clone a category and its child channels."""
        clone = await source.clone(name=name)
        for channel in source.channels:
            await channel.clone(category=clone)
        return clone

    async def bulk_rename_channels(self, guild: disnake.Guild, names: Iterable[tuple[int, str]]) -> int:
        """Bulk rename channels by ID."""
        count = 0
        for channel_id, name in names:
            channel = guild.get_channel(channel_id)
            if channel is not None and hasattr(channel, "edit"):
                await channel.edit(name=name, reason="ServerForge AI bulk rename")
                count += 1
        return count

    async def _apply_roles(self, guild: disnake.Guild, roles: list[Any]) -> int:
        existing = {role.name for role in guild.roles}
        count = 0
        for role in roles:
            if role.name not in existing:
                await guild.create_role(name=role.name, permissions=disnake.Permissions(role.permissions), colour=disnake.Colour(role.color), hoist=role.hoist, mentionable=role.mentionable, reason="ServerForge AI role creation")
                count += 1
        return count

    async def _apply_categories(self, guild: disnake.Guild, plan: ServerPlan) -> dict[str, disnake.CategoryChannel]:
        existing = {category.name: category for category in guild.categories}
        for category in plan.categories:
            if category.name not in existing:
                existing[category.name] = await guild.create_category(name=category.name, position=category.position, reason="ServerForge AI category creation")
        return existing

    async def _apply_channels(self, guild: disnake.Guild, plan: ServerPlan, categories: dict[str, disnake.CategoryChannel]) -> int:
        existing = {channel.name for channel in guild.channels}
        count = 0
        for channel in plan.channels:
            if channel.name in existing:
                continue
            category = categories.get(channel.category or "")
            if channel.kind == ChannelKind.text:
                await guild.create_text_channel(channel.name, category=category, topic=channel.topic, slowmode_delay=channel.slowmode_delay, position=channel.position, reason="ServerForge AI text channel creation")
            elif channel.kind == ChannelKind.voice:
                await guild.create_voice_channel(channel.name, category=category, position=channel.position, reason="ServerForge AI voice channel creation")
            elif channel.kind == ChannelKind.stage:
                await guild.create_stage_channel(channel.name, category=category, position=channel.position, reason="ServerForge AI stage channel creation")
            elif channel.kind == ChannelKind.forum:
                await guild.create_forum_channel(channel.name, category=category, topic=channel.topic, position=channel.position, reason="ServerForge AI forum channel creation")
            count += 1
        return count

    async def _reorder(self, guild: disnake.Guild, plan: ServerPlan) -> None:
        positions = {channel.name: channel.position for channel in plan.channels}
        for channel in guild.channels:
            position = positions.get(channel.name)
            if position is not None and channel.position != position:
                await channel.edit(position=position, reason="ServerForge AI channel ordering")
