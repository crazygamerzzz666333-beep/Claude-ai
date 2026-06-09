"""Natural-language AI planning service for Discord server design."""

import re

from serverforge.services.font.service import FontService
from serverforge.services.models import CategorySpec, ChannelKind, ChannelSpec, ServerPlan
from serverforge.services.theme.service import ThemeService


class AIPlanner:
    """Deterministic natural-language planner for safe server mutations."""

    def __init__(self, themes: ThemeService, fonts: FontService) -> None:
        self._themes = themes
        self._fonts = fonts

    async def plan(self, prompt: str, guild_name: str) -> ServerPlan:
        """Create a server plan from natural language."""
        text = prompt.lower()
        theme = self._detect_theme(text)
        plan = self._themes.build_theme(theme, guild_name)
        if "support" in text:
            self._ensure_support(plan)
        if "shop" in text or "store" in text or "market" in text:
            self._ensure_shop(plan)
        if "small caps" in text:
            self._apply_font(plan, "small_caps")
        if "improve" in text or "layout" in text:
            plan.suggestions.extend(["Separate announcement channels from discussion channels.", "Keep staff-only channels in a private category."])
        for match in re.finditer(r"add (?:a |an )?(?P<name>[a-z0-9 -]+) (?:section|area|category)", text):
            name = match.group("name").strip().replace(" ", "-")
            if name and all(category.name != name for category in plan.categories):
                plan.categories.append(CategorySpec(name=name, position=len(plan.categories)))
                plan.channels.append(ChannelSpec(name="general", kind=ChannelKind.text, category=name, position=len(plan.channels)))
        return plan

    def _detect_theme(self, text: str) -> str:
        for theme in ("minecraft", "hypixel", "gaming", "professional", "minimal", "dark"):
            if theme in text:
                return "minecraft" if theme == "hypixel" else theme
        return "custom"

    def _ensure_support(self, plan: ServerPlan) -> None:
        if all(category.name != "support" for category in plan.categories):
            plan.categories.append(CategorySpec(name="support", position=len(plan.categories)))
        existing = {channel.name for channel in plan.channels}
        for name, kind in (("open-ticket", ChannelKind.text), ("support-faq", ChannelKind.forum)):
            if name not in existing:
                plan.channels.append(ChannelSpec(name=name, kind=kind, category="support", position=len(plan.channels)))

    def _ensure_shop(self, plan: ServerPlan) -> None:
        if all(category.name != "shop" for category in plan.categories):
            plan.categories.append(CategorySpec(name="shop", position=len(plan.categories)))
        for name in ("rank-store", "crate-shop", "trade-offers"):
            if all(channel.name != name for channel in plan.channels):
                plan.channels.append(ChannelSpec(name=name, kind=ChannelKind.text, category="shop", position=len(plan.channels)))

    def _apply_font(self, plan: ServerPlan, style: str) -> None:
        for category in plan.categories:
            category.name = self._fonts.transform(category.name, style)
        for channel in plan.channels:
            channel.name = self._fonts.transform(channel.name, style)
            if channel.category:
                channel.category = self._fonts.transform(channel.category, style)
        for role in plan.roles:
            role.name = self._fonts.transform(role.name, style)
