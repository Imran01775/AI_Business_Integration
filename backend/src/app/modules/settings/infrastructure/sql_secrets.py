"""PostgreSQL secrets store (AES-GCM envelope)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.crypto import AesGcmEnvelope, EncryptedBlob
from app.core.db.session import session_scope
from app.core.db.tenant import TenantContext
from app.core.ids import IdGenerator
from app.modules.settings.application.ports import SecretsStorePort
from app.modules.settings.infrastructure.models import SecretRow


class SqlSecretsStore(SecretsStorePort):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        crypto: AesGcmEnvelope,
        ids: IdGenerator,
    ) -> None:
        self._session_factory = session_factory
        self._crypto = crypto
        self._ids = ids

    async def put_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        plaintext: str,
        *,
        tenant_id: UUID,
    ) -> None:
        blob = self._crypto.encrypt(plaintext.encode())
        async with session_scope(self._session_factory) as session:
            await TenantContext(tenant_id=tenant_id).apply(session)
            stmt = select(SecretRow).where(
                SecretRow.tenant_id == tenant_id,
                SecretRow.scope_type == scope_type,
                SecretRow.scope_id == scope_id,
                SecretRow.key == key,
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                session.add(
                    SecretRow(
                        id=self._ids.uuid7(),
                        tenant_id=tenant_id,
                        scope_type=scope_type,
                        scope_id=scope_id,
                        key=key,
                        ciphertext=blob.ciphertext,
                        key_version=blob.key_version,
                    ),
                )
            else:
                row.ciphertext = blob.ciphertext
                row.key_version = blob.key_version

    async def has_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> bool:
        async with session_scope(self._session_factory) as session:
            await TenantContext(tenant_id=tenant_id).apply(session)
            stmt = select(SecretRow.id).where(
                SecretRow.tenant_id == tenant_id,
                SecretRow.scope_type == scope_type,
                SecretRow.scope_id == scope_id,
                SecretRow.key == key,
            )
            return (await session.execute(stmt)).scalar_one_or_none() is not None

    async def get_secret(
        self,
        scope_type: str,
        scope_id: str,
        key: str,
        *,
        tenant_id: UUID,
    ) -> str:
        async with session_scope(self._session_factory) as session:
            await TenantContext(tenant_id=tenant_id).apply(session)
            stmt = select(SecretRow).where(
                SecretRow.tenant_id == tenant_id,
                SecretRow.scope_type == scope_type,
                SecretRow.scope_id == scope_id,
                SecretRow.key == key,
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise KeyError(key)
            blob = EncryptedBlob(ciphertext=row.ciphertext, key_version=row.key_version)
            return self._crypto.decrypt(blob).decode()
