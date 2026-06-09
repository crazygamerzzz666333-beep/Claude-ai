"""FastAPI application for health, metrics, templates, and backup inspection."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from serverforge.core.config import get_settings
from serverforge.core.container import Container, create_container
from serverforge.core.logging import configure_logging

_container: Container | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create and close API dependencies."""
    global _container
    settings = get_settings()
    configure_logging(settings.log_level)
    _container = await create_container(settings)
    app.state.container = _container
    yield
    await _container.redis.aclose()
    await _container.database.close()


app = FastAPI(title="ServerForge AI", version="1.0.0", lifespan=lifespan)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return service health."""
    return {"status": "ok"}


@app.get("/metrics", tags=["system"])
async def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/templates/marketplace", tags=["templates"])
async def marketplace(limit: int = 20) -> list[dict[str, object]]:
    """Return marketplace templates."""
    container = _require_container()
    return await container.templates.marketplace(limit)


@app.get("/templates/{template_id}", tags=["templates"])
async def export_template(template_id: UUID) -> dict[str, object]:
    """Export a template by ID."""
    container = _require_container()
    try:
        return await container.templates.export(template_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _require_container() -> Container:
    if _container is None:
        raise RuntimeError("container is not initialized")
    return _container
