"""Local SQLite Client for ADA Desktop Companion.

Stores local settings, cached tasks, offline action queue, and device credentials.
Ensures the assistant can operate offline and sync state when reconnected.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

from ada_desktop.config import get_desktop_settings

logger = structlog.get_logger(__name__)


from contextlib import contextmanager

class LocalDB:
    def __init__(self, db_path: Path | None = None) -> None:
        settings = get_desktop_settings()
        self.db_path = db_path or settings.local_db_path
        self._init_db()

    @contextmanager
    def _connection(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS local_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cached_tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    tool_args TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );

                CREATE TABLE IF NOT EXISTS offline_action_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP NOT NULL
                );
                """
            )
        logger.info("Local SQLite database initialized", path=str(self.db_path))

    def set_config(self, key: str, value: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO local_config (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, now),
            )

    def get_config(self, key: str, default: str | None = None) -> str | None:
        with self._connection() as conn:
            cur = conn.execute("SELECT value FROM local_config WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    def cache_task(
        self,
        task_id: str,
        title: str,
        tool_name: str,
        tool_args: dict[str, Any],
        status: str,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cached_tasks
                (task_id, title, tool_name, tool_args, status, result, error, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    title,
                    tool_name,
                    json.dumps(tool_args),
                    status,
                    json.dumps(result) if result else None,
                    error,
                    now,
                    now,
                ),
            )

    def get_cached_task(self, task_id: str) -> dict[str, Any] | None:
        with self._connection() as conn:
            cur = conn.execute("SELECT * FROM cached_tasks WHERE task_id = ?", (task_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "task_id": row["task_id"],
                "title": row["title"],
                "tool_name": row["tool_name"],
                "tool_args": json.loads(row["tool_args"]),
                "status": row["status"],
                "result": json.loads(row["result"]) if row["result"] else None,
                "error": row["error"],
            }
