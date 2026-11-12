"""Tests for the permission engine — the core security boundary."""
from __future__ import annotations

import pytest

from ada.models.domain import AutonomyMode, RiskLevel
from ada.permissions.engine import (
    PermissionContext,
    check_permission,
    validate_path_in_allowed_roots,
)


def _ctx(tool: str, mode: AutonomyMode) -> PermissionContext:
    return PermissionContext(
        user_id="user-1",
        device_id="device-1",
        autonomy_mode=mode,
        tool_name=tool,
        tool_args={},
    )


class TestConversationMode:
    """In conversation mode NO external actions are permitted."""

    def test_read_file_denied_in_conversation_mode(self):
        result = check_permission(_ctx("read_file", AutonomyMode.CONVERSATION))
        assert not result.allowed

    def test_write_file_denied_in_conversation_mode(self):
        result = check_permission(_ctx("write_file", AutonomyMode.CONVERSATION))
        assert not result.allowed

    def test_delete_file_denied_in_conversation_mode(self):
        result = check_permission(_ctx("delete_file", AutonomyMode.CONVERSATION))
        assert not result.allowed


class TestAssistedMode:
    """In assisted mode only low-risk reads are permitted."""

    def test_read_file_allowed_in_assisted(self):
        result = check_permission(_ctx("read_file", AutonomyMode.ASSISTED))
        assert result.allowed
        assert not result.requires_approval

    def test_write_file_denied_in_assisted(self):
        result = check_permission(_ctx("write_file", AutonomyMode.ASSISTED))
        assert not result.allowed

    def test_web_search_allowed_in_assisted(self):
        result = check_permission(_ctx("web_search", AutonomyMode.ASSISTED))
        assert result.allowed


class TestSupervisedMode:
    """In supervised mode reads are free; writes need approval."""

    def test_read_file_allowed_no_approval(self):
        result = check_permission(_ctx("read_file", AutonomyMode.SUPERVISED))
        assert result.allowed
        assert not result.requires_approval

    def test_write_file_requires_approval_in_supervised(self):
        result = check_permission(_ctx("write_file", AutonomyMode.SUPERVISED))
        assert result.allowed
        assert result.requires_approval

    def test_run_dev_command_requires_approval_in_supervised(self):
        result = check_permission(_ctx("run_dev_command", AutonomyMode.SUPERVISED))
        assert result.allowed
        assert result.requires_approval

    def test_delete_file_requires_approval_in_supervised(self):
        result = check_permission(_ctx("delete_file", AutonomyMode.SUPERVISED))
        assert result.allowed
        assert result.requires_approval
        assert result.risk_level == RiskLevel.HIGH


class TestBoundedMode:
    """In bounded mode pre-approved low-risk tools run without approval."""

    def test_write_file_allowed_without_approval_in_bounded(self):
        result = check_permission(_ctx("write_file", AutonomyMode.BOUNDED))
        assert result.allowed
        assert not result.requires_approval

    def test_run_dev_command_allowed_without_approval_in_bounded(self):
        result = check_permission(_ctx("run_dev_command", AutonomyMode.BOUNDED))
        assert result.allowed
        assert not result.requires_approval

    def test_delete_file_requires_approval_even_in_bounded(self):
        """High-risk tools still require approval in bounded mode."""
        result = check_permission(_ctx("delete_file", AutonomyMode.BOUNDED))
        assert result.allowed
        assert result.requires_approval

    def test_make_purchase_always_requires_approval(self):
        result = check_permission(_ctx("make_purchase", AutonomyMode.BOUNDED))
        assert result.allowed and result.requires_approval

    def test_delete_directory_always_requires_approval(self):
        result = check_permission(_ctx("delete_directory", AutonomyMode.BOUNDED))
        assert result.allowed
        assert result.requires_approval
        assert result.risk_level == RiskLevel.CRITICAL

    def test_run_admin_command_always_requires_approval(self):
        result = check_permission(_ctx("run_admin_command", AutonomyMode.BOUNDED))
        assert result.allowed
        assert result.requires_approval

    @property
    def allows_but_needs_approval(self):
        return False


class TestUnknownTool:
    """Unknown tools must always be denied."""

    def test_unknown_tool_denied_in_bounded(self):
        result = check_permission(_ctx("rm_rf_everything", AutonomyMode.BOUNDED))
        assert not result.allowed

    def test_unknown_tool_denied_in_supervised(self):
        result = check_permission(_ctx("open_shell", AutonomyMode.SUPERVISED))
        assert not result.allowed


class TestPathValidation:
    """Path validation must reject traversal and out-of-bounds paths."""

    def test_allowed_path_accepted(self):
        import os
        allowed = [os.path.expanduser("~/Documents/projects")]
        path = os.path.join(os.path.expanduser("~/Documents/projects"), "myapp", "README.md")
        assert validate_path_in_allowed_roots(path, allowed, write=False)

    def test_path_outside_roots_rejected(self):
        allowed = ["C:\\Users\\user\\projects"]
        assert not validate_path_in_allowed_roots("C:\\Windows\\System32\\cmd.exe", allowed)

    def test_traversal_rejected(self):
        allowed = ["C:\\Users\\user\\projects"]
        assert not validate_path_in_allowed_roots(
            "C:\\Users\\user\\projects\\..\\..\\Windows\\System32",
            allowed,
        )
