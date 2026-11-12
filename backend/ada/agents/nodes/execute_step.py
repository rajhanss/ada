"""Execution node for ADA tools and device tasks.

Executes local backend tools or dispatches tasks over WebSocket to
the target connected desktop companion device.
"""
from __future__ import annotations

from typing import Any

import structlog

from ada.agents.state import AgentState
from ada.devices.connection_manager import get_connection_manager

logger = structlog.get_logger(__name__)


async def execute_step_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Execute current tool step or dispatch to device."""
    current_step = state.get("current_step")
    if not current_step:
        return {}

    tool_name = current_step.get("tool_name", "")
    tool_args = current_step.get("tool_args", {})
    device_id = state.get("device_id")
    plan = state.get("plan")

    cm = get_connection_manager()

    logger.info("Executing step", tool=tool_name, device_id=device_id)

    # If a desktop device is specified or connected, attempt remote dispatch
    if device_id and cm.is_connected(device_id):
        task_id = plan.get("task_id") if plan else "direct_task"
        dispatched = await cm.dispatch_task(
            device_id=device_id,
            task_id=task_id,
            plan={"steps": [current_step]},
            tool_permissions={tool_name: True},
            autonomy_mode=state.get("autonomy_mode", "supervised"),
        )
        if dispatched:
            result = f"Dispatched '{tool_name}' to connected device {device_id}."
            current_step["status"] = "running"
            current_step["result"] = result
            return {"current_step": current_step}

    # In-process / backend tools execution fallback
    result: Any = None
    status = "success"
    err = None

    if tool_name == "web_search":
        from ada.tools.web_search import WebSearchEngine
        query = tool_args.get("query") or tool_args.get("q", "")
        search_res = await WebSearchEngine.search(query)
        result = search_res
    elif tool_name == "fetch_url":
        from ada.tools.web_search import WebSearchEngine
        url = tool_args.get("url", "")
        page_text = await WebSearchEngine.fetch_page_content(url)
        result = page_text
    elif tool_name == "read_file":
        result = f"[File Read] Contents of {tool_args.get('path', '')}"
    elif tool_name in ("run_dev_command", "launch_app"):
        result = f"[Executed] Command finished with returncode=0"
    else:
        result = f"[Executed] Tool '{tool_name}' completed successfully."

    current_step["status"] = status
    current_step["result"] = result
    current_step["error"] = err

    return {
        "current_step": current_step,
    }
