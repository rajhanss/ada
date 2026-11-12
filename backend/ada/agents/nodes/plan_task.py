"""Task planning node for ADA.

Deconstructs an action or multi-step request into a sequence of concrete,
verifiable steps with explicit tool calls and verification criteria.
"""
from __future__ import annotations

import json
from typing import Any
import uuid

import structlog

from ada.agents.state import AgentPlan, AgentState, AgentStep
from ada.providers.base import LLMMessage, TaskType
from ada.providers.gateway import get_model_gateway

logger = structlog.get_logger(__name__)

PLANNER_PROMPT = """You are ADA's Task Planner.
Break down the user's request into a clean, minimal list of concrete tool steps.
For each step, specify:
1. "description": What this step does.
2. "tool_name": One of [read_file, write_file, delete_file, list_directory, search_codebase, run_dev_command, web_search, fetch_url, browser_navigate, launch_app].
3. "tool_args": JSON dictionary of tool parameters.
4. "verification_criteria": How the verifier will confirm success (e.g., "file exists and contains updated function", "command returns exit code 0").

Respond strictly in valid JSON:
{
  "goal": "High-level goal description",
  "steps": [
    {
      "description": "...",
      "tool_name": "...",
      "tool_args": {},
      "verification_criteria": "..."
    }
  ]
}
"""


async def plan_task_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Plan task execution."""
    current_input = state.get("current_input") or ""
    gateway = get_model_gateway()

    messages = [
        LLMMessage(role="system", content=PLANNER_PROMPT),
        LLMMessage(role="user", content=f"Plan this request: '{current_input}'"),
    ]

    try:
        response = await gateway.generate(
            task_type=TaskType.PLANNING,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
        )

        content = response.content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        data = json.loads(content)
        raw_steps = data.get("steps", [])
        goal = data.get("goal", current_input)

        steps: list[AgentStep] = []
        for s in raw_steps:
            steps.append(
                AgentStep(
                    step_id=str(uuid.uuid4())[:8],
                    description=s.get("description", "Execute step"),
                    tool_name=s.get("tool_name", "run_dev_command"),
                    tool_args=s.get("tool_args", {}),
                    target_device_id=state.get("device_id"),
                    verification_criteria=s.get("verification_criteria", "Exit code 0"),
                    status="pending",
                    result=None,
                    error=None,
                )
            )

        if not steps:
            # Fallback single step
            steps.append(
                AgentStep(
                    step_id="step-1",
                    description=f"Execute: {current_input}",
                    tool_name="run_dev_command",
                    tool_args={"command": current_input},
                    target_device_id=state.get("device_id"),
                    verification_criteria="Execution complete",
                    status="pending",
                )
            )

    except Exception as exc:
        logger.warning("Planning failed, falling back to direct tool execution", error=str(exc))
        goal = current_input
        steps = [
            AgentStep(
                step_id="step-1",
                description=f"Action: {current_input}",
                tool_name="run_dev_command",
                tool_args={"command": current_input},
                target_device_id=state.get("device_id"),
                verification_criteria="Execution finished",
                status="pending",
            )
        ]

    plan: AgentPlan = {
        "task_id": str(uuid.uuid4()),
        "goal": goal,
        "steps": steps,
        "current_index": 0,
        "is_complete": False,
    }

    current_step = steps[0] if steps else None

    logger.info("Planned task", goal=goal, total_steps=len(steps))
    return {
        "plan": plan,
        "current_step": current_step,
    }
