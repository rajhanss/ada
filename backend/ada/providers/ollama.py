"""Local Ollama provider adapter for offline operation and sensitive tasks.

Default endpoint: http://localhost:11434/v1
Cost is always $0.00. Latency depends on local GPU (RTX 2050 / CPU).
"""
from __future__ import annotations

import httpx

from ada.providers.base import ModelCapability, ModelSpec
from ada.providers.openai_compatible import OpenAICompatibleAdapter

DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"

OLLAMA_MODELS: dict[str, ModelSpec] = {
    "qwen2.5:7b": ModelSpec(
        model_id="qwen2.5:7b",
        provider="ollama",
        display_name="Local Qwen 2.5 7B",
        context_window=32_000,
        cost_per_million_input=0.0,
        cost_per_million_output=0.0,
        typical_latency_ms=1800,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.CODE,
            ModelCapability.STREAMING,
            ModelCapability.LOCAL,
        }),
        is_local=True,
    ),
    "mistral-nemo:12b": ModelSpec(
        model_id="mistral-nemo:12b",
        provider="ollama",
        display_name="Local Mistral Nemo 12B",
        context_window=128_000,
        cost_per_million_input=0.0,
        cost_per_million_output=0.0,
        typical_latency_ms=2500,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.STREAMING,
            ModelCapability.LOCAL,
        }),
        is_local=True,
    ),
}


class OllamaAdapter(OpenAICompatibleAdapter):
    """Adapter for locally running Ollama instance."""

    def __init__(
        self,
        spec: ModelSpec,
        base_url: str = DEFAULT_OLLAMA_URL,
        timeout_seconds: float = 3.0,
    ) -> None:
        super().__init__(
            spec=spec,
            api_key=None,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )

    async def check_health(self) -> bool:
        """Ping local Ollama /api/tags or /v1/models."""
        try:
            host = self.base_url.replace("/v1", "")
            async with httpx.AsyncClient(timeout=0.5) as client:
                resp = await client.get(f"{host}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
