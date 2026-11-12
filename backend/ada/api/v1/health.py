from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from ada.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint. No authentication required. Used by Render."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
