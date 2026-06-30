from __future__ import annotations

import json
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.execution.execution_provider import ExecutionProvider


class PistonProvider(ExecutionProvider):
    def __init__(self) -> None:
        settings = get_settings()

        # Must be configurable via environment variables.
        self.base_url: str = getattr(settings, "PISTON_BASE_URL", "http://localhost:2000")
        self.api_key: str = getattr(settings, "PISTON_API_KEY", "") or ""

        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        # Piston v2 execute endpoint.
        self.execute_url = f"{self.base_url}/api/v2/piston/execute"

    async def run_python(
        self,
        *,
        code: str,
        stdin: str | None = None,
        timeout: int = 5,
    ) -> dict[str, Any]:
        started = time.perf_counter()

        payload = {
            "language": "python3",
            "version": "3.11.0",
            "files": [{"content": code, "name": "main.py"}],
            "stdin": stdin or "",
            "args": [],
        }

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=timeout + 2) as client:
            try:
                resp = await client.post(
                    self.execute_url,
                    headers=headers,
                    content=json.dumps(payload),
                )
            except httpx.HTTPError as exc:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Provider HTTP error: {exc}",
                    "exit_code": None,
                    "execution_time": float(time.perf_counter() - started),
                }

        try:
            data = resp.json()
        except Exception:
            return {
                "success": False,
                "stdout": "",
                "stderr": resp.text[:2000],
                "exit_code": None,
                "execution_time": float(time.perf_counter() - started),
            }

        result_item: dict[str, Any] = {}
        if isinstance(data, list) and data:
            result_item = data[0] or {}

        stdout = result_item.get("stdout") or ""
        stderr = result_item.get("stderr") or ""
        exit_code = result_item.get("code", None)

        return {
            "success": resp.status_code < 500,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "execution_time": float(time.perf_counter() - started),
        }

