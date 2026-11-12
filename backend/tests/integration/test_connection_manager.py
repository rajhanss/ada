"""Integration tests — ConnectionManager (device WebSocket coordinator).

Tests the in-process connection manager logic without real WebSocket
connections: connect, disconnect, dispatch, and broadcast semantics.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ada.devices.connection_manager import ConnectionManager, DeviceConnection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ws() -> MagicMock:
    """Create a minimal mock WebSocket that satisfies the manager's interface."""
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    ws.close = AsyncMock()
    return ws


async def _connect(
    cm: ConnectionManager,
    device_id: str = "dev-1",
    user_id: str = "user-1",
) -> DeviceConnection:
    """Connect a mock device and return the DeviceConnection."""
    ws = _make_ws()
    return await cm.connect(device_id=device_id, user_id=user_id, websocket=ws)


# ---------------------------------------------------------------------------
# ConnectionManager unit tests
# ---------------------------------------------------------------------------


class TestConnectionManagerConnect:
    def setup_method(self):
        self.cm = ConnectionManager()

    @pytest.mark.asyncio
    async def test_connect_registers_device(self):
        await _connect(self.cm, "dev-1")
        assert self.cm.is_connected("dev-1")

    @pytest.mark.asyncio
    async def test_connect_returns_device_connection(self):
        conn = await _connect(self.cm, "dev-1")
        assert isinstance(conn, DeviceConnection)
        assert conn.device_id == "dev-1"
        assert conn.user_id == "user-1"

    @pytest.mark.asyncio
    async def test_connect_calls_websocket_accept(self):
        ws = _make_ws()
        await self.cm.connect(device_id="dev-1", user_id="user-1", websocket=ws)
        ws.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_reconnect_replaces_old_connection(self):
        ws1 = _make_ws()
        ws2 = _make_ws()
        await self.cm.connect("dev-1", "user-1", ws1)
        await self.cm.connect("dev-1", "user-1", ws2)
        # Old connection should have been closed
        ws1.close.assert_called_once()
        # New connection is active
        assert self.cm.is_connected("dev-1")
        assert self.cm.get("dev-1").websocket is ws2


class TestConnectionManagerDisconnect:
    def setup_method(self):
        self.cm = ConnectionManager()

    @pytest.mark.asyncio
    async def test_disconnect_removes_device(self):
        await _connect(self.cm, "dev-1")
        self.cm.disconnect("dev-1")
        assert not self.cm.is_connected("dev-1")

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_is_safe(self):
        # Should not raise
        self.cm.disconnect("ghost-device")

    @pytest.mark.asyncio
    async def test_multiple_devices_same_user(self):
        await _connect(self.cm, "dev-1", "user-A")
        await _connect(self.cm, "dev-2", "user-A")
        assert self.cm.is_connected("dev-1")
        assert self.cm.is_connected("dev-2")
        assert len(self.cm.connected_device_ids) == 2


class TestConnectionManagerSend:
    def setup_method(self):
        self.cm = ConnectionManager()

    @pytest.mark.asyncio
    async def test_send_to_device_calls_send_json(self):
        ws = _make_ws()
        await self.cm.connect("dev-1", "user-1", ws)
        ok = await self.cm.send_to_device("dev-1", "task_update", {"status": "running"})
        assert ok is True
        ws.send_json.assert_called_once()
        sent = ws.send_json.call_args[0][0]
        assert sent["type"] == "task_update"
        assert sent["payload"]["status"] == "running"

    @pytest.mark.asyncio
    async def test_send_to_offline_device_returns_false(self):
        ok = await self.cm.send_to_device("ghost-device", "ping", {})
        assert ok is False

    @pytest.mark.asyncio
    async def test_broadcast_to_user_reaches_all_devices(self):
        ws1 = _make_ws()
        ws2 = _make_ws()
        await self.cm.connect("dev-1", "user-B", ws1)
        await self.cm.connect("dev-2", "user-B", ws2)
        sent_count = await self.cm.broadcast_to_user("user-B", "broadcast", {"msg": "hi"})
        assert sent_count == 2
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_user_with_no_devices_returns_zero(self):
        count = await self.cm.broadcast_to_user("user-nobody", "ping", {})
        assert count == 0

    @pytest.mark.asyncio
    async def test_broadcast_does_not_reach_other_users(self):
        ws1 = _make_ws()
        ws2 = _make_ws()
        await self.cm.connect("dev-1", "user-X", ws1)
        await self.cm.connect("dev-2", "user-Y", ws2)
        await self.cm.broadcast_to_user("user-X", "ping", {})
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_not_called()


class TestConnectionManagerDispatch:
    def setup_method(self):
        self.cm = ConnectionManager()

    @pytest.mark.asyncio
    async def test_dispatch_task_sends_to_target_device(self):
        ws = _make_ws()
        await self.cm.connect("dev-target", "user-C", ws)
        success = await self.cm.dispatch_task(
            device_id="dev-target",
            task_id="task-1",
            plan={"steps": ["read_file"]},
            tool_permissions={"read_file": True},
            autonomy_mode="supervised",
        )
        assert success is True
        ws.send_json.assert_called_once()
        sent = ws.send_json.call_args[0][0]
        assert sent["type"] == "task_dispatch"
        assert sent["payload"]["task_id"] == "task-1"

    @pytest.mark.asyncio
    async def test_dispatch_task_to_offline_device_returns_false(self):
        success = await self.cm.dispatch_task(
            device_id="offline-device",
            task_id="task-2",
            plan={},
            tool_permissions={},
            autonomy_mode="supervised",
        )
        assert success is False
