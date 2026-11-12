"""Context retrieval node for ADA.

Fetches relevant user memories, device states, and active preferences
to contextualize the user's intent.
"""
from __future__ import annotations

from typing import Any

import structlog

from ada.agents.state import AgentState
from ada.devices.connection_manager import get_connection_manager

logger = structlog.get_logger(__name__)


async def retrieve_context_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Retrieve contextual memories and device status."""
    user_id = state.get("user_id", "")
    cm = get_connection_manager()

    # Discover connected devices for this user
    connected_ids = cm.connected_device_ids
    device_info: dict[str, Any] = {
        "connected_device_ids": connected_ids,
        "is_desktop_online": any("desktop" in d or "pc" in d for d in connected_ids) or len(connected_ids) > 0,
    }

    # In production, this queries pgvector semantic search or Supabase memories
    # For now, initialize mock relevant memories structure
    memories: list[dict[str, Any]] = state.get("retrieved_memories") or []

    logger.info(
        "Retrieved context for agent",
        user_id=user_id,
        connected_devices=len(connected_ids),
        memories_count=len(memories),
    )

    return {
        "device_context": device_info,
        "retrieved_memories": memories,
    }
