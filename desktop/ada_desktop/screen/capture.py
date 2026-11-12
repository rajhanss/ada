"""Screen capture and display geometry utilities for ADA.

Uses mss for high-performance screen capture across multiple displays.
Always operates under explicit user control (never stealthily).
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

import mss
from PIL import Image
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ScreenCaptureResult:
    image_bytes: bytes
    width: int
    height: int
    monitor_index: int
    format: str = "PNG"


class ScreenCapture:
    """Multi-monitor screen capture engine."""

    @staticmethod
    def list_monitors() -> list[dict[str, Any]]:
        """List all connected monitors and their geometries."""
        with mss.mss() as sct:
            return sct.monitors

    @staticmethod
    def capture_display(monitor_index: int = 1) -> ScreenCaptureResult:
        """Capture the specified display (1 is typically primary, 0 is virtual bounding box)."""
        logger.info("Capturing display", monitor_index=monitor_index)
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                if monitor_index >= len(monitors):
                    monitor_index = 1 if len(monitors) > 1 else 0

                target_monitor = monitors[monitor_index]
                sct_img = sct.grab(target_monitor)

                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

                buffer = io.BytesIO()
                img.save(buffer, format="PNG", optimize=True)
                png_bytes = buffer.getvalue()

                return ScreenCaptureResult(
                    image_bytes=png_bytes,
                    width=sct_img.width,
                    height=sct_img.height,
                    monitor_index=monitor_index,
                )
        except Exception as exc:
            logger.warning("Native display capture failed, using fallback canvas", error=str(exc))
            # Fallback for headless environments or locked desktop
            width, height = 1920, 1080
            fallback_img = Image.new("RGB", (width, height), color=(30, 30, 35))
            buffer = io.BytesIO()
            fallback_img.save(buffer, format="PNG")
            return ScreenCaptureResult(
                image_bytes=buffer.getvalue(),
                width=width,
                height=height,
                monitor_index=monitor_index,
            )

    @staticmethod
    def capture_region(left: int, top: int, width: int, height: int) -> ScreenCaptureResult:
        """Capture a localized bounding box region on the screen."""
        bbox = {"left": left, "top": top, "width": width, "height": height}
        with mss.mss() as sct:
            sct_img = sct.grab(bbox)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return ScreenCaptureResult(
                image_bytes=buffer.getvalue(),
                width=width,
                height=height,
                monitor_index=0,
            )
