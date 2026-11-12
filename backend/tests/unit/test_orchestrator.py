"""Unit tests for LangGraph Agent Orchestrator."""
from __future__ import annotations

import pytest

from ada.agents.orchestrator import create_orchestrator_graph
from ada.agents.state import AgentState


@pytest.mark.asyncio
async def test_conversational_workflow():
    """A greeting or general question should route directly without requiring tools."""
    graph = create_orchestrator_graph()

    initial_state: AgentState = {
        "user_id": "test-user-1",
        "conversation_id": "conv-1",
        "autonomy_mode": "supervised",
        "current_input": "Hello ADA! How are you today?",
        "messages": [{"role": "user", "content": "Hello ADA! How are you today?"}],
    }

    result = await graph.ainvoke(initial_state)

    assert result["intent"] in ("conversation", "question")
    assert result["requires_tools"] is False
    assert result.get("final_response") is not None
    assert len(result["final_response"]) > 0
    assert result.get("requires_approval", False) is False


@pytest.mark.asyncio
async def test_action_requiring_approval_pauses_workflow():
    """A destructive tool like delete_file must pause at check_permissions with approval required."""
    graph = create_orchestrator_graph()

    initial_state: AgentState = {
        "user_id": "test-user-2",
        "conversation_id": "conv-2",
        "autonomy_mode": "bounded",
        "current_input": "delete_file /etc/hosts",
        "messages": [{"role": "user", "content": "delete_file /etc/hosts"}],
    }

    result = await graph.ainvoke(initial_state)

    assert result["requires_tools"] is True
    assert result.get("requires_approval") is True
    assert result.get("approval_request") is not None
    assert "delete" in result["approval_request"]["tool_name"] or "approval" in result["final_response"].lower()


@pytest.mark.asyncio
async def test_autonomous_action_in_bounded_mode():
    """A permitted read action should execute, verify, and complete without approval."""
    graph = create_orchestrator_graph()

    initial_state: AgentState = {
        "user_id": "test-user-3",
        "conversation_id": "conv-3",
        "autonomy_mode": "bounded",
        "current_input": "read_file /workspace/main.py",
        "messages": [{"role": "user", "content": "read_file /workspace/main.py"}],
    }

    result = await graph.ainvoke(initial_state)

    assert result["requires_tools"] is True
    assert result.get("requires_approval", False) is False
    assert result.get("verification_passed") is True
    assert result.get("plan") is not None
    assert result["plan"]["is_complete"] is True
    assert result.get("final_response") is not None
