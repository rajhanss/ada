"""Task management API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ada.auth.dependencies import get_current_user_id
from ada.models.domain import Task, TaskCreate, TaskStatus, new_uuid, utcnow

router = APIRouter(tags=["tasks"])


@router.post("/", response_model=Task, status_code=201)
async def create_task(
    body: TaskCreate,
    user_id: str = Depends(get_current_user_id),
) -> Task:
    """Create a new task. The orchestrator will plan and execute it."""
    # TODO: persist to Supabase, dispatch to orchestrator
    task_id = new_uuid()
    now = utcnow()
    return Task(
        id=task_id,
        user_id=user_id,
        conversation_id=body.conversation_id,
        device_id=body.device_id,
        title=body.title,
        description=body.description,
        status=TaskStatus.CREATED,
        autonomy_mode=body.autonomy_mode,
        priority=body.priority,
        plan=None,
        current_step_id=None,
        result=None,
        error=None,
        idempotency_key=None,
        parent_task_id=None,
        created_at=now,
        updated_at=now,
        started_at=None,
        completed_at=None,
    )


@router.get("/", response_model=list[Task])
async def list_tasks(
    user_id: str = Depends(get_current_user_id),
    status: TaskStatus | None = None,
) -> list[Task]:
    """List tasks for the current user, optionally filtered by status."""
    # TODO: query Supabase
    return []


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Task:
    """Get a task by ID."""
    # TODO: fetch from Supabase, verify ownership
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/pause", response_model=Task)
async def pause_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Task:
    """Pause a running task."""
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/resume", response_model=Task)
async def resume_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Task:
    """Resume a paused task."""
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/cancel", response_model=Task)
async def cancel_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Task:
    """Cancel a task. Irreversible."""
    raise HTTPException(status_code=404, detail="Task not found")
