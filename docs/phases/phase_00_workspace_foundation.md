# Phase 00 — Workspace Foundation

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 00. No git/Docker/CI actions.

## Goal
Make the monorepo buildable and testable locally with all quality tools, start long-lead external tasks (Meta app, STT evaluation) early.

## Prerequisites
None. Skeleton folders already exist.

## Requirements covered
Chat: modern tooling, testability, OSS. PDF §12 "Meta assets early", §27.4 "test 2–3 STT providers early".

## Scope
**In:** backend/ai-platform Python projects (uv), frontend pnpm + Turborepo workspace, lint/type/test tooling, `.env.example`, local service setup docs (PostgreSQL 16 + pgvector, Redis, MinIO, Mailpit installed natively), Meta developer app checklist, STT evaluation spike.
**Out:** any business code, Docker, CI, git.

## Tasks
1. `backend/pyproject.toml` (uv): fastapi, uvicorn, pydantic, pydantic-settings, sqlalchemy[asyncio], asyncpg, alembic, structlog, httpx, arq, redis, argon2-cffi, pyjwt, cryptography, tenacity, opentelemetry-*; dev: pytest, pytest-asyncio, pytest-cov, hypothesis, polyfactory, respx, testcontainers, ruff, mypy, import-linter, pip-audit.
2. Ruff + mypy (strict) + pytest config in `pyproject.toml`; `importlinter` contracts skeleton (layers per module + module independence).
3. `ai-platform/pyproject.toml` as an independent package (`ai_platform`), editable-installed into backend env.
4. `frontend/`: `package.json`, `pnpm-workspace.yaml` (apps/*, packages/*), `turbo.json`, `tsconfig.base.json` (strict), ESLint + Prettier shared config, empty package manifests for `packages/*`.
5. `backend/.env.example`, `frontend/apps/web/.env.example` (no secrets).
6. `docs/LOCAL_SETUP.md`: install PG16+pgvector, Redis, MinIO, Mailpit on Windows/WSL; commands to run each tool.
7. `docs/CHANGELOG.md`, `docs/PROGRESS_LOG.md`, `docs/adr/0000-template.md`, `docs/adr/0001-modular-monolith.md`, `0002-ai-platform-separate-package.md`, `0003-arq-redis-jobs.md`.
8. **Meta checklist** (`docs/META_APP_CHECKLIST.md`): business verification, developer app, Messenger product, permissions (`pages_messaging`, `pages_manage_metadata`, `pages_show_list`), privacy policy URL, data deletion URL, app review screencast plan.
9. **STT evaluation spike** (`ai-platform/tests/eval/stt/README.md` + script plan): collect 30–50 real Bangla/Banglish voice samples (consented), compare 2–3 providers (faster-whisper large-v3, Google, Azure) on WER/CER, latency, cost/min. Record result in ADR `0004-stt-provider-choice.md`.

## Tests
`uv run pytest` runs (empty suite passes), `uv run ruff check`, `uv run mypy src`, `lint-imports`, `pnpm -r lint` succeed.

## Acceptance criteria
- [ ] All three projects install with one command each
- [ ] Quality commands documented and green
- [ ] Meta checklist started (app created, owner assigned)
- [ ] STT spike plan + sample collection started
- [ ] ADRs 0001–0003 written

## Risks
Meta business verification can take weeks → started now. Bangla STT quality → spike decides provider.

## Rules checklist
- [ ] GLOBAL_RULES applied · no git/Docker/CI files · requirements.txt untouched · PROGRESS_LOG updated
