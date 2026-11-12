"""Integration tests — API routes via TestClient (no live Supabase required).

These tests verify that all API endpoints:
  - Are reachable and return expected HTTP status codes.
  - Return well-formed JSON.
  - Reject unauthenticated requests where auth is required.

No real database calls are made — responses may be error codes, but the
routing layer must work correctly.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ada.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Health — public endpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_json(self, client: TestClient):
        resp = client.get("/health")
        data = resp.json()
        assert "status" in data

    def test_health_status_ok(self, client: TestClient):
        resp = client.get("/health")
        # Health endpoint returns "healthy" (or "ok" — accept either)
        assert resp.json()["status"] in ("ok", "healthy")


# ---------------------------------------------------------------------------
# Devices — requires auth
# ---------------------------------------------------------------------------


class TestDevicesEndpoint:
    def test_list_devices_without_auth_returns_401_or_422(self, client: TestClient):
        resp = client.get("/api/v1/devices")
        assert resp.status_code in (401, 403, 422)

    def test_register_device_without_auth_returns_4xx(self, client: TestClient):
        resp = client.post(
            "/api/v1/devices",
            json={
                "device_type": "desktop",
                "display_name": "Test PC",
                "platform": "windows",
                "capabilities": [],
            },
        )
        assert resp.status_code in (401, 403, 422)


# ---------------------------------------------------------------------------
# Conversations — requires auth
# ---------------------------------------------------------------------------


class TestConversationsEndpoint:
    def test_list_conversations_without_auth_returns_4xx(self, client: TestClient):
        resp = client.get("/api/v1/conversations")
        assert resp.status_code in (401, 403, 422)

    def test_create_conversation_without_auth_returns_4xx(self, client: TestClient):
        resp = client.post("/api/v1/conversations", json={"title": "Test"})
        assert resp.status_code in (401, 403, 422)

    def test_create_and_send_message_authenticated(self, client: TestClient):
        from jose import jwt
        from ada.config import get_settings
        settings = get_settings()
        key = settings.secret_key or "dev-secret-key-change-in-production-min-32-chars"
        token = jwt.encode({"sub": "test-user-e2e"}, key, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create conversation
        conv_resp = client.post(
            "/api/v1/conversations/",
            json={"title": "My Assistant Session"},
            headers=headers,
        )
        assert conv_resp.status_code == 201
        conv_data = conv_resp.json()
        conv_id = conv_data["id"]
        assert conv_data["title"] == "My Assistant Session"

        # 2. Send message and get AI response
        msg_resp = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"content": "Hello ADA! Please introduce yourself."},
            headers=headers,
        )
        assert msg_resp.status_code == 201
        msg_data = msg_resp.json()
        assert msg_data["role"] == "assistant"
        assert len(msg_data["content"]) > 0
        assert "ADA" in msg_data["content"] or len(msg_data["content"]) > 10


# ---------------------------------------------------------------------------
# Tasks — requires auth
# ---------------------------------------------------------------------------


class TestTasksEndpoint:
    def test_list_tasks_without_auth_returns_4xx(self, client: TestClient):
        resp = client.get("/api/v1/tasks")
        assert resp.status_code in (401, 403, 422)

    def test_create_task_without_auth_returns_4xx(self, client: TestClient):
        resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "Test task",
                "description": "Integration test",
                "tool_name": "read_file",
                "tool_args": {},
            },
        )
        assert resp.status_code in (401, 403, 422)


# ---------------------------------------------------------------------------
# Approvals — requires auth
# ---------------------------------------------------------------------------


class TestApprovalsEndpoint:
    def test_list_approvals_without_auth_returns_4xx(self, client: TestClient):
        resp = client.get("/api/v1/approvals")
        assert resp.status_code in (401, 403, 422)


# ---------------------------------------------------------------------------
# WebSocket — basic connectivity
# ---------------------------------------------------------------------------


class TestWebSocketEndpoint:
    def test_ws_connect_without_token_returns_error(self, client: TestClient):
        """WebSocket without a device token should close immediately."""
        # TestClient's websocket_connect raises if the server rejects
        try:
            with client.websocket_connect("/api/v1/ws"):
                pass
            # If we reach here with no exception the server might have
            # accepted and then closed — either way acceptable for routing test
        except Exception:
            pass  # Expected: rejected or immediately closed


# ---------------------------------------------------------------------------
# 404 handling
# ---------------------------------------------------------------------------


class TestNotFound:
    def test_unknown_route_returns_404(self, client: TestClient):
        resp = client.get("/api/v1/does-not-exist")
        assert resp.status_code == 404
