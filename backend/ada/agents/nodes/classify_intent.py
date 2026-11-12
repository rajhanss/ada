"""Intent classification node for ADA.

Quickly determines whether the user request is:
- A conversation / conversational question (no tools)
- An informative guidance inquiry (no tools)
- A single action request (run a command, read a file, open an app)
- A multi-step autonomous task (build, test, research, refactor)
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from ada.agents.state import AgentState
from ada.providers.base import LLMMessage, TaskType
from ada.providers.gateway import get_model_gateway

logger = structlog.get_logger(__name__)

INTENT_SYSTEM_PROMPT = """You are the intent classifier for ADA (Autonomous Digital Assistant).
Analyze the user's latest input and classify the intent.

Respond strictly in valid JSON with:
{
  "intent": "conversation" | "question" | "action" | "multi_step_task",
  "requires_tools": boolean,
  "summary": "1-sentence summary of the request"
}

Guidelines:
- "conversation": Greetings, chit-chat, personal updates ("Hi ADA", "Thanks").
- "question": Pure information lookup or questions about concepts ("How does asyncio work?").
- "action": Single immediate tool request ("Read file config.py", "Run the test suite", "Open Chrome").
- "multi_step_task": Complex tasks requiring sequential steps, planning, and verification ("Inspect my project, fix failing tests and verify").
"""


async def classify_intent_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Classify user intent."""
    current_input = state.get("current_input") or ""
    if not current_input and state.get("messages"):
        last_msg = state["messages"][-1]
        current_input = last_msg.get("content", "")

    gateway = get_model_gateway()

    messages = [
        LLMMessage(role="system", content=INTENT_SYSTEM_PROMPT),
        LLMMessage(role="user", content=current_input),
    ]

    try:
        response = await gateway.generate(
            task_type=TaskType.CLASSIFICATION,
            messages=messages,
            temperature=0.1,
            max_tokens=150,
        )

        content = response.content.strip()
        # Clean potential markdown fences
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        data = json.loads(content)
        intent = data.get("intent", "conversation")
        requires_tools = bool(data.get("requires_tools", False))
    except Exception as exc:
        logger.warning("Intent classification parse failed, defaulting to conversation", error=str(exc))
        # Simple heuristic fallback
        low = current_input.lower()
        if any(w in low for w in ("run", "execute", "build", "create", "delete", "open", "read", "write", "fix", "test")):
            intent = "action"
            requires_tools = True
        else:
            intent = "conversation"
            requires_tools = False

    logger.info("Classified intent", intent=intent, requires_tools=requires_tools)
    return {
        "intent": intent,
        "requires_tools": requires_tools,
        "current_input": current_input,
    }
