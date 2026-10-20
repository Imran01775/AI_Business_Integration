"""Local filesystem object storage fake."""

from __future__ import annotations

import asyncio
from pathlib import Path

from app.core.storage.ports import ObjectStoragePort, PresignedUrl


class LocalObjectStorage(ObjectStoragePort):
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("..", "").lstrip("/")
        return self._root / safe

    async def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        _ = content_type
        path = self._path(key)

        def _write() -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        await asyncio.to_thread(_write)

    async def get_bytes(self, key: str) -> bytes:
        path = self._path(key)
        return await asyncio.to_thread(path.read_bytes)

    async def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            await asyncio.to_thread(path.unlink)

    async def presigned_get(self, key: str, expires_seconds: int = 3600) -> PresignedUrl:
        return PresignedUrl(url=f"file://{self._path(key)}", expires_in_seconds=expires_seconds)
