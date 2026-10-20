"""Composition root (R-ARCH-08)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.auth.jwt_service import JwtService
from app.core.auth.password_hasher import Argon2PasswordHasher
from app.core.cache.memory import InMemoryCache
from app.core.cache.ports import CachePort
from app.core.cache.redis_cache import RedisCache
from app.core.clock import Clock, SystemClock
from app.core.config import AppConfig
from app.core.db.crypto import AesGcmEnvelope
from app.core.db.engine import create_engine
from app.core.db.session import create_session_factory
from app.core.db.uow import UnitOfWork
from app.core.email.memory import InMemoryEmailSender
from app.core.email.ports import EmailSenderPort
from app.core.email.smtp import SmtpEmailSender
from app.core.events.in_memory import InMemoryEventBus, InMemoryOutbox
from app.core.events.ports import EventBusPort, OutboxPort
from app.core.events.postgres_outbox import PostgresOutbox
from app.core.events.redis_streams import RedisStreamsEventBus
from app.core.events.relay import OutboxRelay
from app.core.http.client import ResilientHttpClient
from app.core.ids import IdGenerator, Uuid7Generator
from app.core.jobs.memory import InMemoryJobQueue
from app.core.jobs.ports import JobQueuePort
from app.core.realtime.memory import InMemoryRealtimePublisher
from app.core.realtime.ports import RealtimePublisherPort
from app.core.realtime.redis_pubsub import RedisRealtimePublisher
from app.core.storage.local import LocalObjectStorage
from app.core.storage.ports import ObjectStoragePort
from app.core.storage.s3 import S3ObjectStorage
from app.modules.audit.application.ports import AuditPort, ErrorEventsPort
from app.modules.audit.infrastructure.memory import InMemoryAuditPort
from app.modules.audit.infrastructure.memory_error_events import InMemoryErrorEventsPort
from app.modules.audit.infrastructure.sql_audit import SqlAuditPort
from app.modules.audit.infrastructure.sql_error_events import SqlErrorEventsPort
from app.modules.identity.application.facade import IdentityFacade
from app.modules.identity.infrastructure.repositories import SqlIdentityRepository
from app.modules.settings.application.bootstrap import build_settings_registry
from app.modules.settings.application.feature_flags import FeatureFlagsPort, SettingsFeatureFlags
from app.modules.settings.application.ports import (
    SecretsStorePort,
    SettingValueStorePort,
    TemplateStorePort,
)
from app.modules.settings.application.resolver import SettingsResolver
from app.modules.settings.application.templates import TemplateRenderer
from app.modules.settings.domain.registry import SettingsRegistry
from app.modules.settings.infrastructure.entitlements import AllowAllEntitlements
from app.modules.settings.infrastructure.memory_store import InMemorySettingValueStore
from app.modules.settings.infrastructure.memory_templates import InMemoryTemplateStore
from app.modules.settings.infrastructure.secrets import FernetSecretsStore
from app.modules.settings.infrastructure.sql_secrets import SqlSecretsStore
from app.modules.settings.infrastructure.sql_store import SqlSettingValueStore
from app.modules.settings.infrastructure.sql_templates import SqlTemplateStore
from app.modules.tenancy.application.facade import TenancyFacade
from app.modules.tenancy.infrastructure.repositories import TenancyRepository


@dataclass
class AppContainer:
    config: AppConfig
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: redis.Redis
    clock: Clock
    ids: IdGenerator
    cache: CachePort
    outbox: OutboxPort
    event_bus: EventBusPort
    outbox_relay: OutboxRelay
    job_queue: JobQueuePort
    storage: ObjectStoragePort
    email: EmailSenderPort
    realtime: RealtimePublisherPort
    http_client: ResilientHttpClient
    settings_registry: SettingsRegistry
    settings_resolver: SettingsResolver
    setting_store: SettingValueStorePort
    template_renderer: TemplateRenderer
    template_store: TemplateStorePort
    secrets_store: SecretsStorePort
    feature_flags: FeatureFlagsPort
    audit: AuditPort
    error_events: ErrorEventsPort
    unit_of_work: UnitOfWork
    jwt: JwtService
    password_hasher: Argon2PasswordHasher
    identity: IdentityFacade
    identity_repo: SqlIdentityRepository
    tenancy: TenancyFacade
    tenancy_repo: TenancyRepository


def build_container(config: AppConfig) -> AppContainer:
    engine = create_engine(config)
    session_factory = create_session_factory(engine)
    redis_client = redis.from_url(str(config.redis_url), decode_responses=False)  # type: ignore[no-untyped-call]
    ids = Uuid7Generator()
    crypto = AesGcmEnvelope(config.secrets_encryption_key, key_version=config.secrets_key_version)

    use_memory = config.use_in_memory_adapters or config.is_test

    cache: CachePort = InMemoryCache() if use_memory else RedisCache(redis_client)
    outbox: OutboxPort = InMemoryOutbox() if use_memory else PostgresOutbox(session_factory, ids)
    event_bus: EventBusPort = (
        InMemoryEventBus() if use_memory else RedisStreamsEventBus(redis_client)
    )
    job_queue: JobQueuePort = InMemoryJobQueue()
    storage: ObjectStoragePort = (
        LocalObjectStorage(Path(".data/objects"))
        if use_memory
        else S3ObjectStorage.from_config(config)
    )
    email: EmailSenderPort = InMemoryEmailSender() if use_memory else SmtpEmailSender(config)
    realtime: RealtimePublisherPort = (
        InMemoryRealtimePublisher() if use_memory else RedisRealtimePublisher(redis_client)
    )

    registry = build_settings_registry()
    if use_memory:
        setting_store: SettingValueStorePort = InMemorySettingValueStore()
        template_store: TemplateStorePort = InMemoryTemplateStore()
        secrets: SecretsStorePort = FernetSecretsStore(config.secrets_encryption_key)
        audit: AuditPort = InMemoryAuditPort()
        error_events: ErrorEventsPort = InMemoryErrorEventsPort()
    else:
        setting_store = SqlSettingValueStore(session_factory, ids)
        template_store = SqlTemplateStore(session_factory, ids)
        secrets = SqlSecretsStore(session_factory, crypto, ids)
        audit = SqlAuditPort(ids)
        error_events = SqlErrorEventsPort(ids)

    resolver = SettingsResolver(registry, setting_store, AllowAllEntitlements())
    template_renderer = TemplateRenderer(template_store)
    feature_flags = SettingsFeatureFlags(resolver)
    http_client = ResilientHttpClient()
    relay = OutboxRelay(outbox, event_bus)
    uow = UnitOfWork(session_factory, outbox)
    jwt = JwtService(config)
    password_hasher = Argon2PasswordHasher()
    identity_repo = SqlIdentityRepository(session_factory, ids)
    tenancy_repo = TenancyRepository(session_factory, ids)
    clock = SystemClock()
    identity = IdentityFacade(
        config=config,
        repo=identity_repo,
        uow=uow,
        jwt=jwt,
        hasher=password_hasher,
        clock=clock,
        ids=ids,
        email=email,
        templates=template_renderer,
        audit=audit,
    )
    tenancy = TenancyFacade(
        config=config,
        repo=tenancy_repo,
        uow=uow,
        clock=clock,
        ids=ids,
        email=email,
        templates=template_renderer,
        audit=audit,
    )

    return AppContainer(
        config=config,
        engine=engine,
        session_factory=session_factory,
        redis=redis_client,
        clock=clock,
        ids=ids,
        cache=cache,
        outbox=outbox,
        event_bus=event_bus,
        outbox_relay=relay,
        job_queue=job_queue,
        storage=storage,
        email=email,
        realtime=realtime,
        http_client=http_client,
        settings_registry=registry,
        settings_resolver=resolver,
        setting_store=setting_store,
        template_renderer=template_renderer,
        template_store=template_store,
        secrets_store=secrets,
        feature_flags=feature_flags,
        audit=audit,
        error_events=error_events,
        unit_of_work=uow,
        jwt=jwt,
        password_hasher=password_hasher,
        identity=identity,
        identity_repo=identity_repo,
        tenancy=tenancy,
        tenancy_repo=tenancy_repo,
    )


async def shutdown_container(container: AppContainer) -> None:
    await container.http_client.close()
    await container.redis.aclose()
    await container.engine.dispose()
