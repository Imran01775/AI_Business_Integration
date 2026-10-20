"""Settings, templates, secrets SQL adapter integration tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.tenant_isolation.harness import create_test_tenants

from app.core.db.crypto import AesGcmEnvelope
from app.core.db.uow import UnitOfWork
from app.core.events.in_memory import InMemoryOutbox
from app.core.ids import Uuid7Generator
from app.modules.audit.application.sample_observability import record_sample_business_failure
from app.modules.audit.infrastructure.sql_audit import SqlAuditPort
from app.modules.audit.infrastructure.sql_error_events import SqlErrorEventsPort
from app.modules.settings.infrastructure.sql_secrets import SqlSecretsStore
from app.modules.settings.infrastructure.sql_store import SqlSettingValueStore
from app.modules.settings.infrastructure.sql_templates import SqlTemplateStore
from app.modules.tenancy.infrastructure.repository import TenantRepository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_settings_history_and_rollback(
    pg_session_factory: async_sessionmaker[AsyncSession],
    tenant_repo: TenantRepository,
) -> None:
    tenant_id, _ = await create_test_tenants(tenant_repo)
    store = SqlSettingValueStore(pg_session_factory, Uuid7Generator())
    v1 = await store.set_value(
        "tenant",
        str(tenant_id),
        "platform.maintenance_mode",
        True,
        rls_tenant_id=tenant_id,
    )
    v2 = await store.set_value(
        "tenant",
        str(tenant_id),
        "platform.maintenance_mode",
        False,
        rls_tenant_id=tenant_id,
    )
    assert v2 == v1 + 1
    await store.rollback_value(
        "tenant",
        str(tenant_id),
        "platform.maintenance_mode",
        to_version=1,
        rls_tenant_id=tenant_id,
    )
    value = await store.get_value(
        "tenant",
        str(tenant_id),
        "platform.maintenance_mode",
        rls_tenant_id=tenant_id,
    )
    assert value is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_template_persist_and_render(
    pg_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    store = SqlTemplateStore(pg_session_factory, Uuid7Generator())
    await store.upsert("platform.welcome", "en", "Hi {{ name }}", ["name"], tenant_id=None)
    loaded = await store.get_template("platform.welcome", "en", tenant_id=None)
    assert loaded == ("Hi {{ name }}", ["name"])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_secrets_encrypt_decrypt_and_key_rotation(
    pg_session_factory: async_sessionmaker[AsyncSession],
    tenant_repo: TenantRepository,
) -> None:
    tenant_id, _ = await create_test_tenants(tenant_repo)
    crypto_v1 = AesGcmEnvelope("rotation-key-v1-32bytes-min!!", key_version=1)
    store = SqlSecretsStore(pg_session_factory, crypto_v1, Uuid7Generator())
    await store.put_secret("tenant", str(tenant_id), "token", "plain", tenant_id=tenant_id)
    assert await store.get_secret("tenant", str(tenant_id), "token", tenant_id=tenant_id) == "plain"

    crypto_v2 = AesGcmEnvelope("rotation-key-v2-32bytes-min!!", key_version=2)
    store_v2 = SqlSecretsStore(pg_session_factory, crypto_v2, Uuid7Generator())
    await store_v2.put_secret("tenant", str(tenant_id), "token", "rotated", tenant_id=tenant_id)
    assert (
        await store_v2.get_secret("tenant", str(tenant_id), "token", tenant_id=tenant_id)
        == "rotated"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_outbox_persisted_in_same_transaction(
    pg_session_factory: async_sessionmaker[AsyncSession],
    tenant_repo: TenantRepository,
) -> None:
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.core.db.models.platform import OutboxEvent
    from app.core.events.postgres_outbox import PostgresOutbox
    from app.shared.events import ActorRef, DomainEvent

    tenant_id, _ = await create_test_tenants(tenant_repo)
    ids = Uuid7Generator()
    outbox = PostgresOutbox(pg_session_factory, ids)
    uow = UnitOfWork(pg_session_factory, outbox)
    event = DomainEvent(
        event_id=ids.uuid7(),
        type="settings.changed",
        occurred_at=datetime.now(UTC),
        tenant_id=tenant_id,
        trace_id="trace-outbox",
        actor=ActorRef(type="system", id="seed"),
        payload={"key": "platform.maintenance_mode"},
    )
    async with uow:
        uow.collect_event(event)
    async with pg_session_factory() as session:
        count = (
            (
                await session.execute(
                    select(OutboxEvent).where(OutboxEvent.topic == "settings.changed")
                )
            )
            .scalars()
            .all()
        )
        assert len(count) >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_audit_and_error_events_sample_use_case(
    pg_session_factory: async_sessionmaker[AsyncSession],
    tenant_repo: TenantRepository,
) -> None:
    tenant_id, _ = await create_test_tenants(tenant_repo)
    ids = Uuid7Generator()
    uow = UnitOfWork(pg_session_factory, InMemoryOutbox())
    await record_sample_business_failure(
        uow,
        SqlAuditPort(ids),
        SqlErrorEventsPort(ids),
        tenant_id=tenant_id,
        trace_id="trace-1",
        actor_id="user-1",
        error_code="demo.failure",
        message="sample failure",
        entity_type="error_event",
        entity_id="demo",
    )
