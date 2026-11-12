"""Agent state definition for LangGraph orchestrator.

Tracks the complete lifecycle:
Understand -> Contextualize -> Plan -> Authorize -> Execute -> Verify -> Remember
"""
from __future__ import annotations

from typing import Any, TypedDict


class AgentStep(TypedDict, total=False):
    step_id: str
    description: str
    tool_name: str
    tool_args: dict[str, Any]
    target_device_id: str | None
    verification_criteria: str
    status: str                         # "pending", "running", "success", "failed"
    result: Any
    error: str | None


class AgentPlan(TypedDict, total=False):
    task_id: str
    goal: str
    steps: list[AgentStep]
    current_index: int
    is_complete: bool


class AgentState(TypedDict, total=False):
    # Session / Identity
    user_id: str
    conversation_id: str
    device_id: str | None
    autonomy_mode: str                  # "conversation", "assisted", "supervised", "bounded"

    # User input & Conversation history
    messages: list[dict[str, Any]]
    current_input: str

    # Context & Memory
    retrieved_memories: list[dict[str, Any]]
    device_context: dict[str, Any]

    # Intent Classification
    intent: str                         # "conversation", "question", "action", "multi_step_task", "approval"
    requires_tools: bool

    # Planning & Execution
    plan: AgentPlan | None
    current_step: AgentStep | None
    requires_approval: bool
    approval_request: dict[str, Any] | None

    # Verification & Memory
    verification_passed: bool
    verification_notes: str | None
    memory_to_store: dict[str, Any] | None

    # Output
    final_response: str
    error: str | None
