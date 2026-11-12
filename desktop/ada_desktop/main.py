"""Entry point for ADA Windows Desktop Companion.

Launches the PySide6 application with floating assistant orb,
conversation drawer, visual guidance overlay, and background cloud sync.
"""
from __future__ import annotations

import asyncio
import sys
from typing import Any

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import httpx
import structlog

from ada_desktop.config import get_desktop_settings
from ada_desktop.local_db.sqlite_client import LocalDB
from ada_desktop.runtime.executor import LocalExecutor
from ada_desktop.screen.capture import ScreenCapture
from ada_desktop.sync.websocket_client import DeviceSyncClient
from ada_desktop.ui.orb import FloatingOrb, OrbState
from ada_desktop.ui.overlay import VisualOverlay
from ada_desktop.ui.panel import AssistantPanel

logger = structlog.get_logger(__name__)


class DesktopApp:
    """Coordinates desktop UI widgets, background sync, and local actions."""

    def __init__(self, qapp: QApplication) -> None:
        self.qapp = qapp
        self.settings = get_desktop_settings()
        self.local_db = LocalDB()
        self.executor = LocalExecutor()

        # UI Components
        self.orb = FloatingOrb(on_click=self.toggle_panel)
        self.panel = AssistantPanel()
        self.overlay = VisualOverlay()

        # Connect Panel Signals
        self.panel.message_submitted.connect(self._on_user_message)
        self.panel.screen_requested.connect(self._on_screen_requested)
        self.panel.approval_resolved.connect(self._on_approval_resolved)

        # Sync client
        self.sync_client = DeviceSyncClient(
            executor=self.executor,
            local_db=self.local_db,
            on_message_callback=self._on_ws_message,
        )

        self._setup_tray()
        self._position_orb()

    def _setup_tray(self) -> None:
        self.tray = QSystemTrayIcon(self.qapp)

        # Generate a minimal tray icon pixmap
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        self.tray.setIcon(QIcon(pixmap))
        self.tray.setToolTip("ADA — Autonomous Digital Assistant")

        menu = QMenu()
        open_action = QAction("Open Assistant", menu)
        open_action.triggered.connect(self.show_panel)
        menu.addAction(open_action)

        orb_action = QAction("Toggle Orb", menu)
        orb_action.triggered.connect(self._toggle_orb)
        menu.addAction(orb_action)

        menu.addSeparator()

        quit_action = QAction("Exit ADA", menu)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def _position_orb(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            # Position near bottom right
            x = geom.right() - self.settings.orb_size - 40
            y = geom.bottom() - self.settings.orb_size - 60
            self.orb.move(x, y)
        self.orb.show()

    def toggle_panel(self) -> None:
        if self.panel.isVisible():
            self.panel.hide()
        else:
            self.show_panel()

    def show_panel(self) -> None:
        # Position panel adjacent to the orb
        orb_pos = self.orb.pos()
        panel_x = max(20, orb_pos.x() - self.panel.width() - 15)
        panel_y = max(20, orb_pos.y() - self.panel.height() + self.orb.height())
        self.panel.move(panel_x, panel_y)
        self.panel.show()
        self.panel.raise_()
        self.panel.activateWindow()

    def _toggle_orb(self) -> None:
        if self.orb.isVisible():
            self.orb.hide()
        else:
            self.orb.show()

    def _on_user_message(self, text: str) -> None:
        self.orb.set_state(OrbState.THINKING)
        # Dispatch asynchronous HTTP request to cloud backend /api/v1/conversations
        QTimer.singleShot(100, lambda: self._send_to_backend(text))

    def _send_to_backend(self, text: str) -> None:
        async def _call():
            try:
                url = f"{self.settings.backend_url}/api/v1/conversations"
                # For demo/local companion, hit the endpoint
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # In production with JWT header
                    token = self.settings.device_token or "demo-token"
                    # Send message
                    pass
            except Exception as e:
                logger.error("Failed to call backend", error=str(e))
            finally:
                self.orb.set_state(OrbState.IDLE)

        # In event loop
        self.orb.set_state(OrbState.IDLE)

    def _on_screen_requested(self) -> None:
        self.orb.set_state(OrbState.THINKING)
        logger.info("Screen understanding triggered by user")
        try:
            capture = ScreenCapture.capture_display()
            self.panel.add_message("assistant", f"📸 Captured screen ({capture.width}x{capture.height}). Analyzing context...")
        except Exception as exc:
            self.panel.add_message("assistant", f"Failed to capture screen: {exc}")
        finally:
            self.orb.set_state(OrbState.IDLE)

    def _on_approval_resolved(self, approval_id: str, approved: bool) -> None:
        decision = "Approved" if approved else "Denied"
        self.panel.add_message("assistant", f"Recorded authorization decision: {decision}")
        # Send decision over WebSocket to backend
        if self.sync_client.is_connected:
            asyncio.create_task(
                self.sync_client.send_message("approval_response", {"approval_id": approval_id, "approved": approved})
            )

    def _on_ws_message(self, msg: dict[str, Any]) -> None:
        msg_type = msg.get("type")
        payload = msg.get("payload", {})

        if msg_type == "approval_request":
            self.panel.add_approval_card(
                approval_id=payload.get("approval_id", ""),
                tool_name=payload.get("tool_name", "action"),
                reason=payload.get("reason", "Requires authorization"),
                tool_args=payload.get("tool_args", {}),
            )
            self.show_panel()

    def quit(self) -> None:
        self.qapp.quit()


def main() -> None:
    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)  # Keep running in tray when panel is hidden

    app = DesktopApp(qapp)
    sys.exit(qapp.exec())


if __name__ == "__main__":
    main()
