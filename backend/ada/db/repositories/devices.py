"""Devices Repository for ADA."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from ada.db.supabase_client import get_supabase


class DeviceRepository:
    def __init__(self, client: Any = None) -> None:
        self.client = client or get_supabase()

    async def register(
        self,
        user_id: str,
        device_type: str,
        display_name: str,
        platform: str,
        capabilities: list[str],
        token_hash: str,
    ) -> dict[str, Any]:
        dev_id = str(uuid.uuid4())
        record = {
            "id": dev_id,
            "user_id": user_id,
            "device_type": device_type,
            "display_name": display_name,
            "platform": platform,
            "capabilities": capabilities,
            "token_hash": token_hash,
            "is_revoked": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("devices").insert(record).execute()
        return record

    async def list_for_user(self, user_id: str) -> list[dict[str, Any]]:
        resp = self.client.table("devices").select("*").eq("user_id", user_id).execute()
        return [d for d in (resp.data or []) if not d.get("is_revoked")]

    async def get_by_id(self, device_id: str) -> dict[str, Any] | None:
        resp = self.client.table("devices").select("*").eq("id", device_id).execute()
        items = resp.data or []
        return items[0] if items else None

    async def revoke(self, device_id: str) -> None:
        record = {
            "id": device_id,
            "is_revoked": True,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("devices").insert(record).execute()
