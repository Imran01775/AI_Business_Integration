"""MinIO / S3 object storage adapter."""

from __future__ import annotations

import asyncio
import io
from datetime import timedelta

from minio import Minio

from app.core.config import AppConfig
from app.core.storage.ports import ObjectStoragePort, PresignedUrl


class S3ObjectStorage(ObjectStoragePort):
    def __init__(self, client: Minio, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    @classmethod
    def from_config(cls, config: AppConfig) -> S3ObjectStorage:
        client = Minio(
            endpoint=config.s3_endpoint_url.replace("http://", "").replace("https://", ""),
            access_key=config.s3_access_key_id,
            secret_key=config.s3_secret_access_key,
            secure=config.s3_use_ssl,
            region=config.s3_region,
        )
        return cls(client, config.s3_bucket)

    async def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        def _put() -> None:
            self._client.put_object(
                self._bucket,
                key,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )

        await asyncio.to_thread(_put)

    async def get_bytes(self, key: str) -> bytes:
        def _get() -> bytes:
            response = self._client.get_object(self._bucket, key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        return await asyncio.to_thread(_get)

    async def delete(self, key: str) -> None:
        await asyncio.to_thread(self._client.remove_object, self._bucket, key)

    async def presigned_get(self, key: str, expires_seconds: int = 3600) -> PresignedUrl:
        def _url() -> str:
            return self._client.presigned_get_object(
                self._bucket,
                key,
                expires=timedelta(seconds=expires_seconds),
            )

        url = await asyncio.to_thread(_url)
        return PresignedUrl(url=url, expires_in_seconds=expires_seconds)
