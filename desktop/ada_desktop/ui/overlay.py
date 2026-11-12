"""Visual Guidance Desktop Overlay for ADA.

A full-screen click-through transparent canvas that draws visual annotations,
bounding highlights, step badges, and spotlights to guide the user visually.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget


@dataclass
class VisualAnnotation:
    x: int
    y: int
    width: int
    height: int
    label: str = ""
    step_number: int | None = None
    color: str = "#E87518"


class VisualOverlay(QWidget):
    """Transparent click-through desktop overlay for visual guidance."""

    def __init__(self) -> None:
        super().__init__()
        self.annotations: list[VisualAnnotation] = []

        # Flags: Transparent, frameless, stay on top, click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Match primary screen dimensions
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

    def show_annotations(self, annotations: list[VisualAnnotation], duration_ms: int = 5000) -> None:
        """Display bounding boxes and labels for a specified duration."""
        self.annotations = annotations
        self.show()
        self.update()

        if duration_ms > 0:
            QTimer.singleShot(duration_ms, self.clear_annotations)

    def clear_annotations(self) -> None:
        self.annotations = []
        self.hide()
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        if not self.annotations:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for ann in self.annotations:
            color = QColor(ann.color)

            # Draw glowing bounding box
            pen = QPen(color, 3)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
            rect = QRect(ann.x, ann.y, ann.width, ann.height)
            painter.drawRoundedRect(rect, 8, 8)

            # Draw step badge if present
            if ann.step_number is not None:
                badge_radius = 14
                badge_x = ann.x - badge_radius
                badge_y = ann.y - badge_radius
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(badge_x, badge_y, badge_radius * 2, badge_radius * 2)

                painter.setPen(QColor("#FFFFFF"))
                painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                painter.drawText(
                    QRect(badge_x, badge_y, badge_radius * 2, badge_radius * 2),
                    Qt.AlignmentFlag.AlignCenter,
                    str(ann.step_number),
                )

            # Draw label banner
            if ann.label:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(20, 20, 24, 220)))
                label_rect = QRect(ann.x, ann.y + ann.height + 6, len(ann.label) * 9 + 16, 24)
                painter.drawRoundedRect(label_rect, 4, 4)

                painter.setPen(color)
                painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, ann.label)
