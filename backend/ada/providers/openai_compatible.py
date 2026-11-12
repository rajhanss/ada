"""OpenAI-compatible model adapter.

Used for:
- Groq (https://api.groq.com/openai/v1)
- OpenRouter (https://openrouter.ai/api/v1)
- Ollama (http://localhost:11434/v1)
- Local vLLM / llama.cpp / LM Studio
"""
from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx
import structlog

from ada.providers.base import (
    BaseModelAdapter,
    LLMMessage,
    LLMResponse,
    ModelSpec,
    TokenUsage,
)

logger = structlog.get_logger(__name__)


class OpenAICompatibleAdapter(BaseModelAdapter):
    """Generic adapter for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        spec: ModelSpec,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        default_headers: dict[str, str] | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        super().__init__(spec=spec, api_key=api_key, base_url=base_url)
        self.default_headers = default_headers or {}
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            **self.default_headers,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _format_messages(self, messages: list[LLMMessage]) -> list[dict[str, Any]]:
        formatted = []
        for msg in messages:
            entry: dict[str, Any] = {
                "role": msg.role,
                "content": msg.content,
            }
            if msg.name:
                entry["name"] = msg.name
            if msg.tool_calls:
                entry["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            formatted.append(entry)
        return formatted

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_schema: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model_id,
            "messages": self._format_messages(messages),
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools
        if response_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"schema": response_schema, "name": "output_schema"},
            }

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = int((time.perf_counter() - start) * 1000)
        choice = data["choices"][0]
        msg = choice.get("message", {})
        usage_raw = data.get("usage", {})

        p_tokens = usage_raw.get("prompt_tokens", 0)
        c_tokens = usage_raw.get("completion_tokens", 0)
        cost = (
            (p_tokens / 1_000_000.0) * self.spec.cost_per_million_input
            + (c_tokens / 1_000_000.0) * self.spec.cost_per_million_output
        )

        return LLMResponse(
            content=msg.get("content") or "",
            tool_calls=msg.get("tool_calls") or [],
            usage=TokenUsage(
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_tokens=p_tokens + c_tokens,
                estimated_cost_usd=cost,
            ),
            latency_ms=latency_ms,
            finish_reason=choice.get("finish_reason", "stop"),
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
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model_id,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            async with client.stream("POST", url, headers=self._headers(), json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        delta_content = delta.get("content")
                        if delta_content:
                            yield delta_content
                    except json.JSONDecodeError:
                        continue

    async def check_health(self) -> bool:
        """Ping the models endpoint."""
        url = f"{self.base_url.rstrip('/')}/models"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, headers=self._headers())
                return resp.status_code == 200
        except Exception:
            return False
