"""OpenRouter provider adapter.

Provides access to diverse top-tier models (Claude 3.7 Sonnet, GPT-4o,
DeepSeek-R1, Qwen 2.5 Coder) as fallbacks and specialized reasoning tasks.
"""
from __future__ import annotations

from ada.providers.base import ModelCapability, ModelSpec
from ada.providers.openai_compatible import OpenAICompatibleAdapter

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

OPENROUTER_MODELS: dict[str, ModelSpec] = {
    "anthropic/claude-3.7-sonnet": ModelSpec(
        model_id="anthropic/claude-3.7-sonnet",
        provider="openrouter",
        display_name="Claude 3.7 Sonnet",
        context_window=200_000,
        cost_per_million_input=3.0,
        cost_per_million_output=15.0,
        typical_latency_ms=1200,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.CODE,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
        }),
    ),
    "deepseek/deepseek-r1": ModelSpec(
        model_id="deepseek/deepseek-r1",
        provider="openrouter",
        display_name="DeepSeek R1",
        context_window=64_000,
        cost_per_million_input=0.55,
        cost_per_million_output=2.19,
        typical_latency_ms=2500,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.CODE,
            ModelCapability.STREAMING,
        }),
    ),
    "qwen/qwen-2.5-coder-32b-instruct": ModelSpec(
        model_id="qwen/qwen-2.5-coder-32b-instruct",
        provider="openrouter",
        display_name="Qwen 2.5 Coder 32B",
        context_window=32_000,
        cost_per_million_input=0.07,
        cost_per_million_output=0.16,
        typical_latency_ms=600,
        capabilities=frozenset({
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.FAST,
        }),
    ),
}


class OpenRouterAdapter(OpenAICompatibleAdapter):
    """Adapter for OpenRouter API with app attribution headers."""

    def __init__(
        self,
        spec: ModelSpec,
        api_key: str | None = None,
        timeout_seconds: float = 90.0,
    ) -> None:
        super().__init__(
            spec=spec,
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://ada.local",
                "X-Title": "ADA - Autonomous Digital Assistant",
            },
            timeout_seconds=timeout_seconds,
        )
