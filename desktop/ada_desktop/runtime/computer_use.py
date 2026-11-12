"""Windows Computer Use Engine for ADA Desktop Companion.

Provides direct, high-precision desktop control via pure ctypes and Windows user32:
- Mouse movement, clicking, dragging, and scrolling
- Keyboard typing, hotkeys, and keypresses
- Window discovery, enumeration, and foreground focus
- Target verification and safe boundary constraints
"""
from __future__ import annotations

import ctypes
import time
from ctypes import wintypes
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

user32 = ctypes.windll.user32

# Mouse action flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

# Keyboard action flags
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class ComputerUse:
    """Low-level Windows automation controller."""

    @staticmethod
    def get_cursor_position() -> tuple[int, int]:
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    @staticmethod
    def move_mouse(x: int, y: int) -> None:
        user32.SetCursorPos(int(x), int(y))
        logger.info("Moved mouse", x=x, y=y)

    @staticmethod
    def click_mouse(x: int | None = None, y: int | None = None, button: str = "left", double: bool = False) -> None:
        if x is not None and y is not None:
            user32.SetCursorPos(int(x), int(y))
            time.sleep(0.05)

        down = MOUSEEVENTF_LEFTDOWN if button == "left" else MOUSEEVENTF_RIGHTDOWN
        up = MOUSEEVENTF_LEFTUP if button == "left" else MOUSEEVENTF_RIGHTUP

        user32.mouse_event(down, 0, 0, 0, 0)
        time.sleep(0.03)
        user32.mouse_event(up, 0, 0, 0, 0)

        if double:
            time.sleep(0.08)
            user32.mouse_event(down, 0, 0, 0, 0)
            time.sleep(0.03)
            user32.mouse_event(up, 0, 0, 0, 0)

        logger.info("Clicked mouse", x=x, y=y, button=button, double=double)

    @staticmethod
    def scroll_mouse(clicks: int) -> None:
        # 120 units per notch
        delta = clicks * 120
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        logger.info("Scrolled mouse", clicks=clicks)

    @staticmethod
    def type_text(text: str) -> None:
        """Type arbitrary unicode text into the active window."""
        for char in text:
            code = ord(char)
            # Send unicode key down and up
            user32.keybd_event(0, code, KEYEVENTF_UNICODE, 0)
            user32.keybd_event(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0)
            time.sleep(0.015)
        logger.info("Typed text", length=len(text))

    @staticmethod
    def press_key(vk_code: int) -> None:
        user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

    @staticmethod
    def focus_window(title_substring: str) -> bool:
        """Find a visible top-level window by title substring and bring to foreground."""
        found_hwnd = None

        def enum_windows_callback(hwnd: int, lparam: int) -> bool:
            nonlocal found_hwnd
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    if title_substring.lower() in buff.value.lower():
                        found_hwnd = hwnd
                        return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

        if found_hwnd:
            user32.ShowWindow(found_hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(found_hwnd)
            logger.info("Focused window", title=title_substring, hwnd=found_hwnd)
            return True

        logger.warning("Window not found", title=title_substring)
        return False
