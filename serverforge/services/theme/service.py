"""Theme engine for curated and custom server layouts."""

from serverforge.services.models import CategorySpec, ChannelKind, ChannelSpec, RoleSpec, ServerPlan


class ThemeService:
    """Create reusable themed server plans."""

    def build_theme(self, theme: str, guild_name: str) -> ServerPlan:
        """Build a plan for a supported theme name."""
        key = theme.lower()
        if key == "minecraft":
            return self._minecraft(guild_name)
        if key == "gaming":
            return self._gaming(guild_name)
        if key == "professional":
            return self._professional(guild_name)
        if key == "minimal":
            return self._minimal(guild_name)
        if key == "dark":
            return self._dark(guild_name)
        return self._custom(guild_name, theme)

    def _minecraft(self, guild_name: str) -> ServerPlan:
        categories = [CategorySpec(name="spawn"), CategorySpec(name="survival"), CategorySpec(name="market")]
        channels = [
            ChannelSpec(name="rules", kind=ChannelKind.text, category="spawn"),
            ChannelSpec(name="announcements", kind=ChannelKind.text, category="spawn"),
            ChannelSpec(name="general", kind=ChannelKind.text, category="survival"),
            ChannelSpec(name="trading-post", kind=ChannelKind.text, category="market"),
            ChannelSpec(name="voice-cave", kind=ChannelKind.voice, category="survival"),
        ]
        roles = [RoleSpec(name="Owner"), RoleSpec(name="Admin"), RoleSpec(name="Builder"), RoleSpec(name="Member")]
        return ServerPlan(name=guild_name, description="Minecraft-inspired community layout", theme="minecraft", categories=categories, channels=channels, roles=roles, suggestions=["Add a ticket panel for ban appeals."])

    def _gaming(self, guild_name: str) -> ServerPlan:
        categories = [CategorySpec(name="lobby"), CategorySpec(name="squads"), CategorySpec(name="events")]
        channels = [ChannelSpec(name="general", kind=ChannelKind.text, category="lobby"), ChannelSpec(name="clips", kind=ChannelKind.text, category="lobby"), ChannelSpec(name="looking-for-group", kind=ChannelKind.forum, category="squads"), ChannelSpec(name="team-voice", kind=ChannelKind.voice, category="squads")]
        return ServerPlan(name=guild_name, description="Gaming community layout", theme="gaming", categories=categories, channels=channels, roles=[RoleSpec(name="Moderator"), RoleSpec(name="Gamer")])

    def _professional(self, guild_name: str) -> ServerPlan:
        categories = [CategorySpec(name="company"), CategorySpec(name="projects"), CategorySpec(name="support")]
        channels = [ChannelSpec(name="announcements", kind=ChannelKind.text, category="company"), ChannelSpec(name="roadmap", kind=ChannelKind.forum, category="projects"), ChannelSpec(name="support-desk", kind=ChannelKind.text, category="support")]
        return ServerPlan(name=guild_name, description="Professional team workspace", theme="professional", categories=categories, channels=channels, roles=[RoleSpec(name="Leadership"), RoleSpec(name="Staff"), RoleSpec(name="Client")])

    def _minimal(self, guild_name: str) -> ServerPlan:
        return ServerPlan(name=guild_name, description="Minimal layout", theme="minimal", categories=[CategorySpec(name="main")], channels=[ChannelSpec(name="general", kind=ChannelKind.text, category="main"), ChannelSpec(name="voice", kind=ChannelKind.voice, category="main")], roles=[RoleSpec(name="Member")])

    def _dark(self, guild_name: str) -> ServerPlan:
        plan = self._minimal(guild_name)
        plan.theme = "dark"
        plan.description = "Dark aesthetic community layout"
        plan.roles.append(RoleSpec(name="Night Watch"))
        plan.suggestions.append("Use monochrome emojis and low-noise notification channels.")
        return plan

    def _custom(self, guild_name: str, theme: str) -> ServerPlan:
        plan = self._minimal(guild_name)
        plan.theme = theme
        plan.description = f"Custom {theme} layout"
        return plan
