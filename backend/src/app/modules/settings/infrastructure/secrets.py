"""Envelope-encrypted secrets store (in-memory, R-SEC-09)."""

from __future__ import annotations

import base64
import hashlib
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken

from app.core.db.crypto import AesGcmEnvelope, EncryptedBlob
from app.modules.settings.application.ports import SecretsStorePort


def _derive_fernet_key(raw: str) -> bytes:
    digest = hashlib.sha256(raw.encode()).digest()
    return base64.urlsafe_b64encode(digest)


class FernetSecretsStore(SecretsStorePort):
    def __init__(self, encryption_key: str) -> None:
        self._fernet = Fernet(_derive_fernet_key(encryption_key))
        self._store: dict[tuple[str, str, str, UUID], bytes] = {}

    async def put_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        plaintext: str,
        *,
        tenant_id: UUID,
    ) -> None:
        token = self._fernet.encrypt(plaintext.encode())
        self._store[(scope_type, scope_id, key, tenant_id)] = token

    async def has_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> bool:
        return (scope_type, scope_id, key, tenant_id) in self._store

    async def get_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> str:
        token = self._store.get((scope_type, scope_id, key, tenant_id))
        if token is None:
            raise KeyError(key)
        try:
            return self._fernet.decrypt(token).decode()
        except InvalidToken:
            raise ValueError("invalid ciphertext") from None


class AesGcmSecretsStore(SecretsStorePort):
    """In-memory AES-GCM store for contract tests."""

    def __init__(self, crypto: AesGcmEnvelope) -> None:
        self._crypto = crypto
        self._store: dict[tuple[str, str, str, UUID], EncryptedBlob] = {}

    async def put_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        plaintext: str,
        *,
        tenant_id: UUID,
    ) -> None:
        self._store[(scope_type, scope_id, key, tenant_id)] = self._crypto.encrypt(
            plaintext.encode(),
        )

    async def has_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> bool:
        return (scope_type, scope_id, key, tenant_id) in self._store

    async def get_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> str:
        blob = self._store.get((scope_type, scope_id, key, tenant_id))
        if blob is None:
            raise KeyError(key)
        return self._crypto.decrypt(blob).decode()
