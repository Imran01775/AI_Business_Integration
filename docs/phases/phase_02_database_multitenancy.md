# Phase 02 — Database & Multi-Tenancy

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 02. Modules: `core/db`, `tenancy` (tenant table), `settings`, `audit`. No git/Docker.

## Goal
Production-grade PostgreSQL foundation: Alembic, RLS-based tenant isolation, platform tables (outbox, idempotency, audit, error events, job failures, settings, templates, secrets), seed framework.

## Prerequisites
Phase 01.

## Requirements covered
PDF §12–15 tenant isolation (business_id), encrypt secrets, backups (plan). Docs 05, 22, 24.

## Scope
**In:** Alembic async env, DB roles, RLS helper, base tables, seeds, tenant-isolation test harness, pgvector + pg_trgm extensions.
**Out:** module business tables (added by their phases).

## Tasks
1. `backend/alembic.ini` + `migrations/env.py` (async, module-tagged revisions, naming conventions).
2. Extensions: `pgvector`, `pg_trgm`, `citext`, `pgcrypto`.
3. DB roles: `app_owner` (migrations), `app_rw` (runtime, `NOBYPASSRLS`), `app_platform` (admin queries, audited).
4. RLS helper in migrations: `enable_tenant_rls(table)` creating policy `tenant_id = current_setting('app.tenant_id')::uuid`.
5. Tables: `tenants` (minimal), `outbox_events`, `processed_events`, `idempotency_keys`, `audit_log` (partition-ready), `error_events`, `job_failures`, `setting_definitions`, `setting_values`, `setting_values_history`, `message_templates`, `message_templates_history`, `secrets`, `feature_flags` (if separate), `sync_connections`/`sync_jobs` (reserved, empty — PDF §28).
6. Replace in-memory adapters from P01 with SQL adapters: settings repo, templates repo, secrets repo (AES-GCM envelope, `key_version`), audit repo, error_events repo.
7. Seed framework: `python -m app.main.cli seed` (idempotent): setting definitions sync, default templates bn/en, platform roles.
8. Tenant-isolation test harness: fixture creating tenants A/B + generic assertion helpers reusable by every module.
9. Backup/restore procedure doc (`docs/runbooks/backup_restore.md`) for later production.

## DB changes
As listed; all tenant-scoped tables get `tenant_id` + RLS + index.

## Tests
Integration: RLS blocks cross-tenant reads/writes; migrations upgrade/downgrade; secrets encrypt/decrypt + key rotation; outbox persistence in same transaction; settings history/rollback.

## Acceptance criteria
- [ ] `alembic upgrade head` on empty DB succeeds; downgrade works for this phase
- [ ] Runtime role cannot bypass RLS (test proves it)
- [ ] Settings/templates/secrets persisted with history; rollback works
- [ ] Audit + error_events written from a sample use case

## Risks
RLS + connection pooling: always `SET LOCAL` inside transaction (works with PgBouncer transaction mode).

## Rules checklist
- [ ] R-DB-01..08 · R-TEN-01..05 · R-CFG-06/07 · tests · PROGRESS_LOG · no git/Docker
