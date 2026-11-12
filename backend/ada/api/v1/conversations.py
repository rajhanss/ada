"""Conversations API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ada.auth.dependencies import get_current_user_id
from ada.models.domain import (
    Conversation, ConversationCreate,
    Message, MessageSend,
    new_uuid, utcnow,
)

router = APIRouter(tags=["conversations"])


@router.post("/", response_model=Conversation, status_code=201)
async def create_conversation(
    body: ConversationCreate,
    user_id: str = Depends(get_current_user_id),
) -> Conversation:
    from ada.db.repositories.conversations import ConversationRepository
    repo = ConversationRepository()
    record = await repo.create(user_id=user_id, title=body.title)
    return Conversation(
        id=record["id"],
        user_id=user_id,
        device_id=body.device_id,
        title=record["title"],
        summary=None,
        is_archived=False,
        created_at=record["created_at"],
        updated_at=record["updated_at"],
    )


@router.get("/", response_model=list[Conversation])
async def list_conversations(
    user_id: str = Depends(get_current_user_id),
) -> list[Conversation]:
    from ada.db.repositories.conversations import ConversationRepository
    repo = ConversationRepository()
    records = await repo.list_for_user(user_id)
    return [
        Conversation(
            id=r["id"],
            user_id=r["user_id"],
            device_id=r.get("device_id"),
            title=r["title"],
            summary=r.get("summary"),
            is_archived=r.get("is_archived", False),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in records
    ]


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Conversation:
    from ada.db.repositories.conversations import ConversationRepository
    repo = ConversationRepository()
    records = await repo.list_for_user(user_id)
    match = [r for r in records if r["id"] == conversation_id]
    if not match:
        raise HTTPException(status_code=404, detail="Conversation not found")
    r = match[0]
    return Conversation(
        id=r["id"],
        user_id=r["user_id"],
        device_id=r.get("device_id"),
        title=r["title"],
        summary=r.get("summary"),
        is_archived=r.get("is_archived", False),
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


@router.post("/{conversation_id}/messages", response_model=Message, status_code=201)
async def send_message(
    conversation_id: str,
    body: MessageSend,
    user_id: str = Depends(get_current_user_id),
) -> Message:
    """Send a message. The LangGraph orchestrator processes it and returns the response."""
    from ada.agents.orchestrator import get_orchestrator
    from ada.agents.state import AgentState
    from ada.db.repositories.conversations import ConversationRepository
    from ada.models.domain import MessageRole

    repo = ConversationRepository()

    # 1. Save user message
    await repo.add_message(
        conversation_id=conversation_id,
        role="user",
        content=body.content,
    )

    # 2. Retrieve recent message history
    history = await repo.get_messages(conversation_id)

    # 3. Invoke LangGraph Orchestrator
    graph = get_orchestrator()
    agent_state: AgentState = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "device_id": None,
        "autonomy_mode": "supervised",
        "current_input": body.content,
        "messages": [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in history
        ],
    }

    result = await graph.ainvoke(agent_state)
    assistant_content = result.get("final_response") or "I have processed your request."

    # 4. Save assistant message
    metadata: dict[str, Any] = {
        "intent": result.get("intent"),
        "requires_tools": result.get("requires_tools", False),
        "requires_approval": result.get("requires_approval", False),
    }
    if result.get("approval_request"):
        metadata["approval_request"] = result["approval_request"]

    await repo.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_content,
        metadata=metadata,
    )

    now = utcnow()
    return Message(
        id=new_uuid(),
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=assistant_content,
        content_type="text",
        tool_name=None,
        tool_call_id=None,
        metadata=metadata,
        model_provider=None,
        model_id=None,
        input_tokens=None,
        output_tokens=None,
        created_at=now,
    )


@router.get("/{conversation_id}/messages", response_model=list[Message])
async def list_messages(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
) -> list[Message]:
    from ada.db.repositories.conversations import ConversationRepository
    from ada.models.domain import MessageRole
    repo = ConversationRepository()
    records = await repo.get_messages(conversation_id)
    return [
        Message(
            id=r["id"],
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole(r.get("role", "assistant")),
            content=r["content"],
            content_type="text",
            metadata=r.get("metadata", {}),
            created_at=r["created_at"],
        )
        for r in records
    ]
