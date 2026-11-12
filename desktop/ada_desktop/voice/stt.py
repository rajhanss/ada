"""Speech-to-Text (STT) transcription for ADA Desktop Companion.

Transcribes audio from push-to-talk microphone recordings.
"""
from __future__ import annotations

import httpx
import structlog

from ada_desktop.config import get_desktop_settings

logger = structlog.get_logger(__name__)

GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class SpeechToText:
    """Audio transcription client."""

    def __init__(self, api_key: str | None = None) -> None:
        settings = get_desktop_settings()
        self.api_key = api_key or settings.groq_api_key

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """Transcribe audio bytes using Groq Whisper or fallback."""
        if not self.api_key:
            logger.warning("No Groq API key configured for STT, returning empty transcript")
            return ""

        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": (filename, audio_bytes, "audio/wav")}
        data = {"model": "whisper-large-v3"}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(GROQ_AUDIO_URL, headers=headers, files=files, data=data)
                resp.raise_for_status()
                res_data = resp.json()
                transcript = res_data.get("text", "")
                logger.info("Transcribed audio", text=transcript[:50])
                return transcript
        except Exception as exc:
            logger.error("Audio transcription failed", error=str(exc))
            return ""
