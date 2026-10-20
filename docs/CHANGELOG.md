# Changelog

All notable changes are documented here ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/), [Semantic Versioning](https://semver.org/)).

## [Unreleased]
### Added
- Architecture and phase plan (`docs/`), global engineering rules, project folder skeleton.
- Phase 00: `backend/` and `ai-platform/` uv projects (ruff, mypy strict, pytest, import-linter), frontend pnpm/Turborepo workspace, `docs/LOCAL_SETUP.md`, Meta app checklist, STT eval plan, ADRs 0001–0004.
- Phase 01: backend core platform — FastAPI app factory, DI container, structlog + trace_id, error envelope, async DB/UoW/tenant context, ports (cache, jobs, events/outbox, storage, email, realtime), settings registry/resolver/templates, audit port, health + Prometheus metrics, module generator (`backend/scripts/new_module.py`), ADR 0005.
- Phase 02: Alembic async migrations, PostgreSQL platform schema with RLS, SQL adapters (settings, templates, secrets, audit, error_events, outbox), AES-GCM secrets envelope, idempotent `python -m app.main.cli seed`, tenant-isolation test harness, backup runbook, ADR 0006.
