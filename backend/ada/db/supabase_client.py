"""Supabase Client for ADA Backend.

Provides a singleton Supabase client authenticated via the service-role key
(never exposed to clients). If Supabase credentials are not set (e.g. in
offline development or CI tests), provides graceful in-memory storage fallback.
"""
from __future__ import annotations

from typing import Any

import structlog

from ada.config import Settings, get_settings

logger = structlog.get_logger(__name__)


class InMemoryStore:
    """In-memory key-value table store for testing and offline operation."""

    def __init__(self) -> None:
        self._tables: dict[str, dict[str, dict[str, Any]]] = {}

    def table(self, table_name: str) -> InMemoryTableQuery:
        if table_name not in self._tables:
            self._tables[table_name] = {}
        return InMemoryTableQuery(self._tables[table_name])


class InMemoryTableQuery:
    def __init__(self, table_data: dict[str, dict[str, Any]]) -> None:
        self.data = table_data
        self._filters: list[tuple[str, Any]] = []

    def eq(self, column: str, value: Any) -> InMemoryTableQuery:
        self._filters.append((column, value))
        return self

    def insert(self, record: dict[str, Any] | list[dict[str, Any]]) -> InMemoryTableQuery:
        records = [record] if isinstance(record, dict) else record
        for r in records:
            rec_id = r.get("id") or str(len(self.data) + 1)
            self.data[rec_id] = r
        return self

    def select(self, columns: str = "*") -> InMemoryTableQuery:
        return self

    def order(self, column: str, desc: bool = False) -> InMemoryTableQuery:
        return self

    def limit(self, count: int) -> InMemoryTableQuery:
        return self

    def execute(self) -> Any:
        filtered = list(self.data.values())
        for col, val in self._filters:
            filtered = [r for r in filtered if r.get(col) == val]
        return type("SupabaseResponse", (), {"data": filtered})()


_client = None
_in_memory_store = None


def get_supabase(settings: Settings | None = None) -> Any:
    """Get Supabase client or in-memory fallback."""
    global _client, _in_memory_store
    s = settings or get_settings()

    if s.supabase_url and s.supabase_service_role_key:
        if _client is None:
            try:
                from supabase import create_client
                _client = create_client(s.supabase_url, s.supabase_service_role_key)
                logger.info("Initialized Supabase service-role client", url=s.supabase_url)
            except Exception as exc:
                logger.warning("Failed to initialize Supabase client, using in-memory store", error=str(exc))
                if _in_memory_store is None:
                    _in_memory_store = InMemoryStore()
                return _in_memory_store
        return _client

    if _in_memory_store is None:
        _in_memory_store = InMemoryStore()
    return _in_memory_store
