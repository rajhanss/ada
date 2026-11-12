"""ADA domain models — single source of truth for all Pydantic schemas.

These models are used by the API layer, service layer, and agent workflows.
They mirror the database schema in DATABASE_SCHEMA.md.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class AutonomyMode(str, Enum):
    CONVERSATION = "conversation"
    ASSISTED = "assisted"
    SUPERVISED = "supervised_execution"
    BOUNDED = "bounded_autonomy"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    WEB = "web"


class ConnectionState(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"


class TaskStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    PENDING_APPROVAL = "pending_approval"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    VERIFYING = "verifying"
    RECOVERING = "recovering"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryType(str, Enum):
    PROFILE = "profile"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"


class ModelCapability(str, Enum):
    CHAT = "chat"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    CODE = "code"
    REASONING = "reasoning"
    EMBEDDINGS = "embeddings"
    STT = "stt"
    TTS = "tts"
    SEARCH = "search"
    LOCAL = "local"


class ProviderHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    PLANNER = "planner"
    RESEARCH = "research"
    COMPUTER = "computer"
    CODING = "coding"
    SYSTEM = "system"
    MEMORY = "memory"
    ANALYST = "analyst"
    VERIFIER = "verifier"


class VerificationStatus(str, Enum):
    VERIFIED_SUCCESS = "verified_success"
    PARTIAL_SUCCESS = "partial_success"
    UNVERIFIED = "unverified"
    FAILED = "failed"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


class ProfileCreate(BaseModel):
    display_name: str | None = None
    timezone: str = "UTC"
    language: str = "en"
    autonomy_mode: AutonomyMode = AutonomyMode.SUPERVISED


class Profile(BaseModel):
    id: str
    user_id: str
    display_name: str | None
    avatar_url: str | None
    timezone: str
    language: str
    autonomy_mode: AutonomyMode
    preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------


class DeviceRegister(BaseModel):
    device_type: DeviceType
    display_name: str
    platform: str | None = None
    app_version: str | None = None
    capabilities: list[str] = Field(default_factory=list)

    @field_validator("display_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("display_name must not be empty")
        return v.strip()


class DeviceRegistered(BaseModel):
    """Returned once at registration. device_token is not stored after this."""
    device_id: str
    device_token: str   # raw token — store in Keystore/Credential Manager
    expires_at: datetime


class Device(BaseModel):
    id: str
    user_id: str
    device_type: DeviceType
    display_name: str
    app_version: str | None
    platform: str | None
    capabilities: list[str]
    permission_profile: dict[str, Any]
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime


class DeviceSession(BaseModel):
    id: str
    device_id: str
    user_id: str
    expires_at: datetime
    revoked_at: datetime | None
    connection_state: ConnectionState
    created_at: datetime
    last_ping_at: datetime | None


# ---------------------------------------------------------------------------
# Conversation & Message
# ---------------------------------------------------------------------------


class ConversationCreate(BaseModel):
    title: str | None = None
    device_id: str | None = None


class Conversation(BaseModel):
    id: str
    user_id: str
    device_id: str | None
    title: str | None
    summary: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class MessageSend(BaseModel):
    content: str
    content_type: str = "text"
    device_id: str | None = None


class Message(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    role: MessageRole
    content: str | None
    content_type: str
    tool_name: str | None
    tool_call_id: str | None
    metadata: dict[str, Any]
    model_provider: str | None
    model_id: str | None
    input_tokens: int | None
    output_tokens: int | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    device_id: str | None = None
    conversation_id: str | None = None
    autonomy_mode: AutonomyMode = AutonomyMode.SUPERVISED
    priority: int = Field(default=50, ge=0, le=100)


class TaskStep(BaseModel):
    id: str
    task_id: str
    user_id: str
    step_index: int
    agent_role: AgentRole
    description: str
    status: StepStatus
    tool_calls: list[dict[str, Any]]
    result: dict[str, Any] | None
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class TaskEvent(BaseModel):
    id: str
    task_id: str
    user_id: str
    device_id: str | None
    event_type: str
    payload: dict[str, Any]
    acknowledged: bool
    created_at: datetime


class Task(BaseModel):
    id: str
    user_id: str
    conversation_id: str | None
    device_id: str | None
    title: str
    description: str | None
    status: TaskStatus
    autonomy_mode: AutonomyMode
    priority: int
    plan: dict[str, Any] | None
    current_step_id: str | None
    result: dict[str, Any] | None
    error: str | None
    idempotency_key: str | None
    parent_task_id: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


# ---------------------------------------------------------------------------
# Approval
# ---------------------------------------------------------------------------


class ApprovalCreate(BaseModel):
    task_id: str
    step_id: str | None = None
    prompt: str
    tool_name: str | None = None
    tool_args: dict[str, Any] | None = None
    risk_level: RiskLevel = RiskLevel.MEDIUM


class Approval(BaseModel):
    id: str
    task_id: str
    user_id: str
    step_id: str | None
    prompt: str
    tool_name: str | None
    tool_args: dict[str, Any] | None
    risk_level: RiskLevel
    status: ApprovalStatus
    decision_at: datetime | None
    expires_at: datetime
    created_at: datetime


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------


class MemoryCreate(BaseModel):
    memory_type: MemoryType
    content: str
    summary: str | None = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    source: str | None = None
    source_id: str | None = None
    tags: list[str] = Field(default_factory=list)


class Memory(BaseModel):
    id: str
    user_id: str
    memory_type: MemoryType
    content: str
    summary: str | None
    importance: float
    confidence: float
    source: str | None
    source_id: str | None
    tags: list[str]
    is_deleted: bool
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Model Registry
# ---------------------------------------------------------------------------


class ModelProvider(BaseModel):
    id: str
    name: str
    display_name: str
    base_url: str | None
    is_enabled: bool
    is_local: bool
    health_status: ProviderHealth
    last_health_check: datetime | None


class ModelRegistryEntry(BaseModel):
    id: str
    provider_id: str
    model_id: str
    display_name: str
    capabilities: list[ModelCapability]
    context_window: int | None
    max_output_tokens: int | None
    cost_per_1k_input_tokens: Decimal | None
    cost_per_1k_output_tokens: Decimal | None
    is_enabled: bool


# ---------------------------------------------------------------------------
# WebSocket message envelopes
# ---------------------------------------------------------------------------


class WSMessage(BaseModel):
    """Base envelope for all WebSocket messages."""
    id: str = Field(default_factory=new_uuid)
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskDispatch(BaseModel):
    """Sent from cloud to desktop to initiate local task execution."""
    task_id: str
    title: str
    plan: dict[str, Any]
    tool_permissions: dict[str, Any]
    autonomy_mode: AutonomyMode


class TaskEventReport(BaseModel):
    """Sent from desktop to cloud as task executes."""
    task_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# API response wrappers
# ---------------------------------------------------------------------------


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    cursor: str | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail
