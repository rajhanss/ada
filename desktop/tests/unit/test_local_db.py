"""Unit tests for Local SQLite Client."""
from __future__ import annotations

from pathlib import Path

from ada_desktop.local_db.sqlite_client import LocalDB


def test_config_storage(temp_db: LocalDB):
    temp_db.set_config("device_token", "secret-token-xyz")
    val = temp_db.get_config("device_token")
    assert val == "secret-token-xyz"

    missing = temp_db.get_config("nonexistent_key", default="fallback")
    assert missing == "fallback"


def test_task_caching(temp_db: LocalDB):
    temp_db.cache_task(
        task_id="task-101",
        title="Compile binary",
        tool_name="run_dev_command",
        tool_args={"command": "cargo build"},
        status="running",
    )

    task = temp_db.get_cached_task("task-101")
    assert task is not None
    assert task["task_id"] == "task-101"
    assert task["status"] == "running"
    assert task["tool_args"]["command"] == "cargo build"

    # Update result
    temp_db.cache_task(
        task_id="task-101",
        title="Compile binary",
        tool_name="run_dev_command",
        tool_args={"command": "cargo build"},
        status="completed",
        result={"exit_code": 0},
    )
    updated = temp_db.get_cached_task("task-101")
    assert updated["status"] == "completed"
    assert updated["result"]["exit_code"] == 0
