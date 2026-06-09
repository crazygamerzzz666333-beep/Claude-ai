"""Tests for AI planning and font transformations."""

import pytest

from serverforge.services.ai.service import AIPlanner
from serverforge.services.font.service import FontService
from serverforge.services.theme.service import ThemeService


@pytest.mark.asyncio
async def test_ai_planner_understands_minecraft_shop_and_small_caps() -> None:
    planner = AIPlanner(ThemeService(), FontService())
    plan = await planner.plan("Make my server look like Hypixel and create a Minecraft shop area in small caps", "Guild")
    assert plan.theme == "minecraft"
    assert any("ꜱʜᴏᴘ" == category.name for category in plan.categories)
    assert any(channel.name == "ʀᴀɴᴋ-ꜱᴛᴏʀᴇ" for channel in plan.channels)


def test_font_service_supports_bold_and_fancy() -> None:
    fonts = FontService()
    assert fonts.transform("Ab", "bold") == "𝐀𝐛"
    assert fonts.transform("hello", "fancy") == "✦ hello ✦"
