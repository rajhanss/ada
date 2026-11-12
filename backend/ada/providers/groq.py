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
    "llama-3.3-70b-versatile": ModelSpec(
        model_id="llama-3.3-70b-versatile",
        provider="groq",
        display_name="Groq Llama 3.3 70B",
        context_window=128_000,
        cost_per_million_input=0.59,
        cost_per_million_output=0.79,
        typical_latency_ms=250,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.FAST,
        }),
    ),
    "llama-3.1-8b-instant": ModelSpec(
        model_id="llama-3.1-8b-instant",
        provider="groq",
        display_name="Groq Llama 3.1 8B Instant",
        context_window=128_000,
        cost_per_million_input=0.05,
        cost_per_million_output=0.08,
        typical_latency_ms=120,
        capabilities=frozenset({
            ModelCapability.FAST,
            ModelCapability.STREAMING,
            ModelCapability.FUNCTION_CALLING,
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
