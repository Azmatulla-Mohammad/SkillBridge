from __future__ import annotations

from datetime import UTC, datetime
import re


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-")


def utcnow() -> datetime:
    return datetime.now(UTC)

