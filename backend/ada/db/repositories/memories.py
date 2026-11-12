"""Memories Repository for ADA (Vector / Episodic / Semantic memory)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from ada.db.supabase_client import get_supabase


class MemoryRepository:
    def __init__(self, client: Any = None) -> None:
        self.client = client or get_supabase()

    async def create(
        self,
        user_id: str,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        confidence: float = 0.8,
        embedding: list[float] | None = None,
        source: str = "conversation",
    ) -> dict[str, Any]:
        mem_id = str(uuid.uuid4())
        record = {
            "id": mem_id,
            "user_id": user_id,
            "content": content,
            "category": category,
            "importance": importance,
            "confidence": confidence,
            "embedding": embedding,
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("memories").insert(record).execute()
        return record

    async def list_for_user(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        resp = self.client.table("memories").select("*").eq("user_id", user_id).limit(limit).execute()
        return resp.data or []

    async def search_similar(self, user_id: str, query_embedding: list[float], match_count: int = 5) -> list[dict[str, Any]]:
        """In production with pgvector, calls match_memories RPC in Postgres."""
        resp = self.client.table("memories").select("*").eq("user_id", user_id).limit(match_count).execute()
        return resp.data or []
