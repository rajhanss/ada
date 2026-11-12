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
    now = utcnow()
    return Conversation(
        id=new_uuid(),
        user_id=user_id,
        device_id=body.device_id,
        title=body.title,
        summary=None,
        is_archived=False,
        created_at=now,
        updated_at=now,
    )


@router.get("/", response_model=list[Conversation])
async def list_conversations(
    user_id: str = Depends(get_current_user_id),
) -> list[Conversation]:
    return []


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Conversation:
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/{conversation_id}/messages", response_model=Message, status_code=201)
async def send_message(
    conversation_id: str,
    body: MessageSend,
    user_id: str = Depends(get_current_user_id),
) -> Message:
    """Send a message. The orchestrator processes it and returns the response."""
    # TODO: route through orchestrator, return streamed or single response
    from ada.models.domain import MessageRole
    now = utcnow()
    return Message(
        id=new_uuid(),
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content="ADA is not yet wired to the intelligence core. Stage B will connect this.",
        content_type="text",
        tool_name=None,
        tool_call_id=None,
        metadata={},
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
    return []
