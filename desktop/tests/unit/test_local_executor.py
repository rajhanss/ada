"""Unit tests for Local Tool Executor."""
from __future__ import annotations

from pathlib import Path
import pytest

from ada_desktop.runtime.executor import LocalExecutor


def test_path_validation(temp_dir: Path, test_executor: LocalExecutor):
    inside_path = str(temp_dir / "valid_file.txt")
    outside_path = "C:\\Windows\\System32\\calc.exe"

    assert test_executor.validate_path(inside_path) is True
    assert test_executor.validate_path(outside_path) is False


@pytest.mark.asyncio
async def test_write_and_read_file(temp_dir: Path, test_executor: LocalExecutor):
    target = temp_dir / "test_notes.md"

    # Write file
    write_res = await test_executor.execute_tool(
        "write_file",
        {"path": str(target), "content": "# ADA Desktop Notes\nTested successfully."},
    )
    assert write_res.success is True
    assert target.exists()

    # Read file
    read_res = await test_executor.execute_tool("read_file", {"path": str(target)})
    assert read_res.success is True
    assert "# ADA Desktop Notes" in read_res.output


@pytest.mark.asyncio
async def test_path_outside_allowed_roots_is_blocked(test_executor: LocalExecutor):
    res = await test_executor.execute_tool(
        "write_file",
        {"path": "C:\\Unauthorized\\secret.txt", "content": "blocked"},
    )
    assert res.success is False
    assert "outside allowed directory roots" in res.error


@pytest.mark.asyncio
async def test_run_dev_command(temp_dir: Path, test_executor: LocalExecutor):
    res = await test_executor.execute_tool(
        "run_dev_command",
        {"command": "python -c \"print('Hello from ADA desktop executor')\"", "cwd": str(temp_dir)},
    )
    assert res.success is True
    assert "Hello from ADA desktop executor" in res.output["stdout"]
