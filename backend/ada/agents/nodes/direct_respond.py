"""Direct conversational response node for ADA.

Generates concise, intelligent responses for questions, guidance,
and conversational continuity using the Model Gateway.
"""
from __future__ import annotations

from typing import Any

import structlog

from ada.agents.state import AgentState
from ada.providers.base import LLMMessage, TaskType
from ada.providers.gateway import get_model_gateway

logger = structlog.get_logger(__name__)

ADA_PERSONA_PROMPT = """You are ADA (Autonomous Digital Assistant).
Tagline: "Your intelligence. Everywhere."

Personality:
- Intelligent, calm, and concise.
- Direct and clear. Never robotic.
- Never pretend to know something you do not know.
- If an action was performed, clearly state the outcome and verification result.
- Keep responses compact unless detailed technical depth is explicitly requested.
"""


async def direct_respond_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: Generate direct assistant response."""
    current_input = state.get("current_input") or ""
    history = state.get("messages", [])
    gateway = get_model_gateway()

    llm_messages: list[LLMMessage] = [
        LLMMessage(role="system", content=ADA_PERSONA_PROMPT)
    ]

    # Add conversation history
    for msg in history[-6:]:  # last 6 messages
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant", "system"):
            llm_messages.append(LLMMessage(role=role, content=content))

    # Add current context if available
    plan = state.get("plan")
    verification_passed = state.get("verification_passed")
    if plan and plan.get("is_complete"):
        status_note = "Plan completed successfully and verified." if verification_passed else "Plan completed with warnings."
        llm_messages.append(
            LLMMessage(
                role="system",
                content=f"Task status update: {status_note} Goal was: '{plan.get('goal')}'. Summarize the completed action for the user.",
            )
        )
    elif not any(m.role == "user" and m.content == current_input for m in llm_messages):
        llm_messages.append(LLMMessage(role="user", content=current_input))

    response = await gateway.generate(
        task_type=TaskType.CONVERSATION,
        messages=llm_messages,
        temperature=0.7,
        max_tokens=600,
    )

    final_text = response.content or "I have processed your request."
    logger.info("Generated direct response", length=len(final_text))

    return {
        "final_response": final_text,
    }
