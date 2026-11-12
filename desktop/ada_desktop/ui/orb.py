"""Floating Assistant Orb for ADA Desktop Companion.

A lightweight, draggable, pulsing circular widget that lives unobtrusively
on the user's desktop, signaling status and providing single-click access.
"""
from __future__ import annotations

from enum import Enum
from typing import Callable

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget

from ada_desktop.config import get_desktop_settings


class OrbState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    SCANNING = "scanning"
    ERROR = "error"


class FloatingOrb(QWidget):
    """Floating transparent desktop widget representing ADA's physical presence."""

    clicked = Signal()

    def __init__(self, on_click: Callable[[], None] | None = None) -> None:
        super().__init__()
        self.settings = get_desktop_settings()
        self.state = OrbState.IDLE
        self._on_click = on_click
        if on_click:
            self.clicked.connect(on_click)

        # Window flags: Frameless, stay on top, tool window (no taskbar item)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._drag_position = QPoint()
        self._pulse_phase = 0.0
        self._pulse_direction = 1

        # Pulse timer for breathing animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate_pulse)
        self.timer.start(50)  # 20 FPS pulse

        size = self.settings.orb_size
        self.setFixedSize(size + 16, size + 16)  # padding for glow

    def set_state(self, new_state: OrbState) -> None:
        self.state = new_state
        self.update()

    def _animate_pulse(self) -> None:
        speed = 0.05 if self.state == OrbState.IDLE else 0.12
        self._pulse_phase += speed * self._pulse_direction
        if self._pulse_phase >= 1.0:
            self._pulse_phase = 1.0
            self._pulse_direction = -1
        elif self._pulse_phase <= 0.0:
            self._pulse_phase = 0.0
            self._pulse_direction = 1
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        base_radius = self.settings.orb_size / 2.0
        pulse_extra = self._pulse_phase * 4.0
        radius = base_radius + pulse_extra

        # Color mapping by state
        if self.state == OrbState.IDLE:
            core_color = QColor(232, 117, 24)       # ADA Saffron
            glow_color = QColor(232, 117, 24, 60)
        elif self.state == OrbState.LISTENING:
            core_color = QColor(0, 195, 255)        # Electric Cyan
            glow_color = QColor(0, 195, 255, 90)
        elif self.state == OrbState.THINKING:
            core_color = QColor(255, 180, 0)        # Amber Yellow
            glow_color = QColor(255, 180, 0, 80)
        elif self.state == OrbState.SPEAKING:
            core_color = QColor(140, 230, 80)       # Sage Green
            glow_color = QColor(140, 230, 80, 80)
        else:  # ERROR
            core_color = QColor(230, 50, 50)        # Crimson
            glow_color = QColor(230, 50, 50, 90)

        # Outer Glow
        gradient = QRadialGradient(center_x, center_y, radius + 8)
        gradient.setColorAt(0.0, glow_color)
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRect(int(center_x - radius - 8), int(center_y - radius - 8), int((radius + 8) * 2), int((radius + 8) * 2)))

        # Inner Solid Orb with soft specular highlight
        inner_gradient = QRadialGradient(center_x - 4, center_y - 4, radius)
        inner_gradient.setColorAt(0.0, core_color.lighter(130))
        inner_gradient.setColorAt(0.8, core_color)
        inner_gradient.setColorAt(1.0, core_color.darker(140))

        painter.setBrush(QBrush(inner_gradient))
        painter.drawEllipse(QRect(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2)))

        # Draw Expressive Animated Eyes / Visor
        if self.state == OrbState.SCANNING:
            # Scanning Visor Bar
            visor_w = radius * 1.3
            visor_h = 6
            visor_x = center_x - (visor_w / 2.0)
            visor_y = center_y - 3 + (self._pulse_phase * 6 - 3)
            painter.setBrush(QBrush(QColor(0, 195, 255)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRect(int(visor_x), int(visor_y), int(visor_w), int(visor_h)), 3, 3)
        else:
            # Two Expressive Glowing Eyes
            eye_spacing = 9
            eye_radius = 3.5
            eye_y = center_y - 1

            # Dark eye socket
            painter.setBrush(QBrush(QColor(18, 18, 24)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRect(int(center_x - eye_spacing - eye_radius), int(eye_y - eye_radius), int(eye_radius * 2), int(eye_radius * 2)))
            painter.drawEllipse(QRect(int(center_x + eye_spacing - eye_radius), int(eye_y - eye_radius), int(eye_radius * 2), int(eye_radius * 2)))

            # Bright white cyber pupils
            pupil_r = 1.8
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QRect(int(center_x - eye_spacing - pupil_r), int(eye_y - pupil_r), int(pupil_r * 2), int(pupil_r * 2)))
            painter.drawEllipse(QRect(int(center_x + eye_spacing - pupil_r), int(eye_y - pupil_r), int(pupil_r * 2), int(pupil_r * 2)))

    # Drag and click support
    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            # If mouse didn't drag far, treat as click
            self.clicked.emit()
            event.accept()
