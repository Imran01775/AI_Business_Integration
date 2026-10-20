# ADR 0006 — Phase 02 database & multi-tenancy

## Status
Accepted (2026-10-13)

## Context
Phase 02 requires PostgreSQL schema via Alembic, RLS-based tenant isolation, platform tables (outbox, settings, secrets, audit), and SQL adapters replacing Phase 01 in-memory stores.

## Decision
- **Alembic async** env under `backend/migrations/` with revision prefix `platform:` in docstring / module tag.
- **RLS** via migration helper `enable_tenant_rls(regclass)`; runtime sets `app.tenant_id` with `SET LOCAL` inside transactions (`TenantContext`).
- **DB roles:** `app_owner` (migrations), `app_rw` (`NOBYPASSRLS`), `app_platform` (admin path, `BYPASSRLS` — audited in application code).
- **Secrets at rest:** AES-256-GCM envelope in application layer (`AesGcmEnvelope`) with `key_version` column; not pgcrypto column encryption (keeps rotation in app).
- **UUIDv7** assigned in application via `Uuid7Generator` on insert.

## Consequences
- Integration tests use Testcontainers PostgreSQL 16; CI must allow Docker.
- Seed command (`python -m app.main.cli seed`) is idempotent and separate from migrations.
- Platform-scoped settings/templates use `tenant_id IS NULL` with RLS policy allowing null tenant rows.
