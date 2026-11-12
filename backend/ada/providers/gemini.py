"""Google Gemini model adapter for ADA.

Direct HTTP implementation against Google's Generative Language API v1beta.
Supports text, structured JSON schemas, tool function declarations, multimodal vision,
and Server-Sent Events (SSE) streaming with minimal external dependency overhead.
"""
from __future__ import annotations

import base64
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

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiAdapter(BaseModelAdapter):
    """Adapter for Google Gemini models (2.0 Flash, 2.5 Pro, etc.)."""

    def __init__(
        self,
        spec: ModelSpec,
        api_key: str | None = None,
        timeout_seconds: float = 12.0,
    ) -> None:
        super().__init__(spec=spec, api_key=api_key, base_url=GEMINI_BASE_URL)
        self.timeout_seconds = timeout_seconds

    def _convert_messages(
        self, messages: list[LLMMessage]
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        """Convert universal LLMMessage list to Gemini system_instruction + contents."""
        system_instruction: dict[str, Any] | None = None
        contents: list[dict[str, Any]] = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = {"parts": [{"text": msg.content}]}
                continue

            role = "user" if msg.role in ("user", "tool") else "model"
            parts: list[dict[str, Any]] = []

            if msg.content:
                parts.append({"text": msg.content})

            # Vision images
            for img_bytes in msg.images:
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": b64,
                    }
                })

            if parts:
                contents.append({"role": role, "parts": parts})

        return system_instruction, contents

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_schema: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        model = self.model_id
        url = f"{self.base_url}/models/{model}:generateContent"
        params: dict[str, str] = {}
        if self.api_key:
            params["key"] = self.api_key

        system_instruction, contents = self._convert_messages(messages)

        gen_config: dict[str, Any] = {"temperature": temperature}
        if max_tokens:
            gen_config["maxOutputTokens"] = max_tokens
        if response_schema:
            gen_config["responseMimeType"] = "application/json"
            gen_config["responseSchema"] = response_schema

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": gen_config,
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        if tools:
            payload["tools"] = tools

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = int((time.perf_counter() - start) * 1000)

        # Parse Gemini response structure
        content = ""
        tool_calls: list[dict[str, Any]] = []
        candidates = data.get("candidates", [])
        finish_reason = "stop"

        if candidates:
            cand = candidates[0]
            finish_reason = cand.get("finishReason", "stop")
            cand_parts = cand.get("content", {}).get("parts", [])
            for p in cand_parts:
                if "text" in p:
                    content += p["text"]
                elif "functionCall" in p:
                    fc = p["functionCall"]
                    tool_calls.append({
                        "id": f"call_{len(tool_calls)}",
                        "type": "function",
                        "function": {
                            "name": fc.get("name"),
                            "arguments": json.dumps(fc.get("args", {})),
                        },
                    })

        usage_meta = data.get("usageMetadata", {})
        p_tokens = usage_meta.get("promptTokenCount", 0)
        c_tokens = usage_meta.get("candidatesTokenCount", 0)
        cost = (
            (p_tokens / 1_000_000.0) * self.spec.cost_per_million_input
            + (c_tokens / 1_000_000.0) * self.spec.cost_per_million_output
        )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            usage=TokenUsage(
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_tokens=p_tokens + c_tokens,
                estimated_cost_usd=cost,
            ),
            latency_ms=latency_ms,
            finish_reason=finish_reason,
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
        model = self.model_id
        url = f"{self.base_url}/models/{model}:streamGenerateContent"
        params: dict[str, str] = {"alt": "sse"}
        if self.api_key:
            params["key"] = self.api_key

        system_instruction, contents = self._convert_messages(messages)
        gen_config: dict[str, Any] = {"temperature": temperature}
        if max_tokens:
            gen_config["maxOutputTokens"] = max_tokens

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": gen_config,
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            async with client.stream("POST", url, params=params, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    try:
                        chunk = json.loads(data_str)
                        candidates = chunk.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for p in parts:
                                if "text" in p:
                                    yield p["text"]
                    except json.JSONDecodeError:
                        continue

    async def check_health(self) -> bool:
        if not self.api_key:
            return False
        url = f"{self.base_url}/models/{self.model_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, params={"key": self.api_key})
                return resp.status_code == 200
        except Exception:
            return False
