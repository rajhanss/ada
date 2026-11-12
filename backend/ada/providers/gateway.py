"""ADA Model Gateway — Dynamic multi-provider routing and fallback.

Routes requests according to task characteristics (latency, reasoning depth,
context window, cost, vision, local availability) defined in docs/MODEL_ROUTING.md.
Automatically cascades to fallbacks when primary providers fail or rate-limit.
"""
from __future__ import annotations

import time
from collections.abc import AsyncIterator
from typing import Any

import structlog

from ada.config import Settings, get_settings
from ada.providers.base import (
    BaseModelAdapter,
    LLMMessage,
    LLMResponse,
    ModelCapability,
    ModelSpec,
    TaskType,
    TokenUsage,
)
from ada.providers.gemini import GeminiAdapter
from ada.providers.groq import GROQ_MODELS, GroqAdapter
from ada.providers.ollama import OLLAMA_MODELS, OllamaAdapter
from ada.providers.openrouter import OPENROUTER_MODELS, OpenRouterAdapter

logger = structlog.get_logger(__name__)

# Standard Gemini model specs
GEMINI_MODELS: dict[str, ModelSpec] = {
    "gemini-2.0-flash": ModelSpec(
        model_id="gemini-2.0-flash",
        provider="gemini",
        display_name="Gemini 2.0 Flash",
        context_window=1_048_576,
        cost_per_million_input=0.10,
        cost_per_million_output=0.40,
        typical_latency_ms=400,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
            ModelCapability.FAST,
        }),
    ),
    "gemini-2.5-pro": ModelSpec(
        model_id="gemini-2.5-pro",
        provider="gemini",
        display_name="Gemini 2.5 Pro",
        context_window=2_097_152,
        cost_per_million_input=1.25,
        cost_per_million_output=5.00,
        typical_latency_ms=1500,
        capabilities=frozenset({
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.CODE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING,
        }),
    ),
}


