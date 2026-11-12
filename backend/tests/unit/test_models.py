"""Tests for domain models — schema correctness and validation."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from ada.models.domain import (
    AutonomyMode,
    DeviceRegister,
    DeviceType,
    MemoryCreate,
    MemoryType,
    MessageSend,
    TaskCreate,
)


class TestDeviceRegister:
    def test_valid_desktop_registration(self):
        d = DeviceRegister(
            device_type=DeviceType.DESKTOP,
            display_name="My Laptop",
            platform="windows",
            app_version="0.1.0",
            capabilities=["automation", "screen_capture"],
        )
        assert d.display_name == "My Laptop"
        assert d.device_type == DeviceType.DESKTOP

    def test_empty_display_name_rejected(self):
        with pytest.raises(ValidationError):
            DeviceRegister(device_type=DeviceType.DESKTOP, display_name="   ")

    def test_capabilities_default_empty(self):
        d = DeviceRegister(device_type=DeviceType.MOBILE, display_name="Phone")
        assert d.capabilities == []


class TestTaskCreate:
    def test_valid_task(self):
        t = TaskCreate(
            title="Run tests",
            autonomy_mode=AutonomyMode.SUPERVISED,
        )
        assert t.priority == 50
        assert t.autonomy_mode == AutonomyMode.SUPERVISED

    def test_priority_bounds(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="x", priority=101)
        with pytest.raises(ValidationError):
            TaskCreate(title="x", priority=-1)

    def test_priority_zero_valid(self):
        t = TaskCreate(title="urgent", priority=0)
        assert t.priority == 0


class TestMemoryCreate:
    def test_importance_bounds(self):
        with pytest.raises(ValidationError):
            MemoryCreate(
                memory_type=MemoryType.EPISODIC,
                content="test",
                importance=1.5,
            )

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            MemoryCreate(
                memory_type=MemoryType.EPISODIC,
                content="test",
                confidence=-0.1,
            )

    def test_valid_memory(self):
        m = MemoryCreate(
            memory_type=MemoryType.PROFILE,
            content="User prefers concise responses",
            importance=0.9,
            tags=["preference", "communication"],
        )
        assert len(m.tags) == 2
        assert m.importance == 0.9


class TestAutonomyModeOrdering:
    def test_all_modes_exist(self):
        modes = [m.value for m in AutonomyMode]
        assert "conversation" in modes
        assert "assisted" in modes
        assert "supervised_execution" in modes
        assert "bounded_autonomy" in modes
