"""Text-to-Speech (TTS) engine for ADA Desktop Companion.

Uses Microsoft edge-tts for high-quality, natural neural voices
with zero API cost and low latency.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts
import structlog

from ada_desktop.config import get_desktop_settings

logger = structlog.get_logger(__name__)


class TextToSpeech:
    """Natural neural speech synthesis."""

    def __init__(self, voice: str | None = None) -> None:
        settings = get_desktop_settings()
        self.voice = voice or settings.tts_voice

    async def synthesize_to_file(self, text: str, output_path: Path) -> Path:
        """Synthesize text into an audio MP3 file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(str(output_path))
        logger.info("Synthesized speech", text_preview=text[:40], path=str(output_path))
        return output_path

    async def synthesize_to_bytes(self, text: str) -> bytes:
        """Synthesize text into in-memory audio bytes."""
        communicate = edge_tts.Communicate(text, self.voice)
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        return b"".join(audio_chunks)
