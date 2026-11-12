"""Groq provider adapter for ultra-low latency inference.

Used for fast intent classification, quick voice acknowledgments,
and rapid summarization (Llama 3.3 70B Versatile, Llama 3.1 8B Instant).
"""
from __future__ import annotations

from ada.providers.base import ModelCapability, ModelSpec
from ada.providers.openai_compatible import OpenAICompatibleAdapter

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Standard Groq model specs in ADA
GROQ_MODELS: dict[str, ModelSpec] = {
    "qwen/qwen3.8-27b": ModelSpec(
        model_id="qwen/qwen3.8-27b",
        provider="groq",
        display_name="Groq Qwen 3.8 27B",
        context_window=32_000,
        cost_per_million_input=0.20,
        cost_per_million_output=0.40,
        typical_latency_ms=180,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.FAST,
        }),
    ),
    "whisper-large-v3-turbo": ModelSpec(
        model_id="whisper-large-v3-turbo",
        provider="groq",
        display_name="Groq Whisper Large v3 Turbo",
        context_window=8192,
        cost_per_million_input=0.04,
        cost_per_million_output=0.04,
        typical_latency_ms=100,
        capabilities=frozenset({
            ModelCapability.FAST,
        }),
    ),
}


class GroqAdapter(OpenAICompatibleAdapter):
    """Adapter for Groq Cloud API."""

    def __init__(
        self,
        spec: ModelSpec,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        super().__init__(
            spec=spec,
            api_key=api_key,
            base_url=GROQ_BASE_URL,
            timeout_seconds=timeout_seconds,
        )
