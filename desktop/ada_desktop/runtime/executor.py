"""Local Tool Execution Engine for ADA Desktop Companion.

Executes permitted operations locally on the user's Windows workstation:
- File system operations (strictly constrained to allowed roots)
- Developer commands and scripts
- Application launch and window management
- Screen reading and OCR context
"""
from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any

import structlog

from ada_desktop.config import get_desktop_settings

logger = structlog.get_logger(__name__)


class ExecutionResult:
    def __init__(self, success: bool, output: Any = None, error: str | None = None) -> None:
        self.success = success
        self.output = output
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
        }


class LocalExecutor:
    """Executes validated desktop actions with explicit boundary checking."""

    def __init__(self, allowed_roots: list[str] | None = None) -> None:
        settings = get_desktop_settings()
        self.allowed_roots = allowed_roots or settings.allowed_roots

    def validate_path(self, path_str: str) -> bool:
        """Enforce path boundary: path must reside inside one of the allowed roots."""
        try:
            target = os.path.realpath(os.path.expanduser(path_str))
            for root in self.allowed_roots:
                real_root = os.path.realpath(os.path.expanduser(root))
                if target.startswith(real_root + os.sep) or target == real_root:
                    return True
            return False
        except Exception:
            return False

    async def execute_tool(self, tool_name: str, tool_args: dict[str, Any]) -> ExecutionResult:
        """Route and execute a local desktop tool."""
        logger.info("Executing local tool", tool=tool_name)

        if tool_name == "read_file":
            return self._read_file(tool_args.get("path", ""))

        elif tool_name == "write_file":
            return self._write_file(tool_args.get("path", ""), tool_args.get("content", ""))

        elif tool_name == "list_directory":
            return self._list_directory(tool_args.get("path", "."))

        elif tool_name == "run_dev_command":
            return await self._run_command(
                command=tool_args.get("command", ""),
                cwd=tool_args.get("cwd"),
                timeout=tool_args.get("timeout", 60),
            )

        elif tool_name == "launch_app":
            return self._launch_app(tool_args.get("app_name", ""))

        else:
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' is not supported by the local desktop executor.",
            )

    def _read_file(self, path: str) -> ExecutionResult:
        if not self.validate_path(path):
            return ExecutionResult(success=False, error=f"Path '{path}' is outside allowed directory roots.")

        try:
            content = Path(path).read_text(encoding="utf-8", errors="replace")
            return ExecutionResult(success=True, output=content)
        except Exception as exc:
            return ExecutionResult(success=False, error=str(exc))

    def _write_file(self, path: str, content: str) -> ExecutionResult:
        if not self.validate_path(path):
            return ExecutionResult(success=False, error=f"Path '{path}' is outside allowed directory roots.")

        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return ExecutionResult(success=True, output=f"Successfully wrote {len(content)} bytes to {path}")
        except Exception as exc:
            return ExecutionResult(success=False, error=str(exc))

    def _list_directory(self, path: str) -> ExecutionResult:
        if not self.validate_path(path):
            return ExecutionResult(success=False, error=f"Path '{path}' is outside allowed directory roots.")

        try:
            entries = os.listdir(path)
            return ExecutionResult(success=True, output=entries)
        except Exception as exc:
            return ExecutionResult(success=False, error=str(exc))

    async def _run_command(self, command: str, cwd: str | None = None, timeout: int = 60) -> ExecutionResult:
        if cwd and not self.validate_path(cwd):
            return ExecutionResult(success=False, error=f"CWD '{cwd}' is outside allowed directory roots.")

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                out_str = stdout.decode("utf-8", errors="replace")
                err_str = stderr.decode("utf-8", errors="replace")
                success = (proc.returncode == 0)

                return ExecutionResult(
                    success=success,
                    output={
                        "returncode": proc.returncode,
                        "stdout": out_str,
                        "stderr": err_str,
                    },
                    error=err_str if not success else None,
                )
            except asyncio.TimeoutError:
                proc.kill()
                return ExecutionResult(success=False, error=f"Command timed out after {timeout} seconds.")
        except Exception as exc:
            return ExecutionResult(success=False, error=str(exc))

    def _launch_app(self, app_name: str) -> ExecutionResult:
        try:
            subprocess.Popen(["start", app_name], shell=True)
            return ExecutionResult(success=True, output=f"Launched application '{app_name}'")
        except Exception as exc:
            return ExecutionResult(success=False, error=str(exc))
