from __future__ import annotations

from dataclasses import dataclass
import mimetypes
import logging
from pathlib import PurePosixPath
from urllib.parse import urlparse
from uuid import uuid4

import httpx
from fastapi import UploadFile

from app.core.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Raised when a file cannot be uploaded to storage."""


@dataclass(slots=True)
class UploadResult:
    file_url: str
    original_filename: str
    content_type: str


class SupabaseStorageService:
    def __init__(self) -> None:
        self.base_url = (settings.supabase_url or "").rstrip("/")
        self.bucket = settings.supabase_bucket
        self.api_key = settings.supabase_service_role_key or ""

    @property
    def _local_upload_dir(self):
        return settings.static_dir / "uploads"

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.bucket)

    async def upload_file(
        self,
        upload: UploadFile,
        folder: str,
        owner_id: int | None = None,
    ) -> UploadResult:
        filename = upload.filename or "upload.bin"
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in settings.upload_extensions:
            raise StorageError(
                f"Unsupported file type. Allowed: {', '.join(sorted(settings.upload_extensions))}."
            )

        content = await upload.read()
        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise StorageError(
                f"File is too large. Maximum allowed size is {settings.max_upload_size_mb} MB."
            )

        content_type = upload.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        storage_path = PurePosixPath(folder) / str(owner_id or "shared") / f"{uuid4().hex}.{extension}"

        if not self.is_configured and settings.is_development:
            local_path = self._local_upload_dir / storage_path.as_posix()
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(content)
            logger.warning("Using local development storage fallback for %s", local_path)
            return UploadResult(
                file_url=f"/static/uploads/{storage_path.as_posix()}",
                original_filename=filename,
                content_type=content_type,
            )

        if not self.is_configured:
            raise StorageError(
                "Supabase storage is not configured. Set SUPABASE_URL, "
                "SUPABASE_SERVICE_ROLE_KEY, and SUPABASE_BUCKET."
            )

        endpoint = f"{self.base_url}/storage/v1/object/{self.bucket}/{storage_path.as_posix()}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "apikey": self.api_key,
            "Content-Type": content_type,
            "x-upsert": "false",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, headers=headers, content=content)

        if response.status_code >= 400:
            raise StorageError(
                "Upload to Supabase failed. "
                f"Status {response.status_code}: {response.text[:200]}"
            )

        file_url = (
            f"{self.base_url}/storage/v1/object/public/{self.bucket}/{storage_path.as_posix()}"
        )
        return UploadResult(
            file_url=file_url,
            original_filename=filename,
            content_type=content_type,
        )

    async def delete_file(self, file_url: str | None) -> None:
        if not file_url:
            return

        if file_url.startswith("/static/uploads/") and settings.is_development:
            local_path = settings.static_dir / file_url.lstrip("/")
            if local_path.exists():
                local_path.unlink()
            return

        if not self.is_configured or self.base_url not in file_url:
            return

        parsed = urlparse(file_url)
        marker = f"/storage/v1/object/public/{self.bucket}/"
        if marker not in parsed.path:
            return

        object_path = parsed.path.split(marker, 1)[1]
        endpoint = f"{self.base_url}/storage/v1/object/{self.bucket}/{object_path}"
        headers = {"Authorization": f"Bearer {self.api_key}", "apikey": self.api_key}

        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.delete(endpoint, headers=headers)

