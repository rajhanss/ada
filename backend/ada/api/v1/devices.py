"""Device management API — registration, listing, revocation."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from ada.auth.dependencies import (
    generate_device_token,
    get_current_user_id,
    hash_device_token,
    device_token_expires_at,
)
from ada.config import get_settings
from ada.models.domain import Device, DeviceRegister, DeviceRegistered, new_uuid

router = APIRouter(tags=["devices"])


@router.post("/", response_model=DeviceRegistered, status_code=201)
async def register_device(
    body: DeviceRegister,
    user_id: str = Depends(get_current_user_id),
) -> DeviceRegistered:
    """Register a new device and return a one-time device token.

    The raw token is returned ONCE. The device must store it in
    secure platform storage (Windows Credential Manager / Android Keystore).
    """
    settings = get_settings()
    raw_token = generate_device_token()
    token_hash = hash_device_token(raw_token)
    expires_at = device_token_expires_at(settings.device_token_ttl_hours)
    device_id = new_uuid()

    # TODO (Stage A complete): persist to Supabase via service client
    # For now, return the token structure so the desktop can be built against it.

    return DeviceRegistered(
        device_id=device_id,
        device_token=raw_token,  # returned ONCE — not stored
        expires_at=expires_at,
    )


@router.get("/", response_model=list[Device])
async def list_devices(
    user_id: str = Depends(get_current_user_id),
) -> list[Device]:
    """List all devices registered to the current user."""
    # TODO: query Supabase devices table filtered by user_id
    return []


@router.delete("/{device_id}", status_code=204)
async def revoke_device(
    device_id: str,
    user_id: str = Depends(get_current_user_id),
) -> None:
    """Revoke a device. Its token is invalidated and WebSocket is closed."""
    # TODO: revoke in Supabase + close active WebSocket via ConnectionManager
    pass
