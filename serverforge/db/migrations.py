"""Database migration runner."""

from pathlib import Path

from serverforge.db.pool import Database

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "001_schema.sql"


async def run_migrations(database: Database) -> None:
    """Run idempotent SQL migrations."""
    await database.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
