"""Memory update node for ADA.

Distills conversation or task outcomes into persistent memories
(e.g., user preferences, project paths, successful workflows).
"""
from __future__ import annotations

from typing import Any

import structlog

from ada.agents.state import AgentState

logger = structlog.get_logger(__name__)


async def update_memory_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Extract and retain valuable facts/preferences."""
    plan = state.get("plan")
    user_id = state.get("user_id")

    memory_to_store = None
    if plan and plan.get("is_complete"):
        # Synthesize an episodic memory record
        memory_to_store = {
            "content": f"Successfully performed task: '{plan.get('goal')}'",
            "category": "task_history",
            "importance": 0.6,
            "confidence": 0.9,
            "user_id": user_id,
        }
        logger.info("Synthesized memory from completed task", user_id=user_id)

    return {
        "memory_to_store": memory_to_store,
    }
