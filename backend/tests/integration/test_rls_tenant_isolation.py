"""RLS tenant isolation integration tests."""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.tenant_isolation.harness import create_test_tenants

from app.core.db.crypto import AesGcmEnvelope
from app.core.db.tenant import TenantContext
from app.core.ids import Uuid7Generator
from app.modules.settings.infrastructure.models import SecretRow
from app.modules.settings.infrastructure.sql_secrets import SqlSecretsStore
from app.modules.tenancy.infrastructure.repository import TenantRepository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rls_blocks_cross_tenant_secret_reads(
    pg_session_factory: async_sessionmaker[AsyncSession],
    tenant_repo: TenantRepository,
) -> None:
    tenant_a, tenant_b = await create_test_tenants(tenant_repo)
    store = SqlSecretsStore(
        pg_session_factory, AesGcmEnvelope("test-key-32-bytes-minimum!!"), Uuid7Generator()
    )
    await store.put_secret("tenant", str(tenant_a), "api_key", "secret-a", tenant_id=tenant_a)

    async with pg_session_factory() as session:
        await TenantContext(tenant_id=tenant_b).apply(session)
        stmt = text(
            "SELECT id FROM secrets WHERE tenant_id = :tenant_id AND key = 'api_key'",
        )
        row = (await session.execute(stmt, {"tenant_id": tenant_a})).first()
        assert row is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_app_rw_role_cannot_bypass_rls(
    pg_session_factory: async_sessionmaker[AsyncSession],
    tenant_repo: TenantRepository,
    postgres_url: str,
) -> None:
    tenant_a, tenant_b = await create_test_tenants(tenant_repo)
    ids = Uuid7Generator()
    async with pg_session_factory() as session:
        session.add(
            SecretRow(
                id=ids.uuid7(),
                tenant_id=tenant_a,
                scope_type="tenant",
                scope_id=str(tenant_a),
                key="k1",
                ciphertext=b"cipher",
                key_version=1,
            ),
        )
        await session.commit()

    rw_url = postgres_url.replace("test:test@", "app_rw:app_rw_dev_change_me@")
    if "app_rw@" not in rw_url:
        pytest.skip("app_rw role URL not configured for this Postgres image")

    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(rw_url, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SET app.tenant_id = :tid"), {"tid": str(tenant_b)})
            result = await conn.execute(
                text("SELECT count(*) FROM secrets WHERE tenant_id = :tid"),
                {"tid": str(tenant_a)},
            )
            assert result.scalar_one() == 0
    finally:
        await engine.dispose()
