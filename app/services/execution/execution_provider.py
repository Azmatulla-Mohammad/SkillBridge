from __future__ import annotations

from abc import ABC, abstractmethod


class ExecutionProvider(ABC):
    @abstractmethod
    async def run_python(
        self,
        *,
        code: str,
        stdin: str | None = None,
        timeout: int = 5,
    ) -> dict:
        """Execute Python code and return a provider-agnostic result."""

