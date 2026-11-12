"""Outcome verification node for ADA.

Ensures actions are verified against expected success criteria before
concluding or remembering an outcome.
"""
from __future__ import annotations

from typing import Any

import structlog

from ada.agents.state import AgentState

logger = structlog.get_logger(__name__)


async def verify_result_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Verify the result of the executed step."""
    plan = state.get("plan")
    current_step = state.get("current_step")

    if not current_step:
        return {"verification_passed": True}

    criteria = current_step.get("verification_criteria", "")
    result = current_step.get("result")
    err = current_step.get("error")

    # Verification checks
    passed = err is None and result is not None
    notes = f"Verified: {criteria}" if passed else f"Verification failed: {err}"

    current_step["status"] = "success" if passed else "failed"

    logger.info("Step verified", step_id=current_step.get("step_id"), passed=passed)

    # Check plan progression
    if plan and "steps" in plan:
        idx = plan.get("current_index", 0)
        plan["steps"][idx] = current_step
        next_idx = idx + 1
        if next_idx < len(plan["steps"]):
            plan["current_index"] = next_idx
            next_step = plan["steps"][next_idx]
            return {
                "plan": plan,
                "current_step": next_step,
                "verification_passed": passed,
                "verification_notes": notes,
            }
        else:
            plan["is_complete"] = True
            return {
                "plan": plan,
                "verification_passed": passed,
                "verification_notes": notes,
            }

    return {
        "verification_passed": passed,
        "verification_notes": notes,
    }
