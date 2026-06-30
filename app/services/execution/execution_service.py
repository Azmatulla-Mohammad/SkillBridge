from __future__ import annotations

import time
from typing import Any

from app.core.config import get_settings
from app.services.execution.execution_provider import ExecutionProvider


class ExecutionService:
    def __init__(self, provider: ExecutionProvider) -> None:
        self.provider = provider

    async def run_python(
        self,
        *,
        code: str,
        stdin: str | None = None,
        timeout: int = 5,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            result = await self.provider.run_python(code=code, stdin=stdin, timeout=timeout)
            # Ensure consistent contract keys even if provider returns extras.
            exec_time = float(time.perf_counter() - started)
            return {
                "success": bool(result.get("success", False)),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "exit_code": result.get("exit_code", None),
                "execution_time": result.get("execution_time", exec_time),
            }
        except Exception as exc:
            # Never leak provider/HTTP exceptions to UI.
            exec_time = float(time.perf_counter() - started)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution failed: {exc}",
                "exit_code": None,
                "execution_time": exec_time,
            }

