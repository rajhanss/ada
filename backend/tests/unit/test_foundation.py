from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_health_check():
    """Health endpoint returns 200 with correct structure."""
    from ada.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body
    assert "environment" in body
    assert "timestamp" in body


def test_settings_loads():
    """Settings load without crashing with defaults."""
    from ada.config import get_settings
    settings = get_settings()
    assert settings.version == "0.1.0"
    assert settings.environment == "development"


def test_api_v1_exists():
    """Health endpoint is reachable and additional routes are mounted."""
    from fastapi.testclient import TestClient
    from ada.main import app
    client = TestClient(app)
    # /health is at root — verify it responds correctly
    r = client.get("/health")
    assert r.status_code == 200
    # /api/v1/health is also mounted via the v1 router
    r2 = client.get("/api/v1/health")
    assert r2.status_code == 200
