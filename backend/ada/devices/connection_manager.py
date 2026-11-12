"""WebSocket connection manager for authenticated device sessions.

Design:
- Each desktop/mobile device connects once with a short-lived device_token.
- The server holds one WebSocket per device_id in memory.
- Messages are JSON-serialized WSMessage envelopes with an `id` for ACKs.
- On disconnect: state stays in Supabase; the device reconnects with backoff.
- If the backend restarts: devices reconnect; in-flight task state is in DB.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import WebSocket

from ada.models.domain import ConnectionState, WSMessage, new_uuid

logger = structlog.get_logger(__name__)


class DeviceConnection:
    """Active WebSocket connection for one device."""

    def __init__(self, device_id: str, user_id: str, websocket: WebSocket) -> None:
        self.device_id = device_id
        self.user_id = user_id
        self.websocket = websocket
        self.connected_at = datetime.now(timezone.utc)
        self.last_ping_at: datetime | None = None
        self._pending_acks: dict[str, asyncio.Future[bool]] = {}

    async def send(self, message: WSMessage) -> None:
        """Send a message to this device."""
        try:
            await self.websocket.send_json(message.model_dump())
        except Exception as exc:
            logger.warning(
                "WebSocket send failed",
                device_id=self.device_id,
                error=str(exc),
            )
            raise

    async def send_and_wait_ack(
        self,
        message: WSMessage,
        timeout_seconds: float = 10.0,
    ) -> bool:
        """Send a message and wait for the device to acknowledge it."""
        future: asyncio.Future[bool] = asyncio.get_event_loop().create_future()
        self._pending_acks[message.id] = future
        try:
            await self.send(message)
            return await asyncio.wait_for(future, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.warning("ACK timeout", device_id=self.device_id, message_id=message.id)
            return False
        finally:
            self._pending_acks.pop(message.id, None)

    def acknowledge(self, message_id: str) -> None:
        """Mark a sent message as acknowledged by the device."""
        future = self._pending_acks.get(message_id)
        if future and not future.done():
            future.set_result(True)


class ConnectionManager:
    """Manages all active device WebSocket connections.

    Thread-safety: FastAPI/uvicorn uses an async event loop; all access
    to this manager is from the same loop, so no locking is required.
    """

    def __init__(self) -> None:
        # device_id → DeviceConnection
        self._connections: dict[str, DeviceConnection] = {}

    async def connect(
        self,
        device_id: str,
        user_id: str,
        websocket: WebSocket,
    ) -> DeviceConnection:
        """Accept a new WebSocket and register the device connection."""
        await websocket.accept()
        conn = DeviceConnection(device_id=device_id, user_id=user_id, websocket=websocket)
        # If device reconnects, replace old connection (may be stale)
        old = self._connections.get(device_id)
        if old:
            logger.info("Device reconnected, closing old connection", device_id=device_id)
            try:
                await old.websocket.close(code=1001)
            except Exception:
                pass
        self._connections[device_id] = conn
        logger.info(
            "Device connected",
            device_id=device_id,
            user_id=user_id,
            total_connections=len(self._connections),
        )
        return conn

    def disconnect(self, device_id: str) -> None:
        """Remove a device connection (call when WebSocket closes)."""
        self._connections.pop(device_id, None)
        logger.info(
            "Device disconnected",
            device_id=device_id,
            total_connections=len(self._connections),
        )

    def get(self, device_id: str) -> DeviceConnection | None:
        return self._connections.get(device_id)

    def is_connected(self, device_id: str) -> bool:
        return device_id in self._connections

    @property
    def connected_device_ids(self) -> list[str]:
        return list(self._connections.keys())

    async def send_to_device(
        self,
        device_id: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> bool:
        """Send a typed message to a device. Returns False if device is offline."""
        conn = self._connections.get(device_id)
        if not conn:
            logger.warning("Device offline, cannot send", device_id=device_id)
            return False
        msg = WSMessage(id=new_uuid(), type=message_type, payload=payload)
        try:
            await conn.send(msg)
            return True
        except Exception:
            self.disconnect(device_id)
            return False

    async def dispatch_task(
        self,
        device_id: str,
        task_id: str,
        plan: dict[str, Any],
        tool_permissions: dict[str, Any],
        autonomy_mode: str,
    ) -> bool:
        """Dispatch a task to a device for local execution."""
        return await self.send_to_device(
            device_id,
            "task_dispatch",
            {
                "task_id": task_id,
                "plan": plan,
                "tool_permissions": tool_permissions,
                "autonomy_mode": autonomy_mode,
            },
        )

    async def broadcast_to_user(
        self,
        user_id: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> int:
        """Send a message to all connected devices owned by a user. Returns count."""
        sent = 0
        for conn in list(self._connections.values()):
            if conn.user_id == user_id:
                ok = await self.send_to_device(conn.device_id, message_type, payload)
                if ok:
                    sent += 1
        return sent


# ---------------------------------------------------------------------------
# Singleton — shared across the FastAPI application lifetime
# ---------------------------------------------------------------------------

_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
