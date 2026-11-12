"""Tasks Repository for ADA."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from ada.db.supabase_client import get_supabase
from ada.models.domain import TaskStatus


class TaskRepository:
    def __init__(self, client: Any = None) -> None:
        self.client = client or get_supabase()

    async def create(
        self,
        user_id: str,
        title: str,
        description: str,
        tool_name: str,
        tool_args: dict[str, Any],
        device_id: str | None = None,
        priority: int = 5,
    ) -> dict[str, Any]:
        task_id = str(uuid.uuid4())
        record = {
            "id": task_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "device_id": device_id,
            "priority": priority,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("tasks").insert(record).execute()
        return record

    async def list_for_user(self, user_id: str) -> list[dict[str, Any]]:
        resp = self.client.table("tasks").select("*").eq("user_id", user_id).execute()
        return resp.data or []

    async def get_by_id(self, task_id: str) -> dict[str, Any] | None:
        resp = self.client.table("tasks").select("*").eq("id", task_id).execute()
        items = resp.data or []
        return items[0] if items else None

    async def update_status(self, task_id: str, status: TaskStatus, result: Any = None, error: str | None = None) -> None:
        record = {
            "id": task_id,
            "status": status.value,
            "result": result,
            "error": error,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("tasks").insert(record).execute()
