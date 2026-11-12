"""Unit tests for Model Gateway and Provider Routing."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from ada.config import Settings
from ada.providers.base import (
    LLMMessage,
    LLMResponse,
    ModelCapability,
    ModelSpec,
    TaskType,
    TokenUsage,
)
from ada.providers.gateway import MockFallbackAdapter, ModelGateway
from ada.providers.ollama import OllamaAdapter


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        environment="test",
        jwt_secret="test-secret-key-at-least-32-chars-long!",
        google_api_key="mock-google-key",
        groq_api_key="mock-groq-key",
        openrouter_api_key="mock-openrouter-key",
    )


class TestModelGatewayRouting:
    def test_all_providers_registered_with_keys(self, mock_settings: Settings):
        gw = ModelGateway(settings=mock_settings)
        models = gw.registered_models
        # Should include gemini, groq, openrouter, and ollama models
        assert "gemini-2.0-flash" in models
        assert "llama-3.1-8b-instant" in models
        assert "anthropic/claude-3.7-sonnet" in models
        assert "qwen2.5:7b" in models

    def test_route_candidates_for_classification(self, mock_settings: Settings):
        gw = ModelGateway(settings=mock_settings)
        candidates = gw.route_candidates(TaskType.CLASSIFICATION)
        assert len(candidates) > 0
        # Fast groq model should be early in the candidate list
        model_ids = [c.model_id for c in candidates]
        assert "llama-3.1-8b-instant" in model_ids

    def test_route_candidates_for_planning(self, mock_settings: Settings):
        gw = ModelGateway(settings=mock_settings)
        candidates = gw.route_candidates(TaskType.PLANNING)
        model_ids = [c.model_id for c in candidates]
        assert "gemini-2.5-pro" in model_ids or "anthropic/claude-3.7-sonnet" in model_ids

    def test_route_candidates_requires_vision_filters_correctly(self, mock_settings: Settings):
        gw = ModelGateway(settings=mock_settings)
        candidates = gw.route_candidates(
            TaskType.VISION,
            require_capabilities={ModelCapability.VISION},
        )
        for c in candidates[:-1]:  # exclude the mock fallback
            assert c.spec.supports(ModelCapability.VISION)

    def test_route_candidates_prefer_local(self, mock_settings: Settings):
        gw = ModelGateway(settings=mock_settings)
        candidates = gw.route_candidates(TaskType.CONVERSATION, prefer_local=True)
        # First candidate should be local
        assert candidates[0].spec.is_local

    def test_mock_fallback_always_present_at_end(self, mock_settings: Settings):
        gw = ModelGateway(settings=mock_settings)
        candidates = gw.route_candidates(TaskType.CODING)
        assert candidates[-1].model_id == "mock-fallback"


class TestMockFallbackAdapter:
    @pytest.mark.asyncio
    async def test_mock_fallback_generate(self):
        adapter = MockFallbackAdapter()
        messages = [LLMMessage(role="user", content="Hello ADA")]
        resp = await adapter.generate(messages)
        assert isinstance(resp, LLMResponse)
        assert "ADA [Mock Response]" in resp.content
        assert resp.model_used == "mock-fallback"
        assert resp.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_mock_fallback_stream(self):
        adapter = MockFallbackAdapter()
        messages = [LLMMessage(role="user", content="Hello ADA")]
        tokens = []
        async for token in adapter.stream(messages):
            tokens.append(token)
        assert len(tokens) > 0
        assert "".join(tokens).startswith("ADA: Processed")


class TestGatewayFallbackExecution:
    @pytest.mark.asyncio
    async def test_gateway_cascades_on_failure(self, mock_settings: Settings):
        gw = ModelGateway(settings=mock_settings)

        # Mock primary candidate to fail
        failing_adapter = AsyncMock()
        failing_adapter.model_id = "failing-model"
        failing_adapter.provider = "failing-provider"
        failing_adapter.spec = ModelSpec(
            model_id="failing-model",
            provider="test",
            display_name="Failer",
            context_window=4096,
            cost_per_million_input=0,
            cost_per_million_output=0,
            typical_latency_ms=10,
        )
        failing_adapter.generate.side_effect = RuntimeError("API Rate Limit exceeded 429")

        # Mock secondary to succeed
        success_adapter = AsyncMock()
        success_adapter.model_id = "success-model"
        success_adapter.provider = "fallback-provider"
        success_adapter.spec = ModelSpec(
            model_id="success-model",
            provider="test",
            display_name="Succeeder",
            context_window=4096,
            cost_per_million_input=0,
            cost_per_million_output=0,
            typical_latency_ms=10,
        )
        success_adapter.generate.return_value = LLMResponse(
            content="Fallback succeeded",
            finish_reason="stop",
            model_used="success-model",
            provider_used="fallback-provider",
        )

        with patch.object(gw, "route_candidates", return_value=[failing_adapter, success_adapter]):
            resp = await gw.generate(
                task_type=TaskType.CONVERSATION,
                messages=[LLMMessage(role="user", content="Test")],
            )
            assert resp.content == "Fallback succeeded"
            assert resp.model_used == "success-model"
            assert failing_adapter.generate.call_count == 1
            assert success_adapter.generate.call_count == 1