class MockFallbackAdapter(BaseModelAdapter):
    """Deterministic fallback adapter when no external API keys are configured."""

    def __init__(self) -> None:
        spec = ModelSpec(
            model_id="mock-fallback",
            provider="mock",
            display_name="Mock Local Adapter",
            context_window=32_000,
            cost_per_million_input=0.0,
            cost_per_million_output=0.0,
            typical_latency_ms=10,
            capabilities=frozenset({
                ModelCapability.REASONING,
                ModelCapability.CODE,
                ModelCapability.VISION,
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.STREAMING,
                ModelCapability.FAST,
                ModelCapability.LOCAL,
            }),
            is_local=True,
        )
        super().__init__(spec=spec)

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_schema: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        import json
        last_msg = messages[-1].content if messages else ""
        sys_msg = messages[0].content if messages and messages[0].role == "system" else ""
        low = last_msg.lower()

        # If system prompt is asking for intent classification JSON
        if "intent" in sys_msg.lower() and "classifier" in sys_msg.lower():
            is_tool = any(w in low for w in ("run", "execute", "build", "create", "delete", "open", "read", "write", "fix", "test"))
            content = json.dumps({
                "intent": "action" if is_tool else "conversation",
                "requires_tools": is_tool,
                "summary": f"Classified intent: {last_msg[:50]}",
            })
        # If system prompt is asking for plan JSON
        elif "planner" in sys_msg.lower():
            # Extract tool name if specified
            tool_name = "run_dev_command"
            for t in ("read_file", "write_file", "delete_file", "list_directory", "web_search"):
                if t in low:
                    tool_name = t
                    break
            content = json.dumps({
                "goal": last_msg,
                "steps": [
                    {
                        "description": f"Execute {last_msg}",
                        "tool_name": tool_name,
                        "tool_args": {"path": "/workspace/main.py"} if "file" in tool_name else {"command": last_msg},
                        "verification_criteria": "Operation completed successfully",
                    }
                ]
            })
        else:
            content = f"ADA [Mock Response]: Processed intent for: '{last_msg[:100]}'."

        return LLMResponse(
            content=content,
            tool_calls=[],
            usage=TokenUsage(prompt_tokens=10, completion_tokens=15, total_tokens=25),
            latency_ms=5,
            finish_reason="stop",
            model_used=self.model_id,
            provider_used=self.provider,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        words = ["ADA:", "Processed", "offline", "mock", "stream."]
        for w in words:
            yield w + " "

    async def check_health(self) -> bool:
        return True


class ModelGateway:
    """Central gateway for model selection, routing, execution, and fallbacks."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._adapters: dict[str, BaseModelAdapter] = {}
        self._mock_fallback = MockFallbackAdapter()
        self._init_adapters()

    def _init_adapters(self) -> None:
        # 1. Gemini models
        gemini_key = self.settings.google_api_key or self.settings.gemini_api_key
        if gemini_key:
            for spec in GEMINI_MODELS.values():
                self._adapters[spec.model_id] = GeminiAdapter(
                    spec=spec,
                    api_key=gemini_key,
                )

        # 2. Groq models
        if self.settings.groq_api_key:
            for spec in GROQ_MODELS.values():
                self._adapters[spec.model_id] = GroqAdapter(
                    spec=spec,
                    api_key=self.settings.groq_api_key,
                )

        # 3. OpenRouter models
        if self.settings.openrouter_api_key:
            for spec in OPENROUTER_MODELS.values():
                self._adapters[spec.model_id] = OpenRouterAdapter(
                    spec=spec,
                    api_key=self.settings.openrouter_api_key,
                )

        # 4. Ollama local models (registered if ollama URL configured)
        for spec in OLLAMA_MODELS.values():
            self._adapters[spec.model_id] = OllamaAdapter(
                spec=spec,
                base_url=f"{self.settings.ollama_base_url.rstrip('/')}/v1",
                timeout_seconds=0.3,  # Fail fast when local Ollama is not running
            )

    @property
    def registered_models(self) -> list[str]:
        return list(self._adapters.keys())

    def get_adapter(self, model_id: str) -> BaseModelAdapter | None:
        return self._adapters.get(model_id)

    def route_candidates(
        self,
        task_type: TaskType,
        require_capabilities: set[ModelCapability] | None = None,
        prefer_local: bool = False,
    ) -> list[BaseModelAdapter]:
        """Return an ordered candidate list of adapters for a specific task type."""
        require_caps = set(require_capabilities or set())

        # Define priority model chains per task type
        priority_chains: dict[TaskType, list[str]] = {
            TaskType.CLASSIFICATION: [
                "llama-3.1-8b-instant",
                "gemini-2.0-flash",
                "llama-3.3-70b-versatile",
                "qwen2.5:7b",
            ],
            TaskType.FAST_RESPONSE: [
                "llama-3.1-8b-instant",
                "gemini-2.0-flash",
                "llama-3.3-70b-versatile",
            ],
            TaskType.PLANNING: [
                "gemini-2.5-pro",
                "anthropic/claude-3.7-sonnet",
                "gemini-2.0-flash",
                "llama-3.3-70b-versatile",
                "qwen2.5:7b",
            ],
            TaskType.CODING: [
                "gemini-2.5-pro",
                "qwen/qwen-2.5-coder-32b-instruct",
                "gemini-2.0-flash",
                "anthropic/claude-3.7-sonnet",
                "qwen2.5:7b",
            ],
            TaskType.VISION: [
                "gemini-2.0-flash",
                "gemini-2.5-pro",
                "anthropic/claude-3.7-sonnet",
            ],
            TaskType.CONVERSATION: [
                "gemini-2.0-flash",
                "llama-3.3-70b-versatile",
                "qwen2.5:7b",
            ],
            TaskType.SUMMARIZATION: [
                "gemini-2.0-flash",
                "llama-3.3-70b-versatile",
                "qwen2.5:7b",
            ],
        }

        chain = priority_chains.get(task_type, ["gemini-2.0-flash"])
        candidates: list[BaseModelAdapter] = []

        if prefer_local:
            # Place local models first
            for mid, adapter in self._adapters.items():
                if adapter.spec.is_local and require_caps.issubset(adapter.spec.capabilities):
                    candidates.append(adapter)

        for model_id in chain:
            adapter = self._adapters.get(model_id)
            if adapter and adapter not in candidates:
                if require_caps.issubset(adapter.spec.capabilities):
                    candidates.append(adapter)

        # Fallback to any registered adapter that satisfies required capabilities
        if not candidates:
            for adapter in self._adapters.values():
                if require_caps.issubset(adapter.spec.capabilities):
                    candidates.append(adapter)

        # Always include mock fallback as the ultimate safety net
        candidates.append(self._mock_fallback)
        return candidates

    async def generate(
        self,
        task_type: TaskType,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_schema: dict[str, Any] | None = None,
        require_capabilities: set[ModelCapability] | None = None,
        prefer_local: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        """Route and execute generation across priority candidates with automatic fallback."""
        candidates = self.route_candidates(
            task_type=task_type,
            require_capabilities=require_capabilities,
            prefer_local=prefer_local,
        )

        last_error: Exception | None = None
        for adapter in candidates:
            try:
                logger.info(
                    "Executing generation via model adapter",
                    model_id=adapter.model_id,
                    provider=adapter.provider,
                    task_type=task_type.value,
                )
                response = await adapter.generate(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                    response_schema=response_schema,
                    **kwargs,
                )
                return response
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Model adapter call failed, cascading to fallback",
                    model_id=adapter.model_id,
                    provider=adapter.provider,
                    error=str(exc),
                )
                continue

        # If somehow all candidates fail including mock
        logger.error("All model candidates exhausted", error=str(last_error))
        return LLMResponse(
            content=f"ADA was unable to reach intelligence providers. Last error: {last_error}",
            finish_reason="error",
            model_used="none",
            provider_used="none",
        )


# Global singleton instance
_gateway: ModelGateway | None = None


def get_model_gateway() -> ModelGateway:
    global _gateway
    if _gateway is None:
        _gateway = ModelGateway()
    return _gateway
