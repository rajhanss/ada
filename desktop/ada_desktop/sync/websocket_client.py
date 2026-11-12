"""WebSocket Synchronization Client for ADA Desktop Companion.

Connects to the Cloud Backend WebSocket endpoint (/api/v1/ws).
Handles:
- Device authentication via device token
- Inbound task dispatches
- Task execution via LocalExecutor
- In-flight execution progress and completion reporting
- Automatic reconnection with exponential backoff
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

import structlog
import websockets

from ada_desktop.config import get_desktop_settings
from ada_desktop.local_db.sqlite_client import LocalDB
from ada_desktop.runtime.executor import LocalExecutor

logger = structlog.get_logger(__name__)


class DeviceSyncClient:
    """Manages persistent WebSocket communication with the ADA Cloud Backend."""

    def __init__(
        self,
        executor: LocalExecutor | None = None,
        local_db: LocalDB | None = None,
        on_message_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.settings = get_desktop_settings()
        self.executor = executor or LocalExecutor()
        self.local_db = local_db or LocalDB()
        self.on_message_callback = on_message_callback

        self._running = False
        self._connected = False
        self._ws: Any = None
        self._reconnect_delay = 2.0
        self._max_reconnect_delay = 60.0

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def start(self) -> None:
        """Run the persistent connection loop."""
        self._running = True
        logger.info("Starting Desktop Sync Client", ws_url=self.settings.backend_ws_url)

        while self._running:
            try:
                # Append device credentials as query params
                token = self.settings.device_token or self.local_db.get_config("device_token", "dev_token_placeholder")
                device_id = self.settings.device_id or self.local_db.get_config("device_id", "desktop-primary")
                url = f"{self.settings.backend_ws_url}?device_id={device_id}&token={token}"

                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                    self._ws = ws
                    self._connected = True
                    self._reconnect_delay = 2.0
                    logger.info("Connected to ADA Cloud Backend WebSocket")

                    await self._listen_loop(ws)

            except (websockets.ConnectionClosed, OSError, asyncio.TimeoutError) as exc:
                self._connected = False
                self._ws = None
                if not self._running:
                    break
                logger.warning(
                    "WebSocket disconnected, reconnecting...",
                    delay=self._reconnect_delay,
                    error=str(exc),
                )
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(self._reconnect_delay * 1.5, self._max_reconnect_delay)

    async def stop(self) -> None:
        self._running = False
        if self._ws:
            await self._ws.close()
        self._connected = False
        logger.info("Desktop Sync Client stopped")

    async def _listen_loop(self, ws: Any) -> None:
        async for raw_msg in ws:
            try:
                data = json.loads(raw_msg)
                await self._handle_message(data)
            except Exception as exc:
                logger.error("Failed to process incoming WebSocket message", error=str(exc))

    async def _handle_message(self, msg: dict[str, Any]) -> None:
        msg_type = msg.get("type")
        payload = msg.get("payload", {})

        if self.on_message_callback:
            try:
                self.on_message_callback(msg)
            except Exception:
                pass

        if msg_type == "task_dispatch":
            await self._handle_task_dispatch(payload)
        elif msg_type == "ping":
            await self.send_message("pong", {})

    async def _handle_task_dispatch(self, payload: dict[str, Any]) -> None:
        task_id = payload.get("task_id", "unknown_task")
        plan = payload.get("plan", {})
        steps = plan.get("steps", [])

        logger.info("Received task dispatch", task_id=task_id, steps_count=len(steps))

        # Acknowledge receipt
        await self.send_message("task_ack", {"task_id": task_id, "status": "running"})

        overall_success = True
        step_results = []

        for step in steps:
            tool_name = step.get("tool_name", "")
            tool_args = step.get("tool_args", {})

            # Cache task locally
            self.local_db.cache_task(
                task_id=task_id,
                title=step.get("description", "Execute step"),
                tool_name=tool_name,
                tool_args=tool_args,
                status="running",
            )

            # Execute tool
            exec_res = await self.executor.execute_tool(tool_name, tool_args)
            step_results.append({
                "step_id": step.get("step_id"),
                "success": exec_res.success,
                "output": exec_res.output,
                "error": exec_res.error,
            })

            if not exec_res.success:
                overall_success = False
                break

        # Send completion report
        status_str = "completed" if overall_success else "failed"
        await self.send_message(
            "task_result",
            {
                "task_id": task_id,
                "status": status_str,
                "results": step_results,
            },
        )

        self.local_db.cache_task(
            task_id=task_id,
            title="Task Result",
            tool_name="task_dispatch",
            tool_args={},
            status=status_str,
            result=step_results,
        )

    async def send_message(self, msg_type: str, payload: dict[str, Any]) -> bool:
        if not self._ws or not self._connected:
            return False
        try:
            msg = {"type": msg_type, "payload": payload}
            await self._ws.send(json.dumps(msg))
            return True
        except Exception as exc:
            logger.warning("Failed to send WebSocket message", error=str(exc))
            return False
