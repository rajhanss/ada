"""API v1 router — aggregates all domain routers."""
from __future__ import annotations

from fastapi import APIRouter

from ada.api.v1.approvals import router as approvals_router
from ada.api.v1.conversations import router as conversations_router
from ada.api.v1.devices import router as devices_router
from ada.api.v1.health import router as health_router
from ada.api.v1.tasks import router as tasks_router

router = APIRouter()

# Health (also mounted at root in main.py for Render's health check)
router.include_router(health_router)

# Domain routers
router.include_router(devices_router,       prefix="/devices")
router.include_router(conversations_router, prefix="/conversations")
router.include_router(tasks_router,         prefix="/tasks")
router.include_router(approvals_router,     prefix="/approvals")

# Stage B — will be enabled when intelligence core is wired:
# router.include_router(memories_router,    prefix="/memories",    tags=["memories"])
# router.include_router(models_router,      prefix="/models",      tags=["models"])
# router.include_router(permissions_router, prefix="/permissions",  tags=["permissions"])
