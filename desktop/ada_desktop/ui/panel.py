"""Conversation and Task Control Panel for ADA Desktop Companion.

Expandable dark-themed drawer allowing text conversation, voice controls,
visual screen understanding trigger, and human-in-the-loop approval actions.
"""
from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ada_desktop.config import get_desktop_settings


class MessageCard(QFrame):
    """Visual bubble for a chat message or task event."""

    def __init__(self, role: str, content: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        is_user = (role == "user")
        bg = "#252528" if is_user else "#1A1A1C"
        border = "#3A3A3E" if is_user else "#E87518"

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            """
        )

        role_lbl = QLabel("You" if is_user else "ADA")
        role_lbl.setStyleSheet("color: #E87518; font-weight: bold; font-size: 11px;")
        layout.addWidget(role_lbl)

        content_lbl = QLabel(content)
        content_lbl.setWordWrap(True)
        content_lbl.setStyleSheet("color: #F0F0F0; font-size: 13px; line-height: 1.4;")
        layout.addWidget(content_lbl)


class ApprovalCard(QFrame):
    """Action card requesting explicit user authorization."""

    approved = Signal(str)
    denied = Signal(str)

    def __init__(self, approval_id: str, tool_name: str, reason: str, tool_args: dict[str, Any]) -> None:
        super().__init__()
        self.approval_id = approval_id

        self.setStyleSheet(
            """
            QFrame {
                background-color: #2D1B1B;
                border: 2px solid #E87518;
                border-radius: 8px;
            }
            """
        )
        layout = QVBoxLayout(self)

        title = QLabel(f"⚠️ Approval Required: {tool_name}")
        title.setStyleSheet("color: #FFA500; font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        desc = QLabel(f"Reason: {reason}\nArguments: {tool_args}")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #E0E0E0; font-size: 11px;")
        layout.addWidget(desc)

        btn_layout = QHBoxLayout()
        approve_btn = QPushButton("Approve Action")
        approve_btn.setStyleSheet("background-color: #2E7D32; color: white; padding: 6px; border-radius: 4px; font-weight: bold;")
        approve_btn.clicked.connect(lambda: self.approved.emit(self.approval_id))

        deny_btn = QPushButton("Deny")
        deny_btn.setStyleSheet("background-color: #C62828; color: white; padding: 6px; border-radius: 4px; font-weight: bold;")
        deny_btn.clicked.connect(lambda: self.denied.emit(self.approval_id))

        btn_layout.addWidget(approve_btn)
        btn_layout.addWidget(deny_btn)
        layout.addLayout(btn_layout)


class AssistantPanel(QWidget):
    """Main conversational window."""

    message_submitted = Signal(str)
    screen_requested = Signal()
    approval_resolved = Signal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_desktop_settings()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFixedSize(self.settings.panel_width, self.settings.panel_height)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #121214;
                color: #FFFFFF;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QLineEdit {
                background-color: #1F1F23;
                border: 1px solid #333338;
                border-radius: 6px;
                padding: 8px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #E87518;
            }
            QPushButton {
                background-color: #E87518;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F08A30;
            }
            """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # Header Bar
        header = QHBoxLayout()
        title_lbl = QLabel("ADA — Autonomous Digital Assistant")
        title_lbl.setStyleSheet("font-weight: bold; color: #E87518; font-size: 13px;")
        header.addWidget(title_lbl)

        header.addStretch()

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Supervised", "Bounded", "Assisted", "Conversation"])
        self.mode_selector.setStyleSheet("background-color: #222226; color: #DDD; border-radius: 4px; padding: 2px 6px;")
        header.addWidget(self.mode_selector)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("background: transparent; color: #888; font-size: 12px;")
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)

        root_layout.addLayout(header)

        # Message Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.scroll_widget)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(8)
        self.scroll.setWidget(self.scroll_widget)
        root_layout.addWidget(self.scroll)

        # Welcome message
        self.add_message("assistant", "Hello! I am ADA, your persistent personal assistant. How can I help you today?")

        # Input Row
        input_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Ask a question, or command an action...")
        self.text_input.returnPressed.connect(self._submit_message)
        input_layout.addWidget(self.text_input)

        self.screen_btn = QPushButton("👁️")
        self.screen_btn.setToolTip("Capture screen and ask ADA")
        self.screen_btn.setFixedSize(36, 36)
        self.screen_btn.setStyleSheet("background-color: #2A2A30; border-radius: 6px;")
        self.screen_btn.clicked.connect(self.screen_requested.emit)
        input_layout.addWidget(self.screen_btn)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._submit_message)
        input_layout.addWidget(self.send_btn)

        root_layout.addLayout(input_layout)

    def add_message(self, role: str, content: str) -> None:
        card = MessageCard(role, content)
        self.messages_layout.addWidget(card)
        # Scroll to bottom
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))

    def add_approval_card(self, approval_id: str, tool_name: str, reason: str, tool_args: dict[str, Any]) -> None:
        card = ApprovalCard(approval_id, tool_name, reason, tool_args)
        card.approved.connect(lambda aid: self.approval_resolved.emit(aid, True))
        card.denied.connect(lambda aid: self.approval_resolved.emit(aid, False))
        self.messages_layout.addWidget(card)
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))

    def _submit_message(self) -> None:
        text = self.text_input.text().strip()
        if not text:
            return
        self.text_input.clear()
        self.add_message("user", text)
        self.message_submitted.emit(text)
