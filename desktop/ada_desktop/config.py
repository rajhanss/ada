"""Configuration for ADA Windows Desktop Companion."""
from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DesktopSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ADA_DESKTOP_",
        env_file=".env",
        extra="ignore",
    )

    # Cloud backend connection
    backend_url: str = "http://127.0.0.1:8000"
    backend_ws_url: str = "ws://127.0.0.1:8000/api/v1/ws"
    device_token: str = Field(default="")
    device_id: str = Field(default="")
    device_name: str = "Windows Primary Workstation"

    # Execution boundaries
    allowed_roots: list[str] = Field(
        default_factory=lambda: [
            os.path.expanduser("~"),
            "C:\\Projects",
        ]
    )

    # Local SQLite Cache
    local_db_path: Path = Path.home() / ".ada" / "desktop_cache.db"

    # UI Preferences
    theme: str = "dark"
    orb_size: int = 56
    primary_color: str = "#E87518"        # ADA Saffron accent
    background_dark: str = "#121212"
    panel_width: int = 400
    panel_height: int = 600

    # Global Hotkeys
    hotkey_toggle: str = "Ctrl+Shift+Space"
    hotkey_ptt: str = "Ctrl+Shift+V"       # Push to talk

    # Voice & Audio
    voice_enabled: bool = True
    tts_voice: str = "en-US-JennyNeural"
    groq_api_key: str = Field(default="")


def get_desktop_settings() -> DesktopSettings:
    return DesktopSettings()
