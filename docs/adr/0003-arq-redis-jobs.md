# ADR 0003 — ARQ on Redis for background jobs

- Status: accepted
- Date: 2026-10-13
- Phase: 00
- Related rules: R-ARCH-04, R-ARCH-08

## Context

The system needs async work: inbound message pipeline, STT, outbound channel sends, CSV import, notifications, outbox relay, and cron-style maintenance. Jobs must sit behind a port so infrastructure can change without touching use cases.

## Options considered

1. **Celery + Redis/RabbitMQ** — mature, heavier ops and worker model; common in Python ecosystems.
2. **ARQ + Redis** — asyncio-native, smaller surface, fits FastAPI stack; MIT license.
3. **In-process `asyncio.create_task` only** — no persistence or horizontal worker scaling.

## Decision

Use **ARQ** as the default adapter for the **`JobQueue`** port, with **Redis** as the broker (same cluster as cache/rate limits where practical). Wire workers only in the composition root (`backend/src/app/main/`, Phase 01). Keep the port interface swappable (Celery or another broker later via ADR).

## Consequences

- **Positive:** Aligns with doc 02 technology stack; async end-to-end; Redis already required for cache and streams.
- **Negative:** ARQ ecosystem smaller than Celery; team must document queue naming and worker deployment (Phase 10+).
- **Follow-ups:** Phase 01 `JobQueue` port + worker entrypoints; separate queues per doc 04 §8.
