"""Permission verification node for ADA.

CRITICAL ARCHITECTURE RULE:
Authorizations and security gates must run in deterministic Python code,
NEVER inside the LLM prompt. This node calls the Permission Engine.
"""
from __future__ import annotations

from typing import Any
import uuid

import structlog

from ada.agents.state import AgentState
from ada.models.domain import AutonomyMode
from ada.permissions.engine import PermissionContext, check_permission

logger = structlog.get_logger(__name__)


async def check_permissions_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Check permission for current step before execution."""
    current_step = state.get("current_step")
    if not current_step:
        return {"requires_approval": False}

    tool_name = current_step.get("tool_name", "")
    tool_args = current_step.get("tool_args", {})
    user_id = state.get("user_id", "default_user")
    device_id = state.get("device_id")

    raw_mode = state.get("autonomy_mode", "supervised")
    try:
        autonomy_mode = AutonomyMode(raw_mode)
    except ValueError:
        autonomy_mode = AutonomyMode.SUPERVISED

    ctx = PermissionContext(
        user_id=user_id,
        device_id=device_id,
        autonomy_mode=autonomy_mode,
        tool_name=tool_name,
        tool_args=tool_args,
    )

    perm_result = check_permission(ctx)

    if not perm_result.allowed:
        logger.warning(
            "Action denied by permission engine",
            tool=tool_name,
            reason=perm_result.reason,
            user_id=user_id,
        )
        return {
            "requires_approval": False,
            "error": f"Action '{tool_name}' was blocked: {perm_result.reason}",
            "final_response": f"I cannot execute '{tool_name}' because: {perm_result.reason}",
        }

    if perm_result.requires_approval:
        approval_id = str(uuid.uuid4())
        logger.info(
            "Action requires user approval",
            tool=tool_name,
            approval_id=approval_id,
            user_id=user_id,
        )
        approval_req = {
            "approval_id": approval_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "risk_level": perm_result.risk_level.value,
            "reason": perm_result.reason,
            "step_id": current_step.get("step_id"),
        }
        return {
            "requires_approval": True,
            "approval_request": approval_req,
            "final_response": (
                f"I need your approval to execute `{tool_name}`: {perm_result.reason}\n"
                f"Arguments: `{tool_args}`"
            ),
        }

    logger.info("Action pre-approved to run", tool=tool_name)
    return {
        "requires_approval": False,
        "approval_request": None,
    }
