# Phase 01 — Backend Core Platform

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 01. Modules: `core`, `shared`, `main`, `settings` (registry/resolver core), `audit` (port). No git/Docker.

## Goal
Build the cross-cutting foundation every module uses: config, app factory, DI, logging with trace_id, error envelope, DB session/UoW, ports (cache, jobs, events/outbox, storage, email, realtime, clock, ids), settings registry + layered resolver + template renderer, feature flags, module template.

## Prerequisites
Phase 00.

## Requirements covered
Chat: modularity, testability, observability base, configurability. Docs 04, 09, 10, 11, 22, 24.

## Scope
**In:** `core/*`, `shared/*`, `main/*`, settings registry/resolver (logic + ports; tables in Phase 02), health endpoints, OpenAPI base, module template + generator script.
**Out:** business modules, auth (Phase 03).

## Tasks
1. `core/config`: `AppConfig` (pydantic-settings) for env; fail-fast validation.
2. `main/app_factory.py`: FastAPI app, middleware (request_id/trace_id, security headers, CORS, GZip, body size limit), router registry per module, lifespan (DB, Redis).
3. `main/container.py`: composition root wiring ports → adapters (in-memory fakes selectable for tests).
4. `core/logging`: structlog JSON, context vars (trace_id, request_id, tenant_id, user_id, module), PII redaction processor.
5. `core/observability`: OpenTelemetry setup (FastAPI, SQLAlchemy, httpx, Redis), Prometheus `/metrics`, GlitchTip SDK init (DSN optional).
6. `core/errors`: `AppError` hierarchy + global handlers → error envelope (doc 19 §4).
7. `core/db`: async engine, session factory, `UnitOfWork`, `TenantContext` + `SET LOCAL app.tenant_id`, base ORM model (UUIDv7, timestamps, version).
8. `core/events`: `DomainEvent`, `EventBus` port, outbox writer (UoW hook), relay worker, Redis Streams adapter, idempotent consumer base.
9. `core/jobs`: `JobQueue` port + ARQ adapter; `workers/` entrypoints per queue; cron registration with leader lock.
10. `core/cache`: `Cache` port + Redis adapter, versioned keys, single-flight.
11. `core/storage`: `ObjectStorage` port + MinIO/S3 adapter (presigned URLs), local-FS fake.
12. `core/email`: `EmailSender` port + SMTP adapter (Mailpit dev).
13. `core/realtime`: `RealtimePublisher` port (Redis pub/sub) + SSE endpoint `/api/v1/realtime/stream` (auth added in P03).
14. `core/ratelimit`, `core/idempotency` (middleware/dependency), `core/clock`, `core/ids`, `core/http` (httpx client with retries + circuit breaker).
15. `modules/settings` (core part): `SettingDefinition`, registry (collect from each module's `settings.py`), `SettingsResolver` (tenant chain + user chain, clamping, entitlement hook), `TemplateRenderer` (sandboxed Jinja2), `SecretsStore` port (envelope encryption), `settings.changed` event, in-memory adapters.
16. Feature flags: `FeatureFlags` port reading settings (`flags.*`) with rollout %.
17. `audit` port: `AuditPort.record(...)` with in-memory adapter (DB in P02).
18. Health: `/health/live`, `/health/ready`.
19. Module template doc + `scripts/new_module.py` generator (creates layers, settings.py, templates.py, permissions.py, test folders).

## Interfaces (key)
`UnitOfWork`, `EventBus`, `Outbox`, `JobQueue`, `Cache`, `ObjectStorage`, `EmailSender`, `RealtimePublisher`, `SettingsResolver.resolve(key, ctx)`, `TemplateRenderer.render(key, ctx, vars)`, `SecretsStore`, `FeatureFlags`, `AuditPort`, `Clock`, `IdGenerator`.

## Settings & templates
Registry mechanism only; first keys: `platform.maintenance_mode`, `flags.*`.

## Tests
Unit: resolver layering/clamping/chain separation, renderer variable validation, error envelope, redaction. Contract: Cache, JobQueue, ObjectStorage, EventBus (fake vs real). Integration: outbox relay with real Redis.

## Acceptance criteria
- [ ] App boots; health + metrics endpoints work
- [ ] Every log line has trace_id; errors return envelope with trace_id
- [ ] Resolver passes layering + bounds + scope tests
- [ ] Outbox → Redis Streams → idempotent consumer demo works
- [ ] Module generator produces a module passing import-linter

## Risks
Over-engineering core → keep each port minimal; add capabilities when a phase needs them.

## Rules checklist
- [ ] R-ARCH-04/08 ports + composition root · R-CFG-08 · R-OBS-01..03 · tests + coverage · ADR for library picks · PROGRESS_LOG · no git/Docker
