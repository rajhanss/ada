"""Base abstractions for LLM providers in ADA's Model Gateway.

Every LLM provider (Gemini, Groq, OpenRouter, Ollama) implements
BaseModelAdapter. The gateway routes requests based on task requirements,
tracks costs and latencies, and handles fallbacks automatically.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModelCapability(str, Enum):
    """Capabilities supported by models."""
    REASONING = "reasoning"
    VISION = "vision"
    CODE = "code"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    FAST = "fast"
    LOCAL = "local"


class TaskType(str, Enum):
    """Categories of tasks routed by the Model Gateway."""
    CLASSIFICATION = "classification"       # ultra-low latency, intent routing
    PLANNING = "planning"                   # deep reasoning, multi-step graphs
    CODING = "coding"                       # code synthesis, diffing, dev tools
    VISION = "vision"                       # screen understanding, OCR, layout
    CONVERSATION = "conversation"           # natural companion interaction
    SUMMARIZATION = "summarization"         # memory distillation, reports
    FAST_RESPONSE = "fast_response"         # instant voice or UI acknowledgment


@dataclass(frozen=True)
class ModelSpec:
    """Specification and telemetry profile for a model."""
    model_id: str
    provider: str                           # "gemini", "groq", "openrouter", "ollama"
    display_name: str
    context_window: int
    cost_per_million_input: float           # USD ($0.0 for local/free)
    cost_per_million_output: float          # USD
    typical_latency_ms: int
    capabilities: frozenset[ModelCapability] = frozenset()
    is_local: bool = False
    is_active: bool = True

    def supports(self, capability: ModelCapability) -> bool:
        return capability in self.capabilities


@dataclass
class LLMMessage:
    """Universal message structure across all providers."""
    role: str                               # "system", "user", "assistant", "tool"
    content: str
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    images: list[bytes] = field(default_factory=list)  # Base64 or raw image bytes for vision


@dataclass
class TokenUsage:
    """Token telemetry for billing and performance tracking."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class LLMResponse:
    """Normalized response from any model provider."""
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    usage: TokenUsage = field(default_factory=TokenUsage)
    latency_ms: int = 0
    finish_reason: str = "stop"
    model_used: str = ""
    provider_used: str = ""


class BaseModelAdapter(ABC):
    """Abstract base class for all LLM provider adapters."""

    def __init__(self, spec: ModelSpec, api_key: str | None = None, base_url: str | None = None) -> None:
        self.spec = spec
        self.api_key = api_key
        self.base_url = base_url

    @property
    def model_id(self) -> str:
        return self.spec.model_id

    @property
    def provider(self) -> str:
        return self.spec.provider

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_schema: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a complete response from the model."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream response tokens as they arrive."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the provider endpoint is reachable and authorized."""
        pass
