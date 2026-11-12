"""Conversations and Messages Repository for ADA."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from ada.db.supabase_client import get_supabase
from ada.models.domain import Conversation, Message


class ConversationRepository:
    def __init__(self, client: Any = None) -> None:
        self.client = client or get_supabase()

    async def create(self, user_id: str, title: str | None = None, autonomy_mode: str = "supervised") -> dict[str, Any]:
        conv_id = str(uuid.uuid4())
        record = {
            "id": conv_id,
            "user_id": user_id,
            "title": title or "New Conversation",
            "autonomy_mode": autonomy_mode,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("conversations").insert(record).execute()
        return record

    async def list_for_user(self, user_id: str) -> list[dict[str, Any]]:
        resp = self.client.table("conversations").select("*").eq("user_id", user_id).execute()
        return resp.data or []

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        msg_id = str(uuid.uuid4())
        record = {
            "id": msg_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("messages").insert(record).execute()
        return record

    async def get_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        resp = self.client.table("messages").select("*").eq("conversation_id", conversation_id).execute()
        return resp.data or []
