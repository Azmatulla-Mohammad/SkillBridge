from __future__ import annotations


import subprocess
import sys
import tempfile
import time
from pathlib import Path

from typing import Any

from app.core.config import get_settings
from app.services.execution.execution_provider import ExecutionProvider

import logging

logger = logging.getLogger(__name__)



class LocalPythonProvider(ExecutionProvider):
    """MVP local-only Python execution provider.

    - Executes Python source using sys.executable
    - No shell invocation
    - Uses a temporary .py file
    - Captures stdout/stderr
    """

    def __init__(self) -> None:
        settings = get_settings()

        # Timeout for the whole execution.
        self.timeout_seconds: int = int(
            getattr(settings, "PYTHON_EXECUTION_TIMEOUT", 5) or 5
        )

        # Maximum characters from stdout/stderr combined.
        # This is enforced by truncating captured output.
        self.max_output_size: int = int(
            getattr(settings, "PYTHON_MAX_OUTPUT_SIZE", 50000) or 50000
        )

    def _truncate_output(self, text: str) -> str:
        if self.max_output_size <= 0:
            return ""
        if text is None:
            return ""
        if len(text) <= self.max_output_size:
            return text
        return text[: self.max_output_size]

    async def run_python(
        self,
        *,
        code: str,
        stdin: str | None = None,
        timeout: int = 5,
    ) -> dict[str, Any]:
        started = time.perf_counter()

        # Respect provider-level default timeout while allowing request override.
        exec_timeout = int(timeout) if timeout is not None else self.timeout_seconds

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            tmp_path = Path(f.name)

        try:
            logger.debug("Starting LocalPythonProvider execution")
            logger.debug("sys.executable=%s", sys.executable)

            input_text = stdin or ""
            run_timeout = max(1, exec_timeout)

            try:
                completed = subprocess.run(
                    [sys.executable, str(tmp_path)],
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=run_timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                stdout = self._truncate_output(getattr(exc, "stdout", "") or "")
                stderr = self._truncate_output(getattr(exc, "stderr", "") or "")
                return {
                    "success": False,
                    "stdout": stdout,
                    "stderr": stderr or "Execution timed out.",
                    "exit_code": None,
                    "execution_time": float(time.perf_counter() - started),
                }
            except SyntaxError as exc:
                # SyntaxError won't typically be raised here (it is captured in stderr),
                # but keep for contract completeness.
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"SyntaxError: {exc}",
                    "exit_code": None,
                    "execution_time": float(time.perf_counter() - started),
                }
            except Exception as exc:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Subprocess failure: {exc}",
                    "exit_code": None,
                    "execution_time": float(time.perf_counter() - started),
                }

            stdout = self._truncate_output(completed.stdout or "")
            stderr = self._truncate_output(completed.stderr or "")
            exit_code = completed.returncode

            success = exit_code == 0
            # Keep contract stable even on non-zero exit.
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "execution_time": float(time.perf_counter() - started),
            }
        finally:
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                # Best-effort cleanup.
                pass

