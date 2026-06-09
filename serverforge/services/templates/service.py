"""Server template save, load, import, export, and marketplace service."""

from uuid import UUID

from serverforge.db.pool import Database
from serverforge.services.models import ServerPlan, Visibility


class TemplateService:
    """Persist and retrieve server templates."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def save(self, owner_id: int, name: str, description: str, plan: ServerPlan, guild_id: int | None = None, visibility: Visibility = Visibility.private) -> UUID:
        """Save a template and return its ID."""
        row = await self._database.fetchrow(
            "INSERT INTO templates (guild_id, owner_id, name, description, visibility, theme, payload) VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb) RETURNING id",
            guild_id,
            owner_id,
            name,
            description,
            visibility.value,
            plan.theme,
            plan.model_dump(mode="json"),
        )
        return UUID(str(row["id"]))

    async def load(self, template_id: UUID) -> ServerPlan:
        """Load a template plan by ID."""
        row = await self._database.fetchrow("SELECT payload FROM templates WHERE id = $1", template_id)
        if row is None:
            raise LookupError("template not found")
        await self._database.execute("UPDATE templates SET downloads = downloads + 1 WHERE id = $1", template_id)
        return ServerPlan.model_validate(dict(row["payload"]))

    async def export(self, template_id: UUID) -> dict[str, object]:
        """Export a template payload for external storage."""
        row = await self._database.fetchrow("SELECT name, description, visibility, theme, payload FROM templates WHERE id = $1", template_id)
        if row is None:
            raise LookupError("template not found")
        return dict(row)

    async def import_template(self, owner_id: int, payload: dict[str, object], visibility: Visibility) -> UUID:
        """Import a template payload."""
        plan = ServerPlan.model_validate(payload["payload"])
        return await self.save(owner_id, str(payload["name"]), str(payload.get("description", "Imported template")), plan, visibility=visibility)

    async def marketplace(self, limit: int = 20) -> list[dict[str, object]]:
        """List marketplace templates."""
        rows = await self._database.fetch("SELECT id, name, description, theme, downloads FROM templates WHERE visibility = 'marketplace' ORDER BY downloads DESC, created_at DESC LIMIT $1", limit)
        return [dict(row) for row in rows]
