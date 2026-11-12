"""Permission engine — enforces authorization OUTSIDE the LLM.

An LLM must NEVER grant itself permissions. This module is the
single enforcement point for all tool and action authorizations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

from ada.models.domain import AutonomyMode, RiskLevel

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class PermissionContext:
    user_id: str
    device_id: str | None
    autonomy_mode: AutonomyMode
    tool_name: str
    tool_args: dict[str, Any]


@dataclass
class PermissionResult:
    allowed: bool
    requires_approval: bool
    risk_level: RiskLevel
    reason: str


# ---------------------------------------------------------------------------
# Tool risk table
# ---------------------------------------------------------------------------

# Maps tool_name → (minimum_autonomy_mode_to_run_without_approval, risk_level)
# If the current autonomy_mode is BELOW the minimum, approval is required.
_TOOL_RISK: dict[str, tuple[AutonomyMode, RiskLevel]] = {
    # Read operations — allowed in supervised mode without approval
    "read_file":            (AutonomyMode.SUPERVISED, RiskLevel.LOW),
    "list_directory":       (AutonomyMode.SUPERVISED, RiskLevel.LOW),
    "search_codebase":      (AutonomyMode.SUPERVISED, RiskLevel.LOW),
    "read_screen":          (AutonomyMode.SUPERVISED, RiskLevel.LOW),
    "web_search":           (AutonomyMode.SUPERVISED, RiskLevel.LOW),
    "fetch_url":            (AutonomyMode.SUPERVISED, RiskLevel.LOW),

    # Write / create operations
    "write_file":           (AutonomyMode.BOUNDED, RiskLevel.MEDIUM),
    "create_directory":     (AutonomyMode.BOUNDED, RiskLevel.MEDIUM),
    "run_dev_command":      (AutonomyMode.BOUNDED, RiskLevel.MEDIUM),

    # Browser automation — read
    "browser_navigate":     (AutonomyMode.SUPERVISED, RiskLevel.LOW),
    "browser_read_page":    (AutonomyMode.SUPERVISED, RiskLevel.LOW),

    # Browser automation — write / submit
    "browser_click":        (AutonomyMode.BOUNDED, RiskLevel.MEDIUM),
    "browser_fill_form":    (AutonomyMode.BOUNDED, RiskLevel.HIGH),
    "browser_submit":       (AutonomyMode.BOUNDED, RiskLevel.HIGH),

    # Application control
    "launch_app":           (AutonomyMode.BOUNDED, RiskLevel.MEDIUM),
    "close_app":            (AutonomyMode.BOUNDED, RiskLevel.MEDIUM),

    # Destructive — always require approval regardless of mode
    "delete_file":          (AutonomyMode.BOUNDED, RiskLevel.HIGH),
    "delete_directory":     (AutonomyMode.BOUNDED, RiskLevel.CRITICAL),
    "run_admin_command":    (AutonomyMode.BOUNDED, RiskLevel.CRITICAL),
    "send_message":         (AutonomyMode.BOUNDED, RiskLevel.HIGH),
    "make_purchase":        (AutonomyMode.BOUNDED, RiskLevel.CRITICAL),
    "change_security":      (AutonomyMode.BOUNDED, RiskLevel.CRITICAL),
}

# These tools ALWAYS require explicit approval, no matter the autonomy mode
_ALWAYS_REQUIRE_APPROVAL: frozenset[str] = frozenset({
    "delete_file",
    "delete_directory",
    "run_admin_command",
    "make_purchase",
    "change_security",
    "browser_fill_form",
    "browser_submit",
    "send_message",
})

# Autonomy mode ordering (higher index = more autonomous)
_MODE_ORDER = [
    AutonomyMode.CONVERSATION,
    AutonomyMode.ASSISTED,
    AutonomyMode.SUPERVISED,
    AutonomyMode.BOUNDED,
]


def _mode_level(mode: AutonomyMode) -> int:
    return _MODE_ORDER.index(mode)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_permission(ctx: PermissionContext) -> PermissionResult:
    """Evaluate whether an agent may execute a tool call.

    This is the single enforcement point. Called before EVERY tool execution.
    Never called inside an LLM — always called in Python.
    """
    tool = ctx.tool_name

    if tool not in _TOOL_RISK:
        logger.warning("Unknown tool requested", tool=tool, user_id=ctx.user_id)
        return PermissionResult(
            allowed=False,
            requires_approval=False,
            risk_level=RiskLevel.CRITICAL,
            reason=f"Tool '{tool}' is not registered. Unknown tools are denied.",
        )

    min_mode, risk = _TOOL_RISK[tool]

    # Conversation mode — no external actions permitted
    if ctx.autonomy_mode == AutonomyMode.CONVERSATION:
        return PermissionResult(
            allowed=False,
            requires_approval=False,
            risk_level=risk,
            reason="Autonomy mode is 'conversation' — no external actions permitted.",
        )

    # Assisted mode — only low-risk reads permitted without approval
    if ctx.autonomy_mode == AutonomyMode.ASSISTED:
        if risk != RiskLevel.LOW:
            return PermissionResult(
                allowed=False,
                requires_approval=False,
                risk_level=risk,
                reason="Autonomy mode is 'assisted' — only read operations permitted.",
            )
        # Low-risk reads: explicitly permitted, no approval needed
        logger.info("Permission granted (assisted read)", tool=tool, user_id=ctx.user_id)
        return PermissionResult(
            allowed=True,
            requires_approval=False,
            risk_level=risk,
            reason="Low-risk read permitted in assisted mode.",
        )

    # Always-require-approval tools
    if tool in _ALWAYS_REQUIRE_APPROVAL:
        logger.info("Approval required (always)", tool=tool, user_id=ctx.user_id)
        return PermissionResult(
            allowed=True,
            requires_approval=True,
            risk_level=risk,
            reason=f"'{tool}' always requires explicit user approval.",
        )

    # Mode check — if user's mode is below the tool's minimum, require approval
    if _mode_level(ctx.autonomy_mode) < _mode_level(min_mode):
        return PermissionResult(
            allowed=True,
            requires_approval=True,
            risk_level=risk,
            reason=f"'{tool}' requires '{min_mode.value}' mode; current is '{ctx.autonomy_mode.value}'.",
        )

    # Permitted without approval
    logger.info("Permission granted", tool=tool, user_id=ctx.user_id, risk=risk.value)
    return PermissionResult(
        allowed=True,
        requires_approval=False,
        risk_level=risk,
        reason="Permitted under current autonomy mode.",
    )


def validate_path_in_allowed_roots(
    path: str,
    allowed_roots: list[str],
    write: bool = False,
) -> bool:
    """Validate a file path is within the user's approved roots.

    Always call this before any file I/O. Never trust LLM-generated paths directly.
    """
    import os
    target = os.path.realpath(os.path.expanduser(path))
    for root in allowed_roots:
        real_root = os.path.realpath(os.path.expanduser(root))
        if target.startswith(real_root + os.sep) or target == real_root:
            return True
    return False
