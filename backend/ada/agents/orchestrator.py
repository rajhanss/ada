"""ADA LangGraph Orchestrator.

Implements the multi-turn stateful graph:
Understand -> Contextualize -> Plan -> Authorize -> Execute -> Verify -> Remember
"""
from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from ada.agents.nodes.check_permissions import check_permissions_node
from ada.agents.nodes.classify_intent import classify_intent_node
from ada.agents.nodes.direct_respond import direct_respond_node
from ada.agents.nodes.execute_step import execute_step_node
from ada.agents.nodes.plan_task import plan_task_node
from ada.agents.nodes.retrieve_context import retrieve_context_node
from ada.agents.nodes.update_memory import update_memory_node
from ada.agents.nodes.verify_result import verify_result_node
from ada.agents.state import AgentState


# Conditional routing functions
def route_after_intent(state: AgentState) -> Literal["retrieve_context", "direct_respond"]:
    if state.get("requires_tools", False):
        return "retrieve_context"
    return "direct_respond"


def route_after_permissions(state: AgentState) -> Literal["execute_step", "__end__"]:
    if state.get("requires_approval", False) or state.get("error"):
        return END
    return "execute_step"


def route_after_verify(state: AgentState) -> Literal["check_permissions", "direct_respond"]:
    plan = state.get("plan")
    if plan and not plan.get("is_complete", False):
        return "check_permissions"
    return "direct_respond"


def create_orchestrator_graph():
    """Build and compile the LangGraph agent orchestrator."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("plan_task", plan_task_node)
    workflow.add_node("check_permissions", check_permissions_node)
    workflow.add_node("execute_step", execute_step_node)
    workflow.add_node("verify_result", verify_result_node)
    workflow.add_node("direct_respond", direct_respond_node)
    workflow.add_node("update_memory", update_memory_node)

    # Connect Edges
    workflow.add_edge(START, "classify_intent")

    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "retrieve_context": "retrieve_context",
            "direct_respond": "direct_respond",
        },
    )

    workflow.add_edge("retrieve_context", "plan_task")
    workflow.add_edge("plan_task", "check_permissions")

    workflow.add_conditional_edges(
        "check_permissions",
        route_after_permissions,
        {
            "execute_step": "execute_step",
            END: END,
        },
    )

    workflow.add_edge("execute_step", "verify_result")

    workflow.add_conditional_edges(
        "verify_result",
        route_after_verify,
        {
            "check_permissions": "check_permissions",
            "direct_respond": "direct_respond",
        },
    )

    workflow.add_edge("direct_respond", "update_memory")
    workflow.add_edge("update_memory", END)

    return workflow.compile()


# Lazy-loaded compiled graph instance
_compiled_orchestrator = None


def get_orchestrator():
    global _compiled_orchestrator
    if _compiled_orchestrator is None:
        _compiled_orchestrator = create_orchestrator_graph()
    return _compiled_orchestrator
