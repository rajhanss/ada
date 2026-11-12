"""Conversations and Messages Repository for ADA."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

import structlog

from ada.db.supabase_client import get_supabase, InMemoryStore
from ada.models.domain import Conversation, Message

logger = structlog.get_logger(__name__)

_global_fallback_store = InMemoryStore()


class ConversationRepository:
    def __init__(self, client: Any = None) -> None:
        self.client = client or get_supabase()
        self._fallback_store = _global_fallback_store

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
        try:
            self.client.table("conversations").insert(record).execute()
        except Exception as e:
            logger.warning("Supabase table insert failed, saving to in-memory store", error=str(e))
            self._fallback_store.table("conversations").insert(record).execute()
        return record

    async def list_for_user(self, user_id: str) -> list[dict[str, Any]]:
        try:
            resp = self.client.table("conversations").select("*").eq("user_id", user_id).execute()
            return resp.data or []
        except Exception as e:
            logger.warning("Supabase table select failed, loading from in-memory store", error=str(e))
            resp = self._fallback_store.table("conversations").select("*").eq("user_id", user_id).execute()
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
        try:
            self.client.table("messages").insert(record).execute()
        except Exception as e:
            logger.warning("Supabase message insert failed, saving to in-memory store", error=str(e))
            self._fallback_store.table("messages").insert(record).execute()
        return record

    async def get_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        try:
            resp = self.client.table("messages").select("*").eq("conversation_id", conversation_id).execute()
            return resp.data or []
        except Exception as e:
            logger.warning("Supabase message select failed, loading from in-memory store", error=str(e))
            resp = self._fallback_store.table("messages").select("*").eq("conversation_id", conversation_id).execute()
            return resp.data or []
