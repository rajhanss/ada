"""Approvals Repository for ADA."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from ada.db.supabase_client import get_supabase
from ada.models.domain import ApprovalStatus


class ApprovalRepository:
    def __init__(self, client: Any = None) -> None:
        self.client = client or get_supabase()

    async def create(
        self,
        user_id: str,
        tool_name: str,
        tool_args: dict[str, Any],
        risk_level: str,
        reason: str,
        task_id: str | None = None,
        device_id: str | None = None,
    ) -> dict[str, Any]:
        app_id = str(uuid.uuid4())
        record = {
            "id": app_id,
            "user_id": user_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "risk_level": risk_level,
            "reason": reason,
            "task_id": task_id,
            "device_id": device_id,
            "status": ApprovalStatus.PENDING.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("approvals").insert(record).execute()
        return record

    async def list_pending(self, user_id: str) -> list[dict[str, Any]]:
        resp = self.client.table("approvals").select("*").eq("user_id", user_id).execute()
        return [a for a in (resp.data or []) if a.get("status") == ApprovalStatus.PENDING.value]

    async def resolve(self, approval_id: str, approved: bool) -> None:
        status = ApprovalStatus.APPROVED.value if approved else ApprovalStatus.DENIED.value
        record = {
            "id": approval_id,
            "status": status,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("approvals").insert(record).execute()
