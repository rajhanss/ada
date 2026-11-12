"""Approvals API — user-facing approval of pending agent actions."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ada.auth.dependencies import get_current_user_id
from ada.models.domain import Approval, ApprovalStatus

router = APIRouter(tags=["approvals"])


@router.get("", response_model=list[Approval])
@router.get("/", response_model=list[Approval], include_in_schema=False)
async def list_approvals(
    user_id: str = Depends(get_current_user_id),
    status: ApprovalStatus | None = ApprovalStatus.PENDING,
) -> list[Approval]:
    """List approval requests, default to pending only."""
    # TODO: query Supabase approvals table
    return []


@router.get("/{approval_id}", response_model=Approval)
async def get_approval(
    approval_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Approval:
    raise HTTPException(status_code=404, detail="Approval not found")


@router.post("/{approval_id}/approve", status_code=200)
async def approve(
    approval_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Approve a pending action. The waiting task will resume execution."""
    # TODO: update approval status, signal waiting task via LangGraph
    raise HTTPException(status_code=404, detail="Approval not found")


@router.post("/{approval_id}/deny", status_code=200)
async def deny(
    approval_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Deny a pending action. The task will be marked failed or skipped."""
    raise HTTPException(status_code=404, detail="Approval not found")
