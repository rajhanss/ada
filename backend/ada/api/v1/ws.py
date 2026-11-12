"""WebSocket endpoint for device sessions."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from ada.auth.dependencies import hash_device_token
from ada.devices.connection_manager import get_connection_manager
from ada.models.domain import ConnectionState

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def web_client_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for web dashboard and browser clients."""
    await websocket.accept()
    logger.info("Web dashboard WebSocket connected")
    try:
        await websocket.send_json({"type": "connected", "payload": {"status": "ok", "message": "Connected to ADA Cloud"}})
        async for raw in websocket.iter_text():
            try:
                msg = json.loads(raw)
                msg_type = msg.get("type", "ping")
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong", "payload": {"timestamp": datetime.now(timezone.utc).isoformat()}})
                else:
                    await websocket.send_json({"type": "ack", "payload": {"received": msg_type}})
            except Exception:
                pass
    except WebSocketDisconnect:
        logger.info("Web dashboard WebSocket disconnected")


@router.websocket("/ws/device")
async def device_websocket(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    """Authenticated WebSocket endpoint for desktop/mobile device sessions.

    Authentication:
        ?token=<device_token>  — validated against stored hash in Supabase

    Message protocol:
        All messages are JSON: { "id": "uuid", "type": "...", "payload": {} }

    Client → Server types:
        ping, task_event, task_result, capability_update, ack

    Server → Client types:
        pong, task_dispatch, task_cancel, config_update, ack
    """
    manager = get_connection_manager()
    device_id: str | None = None
    user_id: str | None = None

    try:
        # TODO: validate token hash against Supabase device_sessions table
        # For now, parse device_id from token header (placeholder until DB is wired)
        # In production: look up token_hash → device_id, user_id, check expiry/revoked
        token_hash = hash_device_token(token)
        # Placeholder lookup — replace with real Supabase query in Stage B
        device_id = f"dev-{token_hash[:8]}"
        user_id = "placeholder-user"

        conn = await manager.connect(device_id, user_id, websocket)
        logger.info("WebSocket session started", device_id=device_id)

        async for raw in websocket.iter_text():
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON from device", device_id=device_id)
                continue

            msg_type = msg.get("type", "")
            msg_id = msg.get("id", "")
            payload = msg.get("payload", {})

            if msg_type == "ping":
                conn.last_ping_at = datetime.now(timezone.utc)
                await conn.send(
                    __import__("ada.models.domain", fromlist=["WSMessage"]).WSMessage(
                        id=msg_id, type="pong", payload={}
                    )
                )

            elif msg_type == "ack":
                # Device acknowledged a message we sent it
                acked_id = payload.get("id", "")
                conn.acknowledge(acked_id)

            elif msg_type == "task_event":
                # Desktop reporting a task execution event
                task_id = payload.get("task_id")
                event_type = payload.get("event_type")
                logger.info(
                    "Task event from device",
                    device_id=device_id,
                    task_id=task_id,
                    event_type=event_type,
                )
                # TODO: persist task_event to Supabase + push FCM notification

            elif msg_type == "capability_update":
                # Device reporting its current capabilities
                logger.info(
                    "Capability update from device",
                    device_id=device_id,
                    capabilities=payload.get("capabilities", []),
                )
                # TODO: update device capabilities in Supabase

            else:
                logger.debug("Unknown message type", msg_type=msg_type, device_id=device_id)

    except WebSocketDisconnect:
        logger.info("Device WebSocket disconnected", device_id=device_id)
    except Exception as exc:
        logger.error("WebSocket error", device_id=device_id, error=str(exc))
    finally:
        if device_id:
            manager.disconnect(device_id)
