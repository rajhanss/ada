"""Pytest fixtures for ADA Desktop tests."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ada_desktop.local_db.sqlite_client import LocalDB
from ada_desktop.runtime.executor import LocalExecutor


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def temp_db(temp_dir: Path):
    db_file = temp_dir / "test_desktop.db"
    return LocalDB(db_path=db_file)


@pytest.fixture
def test_executor(temp_dir: Path):
    return LocalExecutor(allowed_roots=[str(temp_dir)])
