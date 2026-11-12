"""Unit tests for Screen Capture engine."""
from __future__ import annotations

from ada_desktop.screen.capture import ScreenCapture, ScreenCaptureResult


def test_list_monitors():
    monitors = ScreenCapture.list_monitors()
    assert isinstance(monitors, list)
    assert len(monitors) >= 1
    # First entry in mss is always the all-monitor bounding box
    assert "width" in monitors[0]
    assert "height" in monitors[0]


def test_capture_display():
    res = ScreenCapture.capture_display(monitor_index=1)
    assert isinstance(res, ScreenCaptureResult)
    assert res.width > 0
    assert res.height > 0
    assert len(res.image_bytes) > 0
    assert res.format == "PNG"
