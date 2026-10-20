# Phase 21 — Containerization (DEFERRED)

> **Status: DEFERRED.** Do **not** create Dockerfiles/compose files until the owner explicitly starts this phase (R-PROC-04).
> **Prompt header (when started):** Apply `docs/GLOBAL_RULES.md`. Phase: 21. Docker actions explicitly approved.

## Goal
Reproducible container images and a local/production Compose topology per doc 16.

## Prerequisites
Phase 20; explicit approval.

## Scope (when started)
Dockerfiles (multi-stage, non-root, healthchecks) for `api`, `worker` (one image, queue via args), `scheduler`, `ai-gateway`, `web` (Next.js standalone); `compose.yaml` for local (PG+pgvector, Redis, MinIO, Mailpit, observability stack) and `compose.prod.yaml` (Caddy, app services, monitoring); `.dockerignore`; image size and startup budgets; SBOM generation.

## Tasks
1. Images per doc 16 §2 principles.
2. Compose profiles: `core`, `observability`, `ai-local` (faster-whisper/Ollama optional).
3. Env templates per environment; secrets via env files outside repo.
4. Smoke test: whole stack up, quality journeys pass against containers.

## Acceptance criteria
- [ ] `compose up` brings full stack; e2e passes against it
- [ ] Images non-root, scanned, < target sizes

## Rules checklist
- [ ] R-SEC-08/09 · R-CFG-08 · PROGRESS_LOG
