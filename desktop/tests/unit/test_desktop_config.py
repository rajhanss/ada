"""Unit tests for Desktop Settings."""
from __future__ import annotations

from ada_desktop.config import DesktopSettings, get_desktop_settings


def test_default_desktop_settings():
    settings = get_desktop_settings()
    assert settings.backend_url.startswith("http")
    assert settings.orb_size == 56
    assert "#E87518" in settings.primary_color
    assert len(settings.allowed_roots) >= 1
