"""ADA Backend — application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ada.config import get_settings
from ada.logging import configure_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("ADA backend starting", version=settings.version, environment=settings.environment)
    # Future: initialise DB connection pool, WebSocket manager, model registry
    yield
    logger.info("ADA backend shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ADA — Autonomous Digital Assistant",
        version=settings.version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check — mounted at root, no auth, required by Render
    from ada.api.v1.health import router as health_router
    app.include_router(health_router)

    # WebSocket — device sessions (outside /api/v1 prefix)
    from ada.api.v1.ws import router as ws_router
    app.include_router(ws_router)

    # API v1 — all domain routers go under /api/v1
    from ada.api.v1 import router as api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")

    # Static UI — serve React SaaS landing page & web dashboard
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles

    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


app = create_app()
