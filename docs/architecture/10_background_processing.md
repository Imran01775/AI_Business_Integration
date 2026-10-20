# 10 — Background Processing

> Apply `docs/GLOBAL_RULES.md` (esp. R-EVT-03, R-EVT-04).

## 1. Engine
**ARQ** (async, Redis-based) behind `JobQueue` port (`enqueue(job_name, payload, queue, defer_by, job_id)`); Celery/Dramatiq swappable. ARQ cron for schedules.

## 2. Queues & workers
| Queue | Jobs | Scaling note |
|---|---|---|
| `inbound` | run inbound pipeline per message (guard → rules → engine) | scale with message volume; per-conversation lock |
| `stt` | download audio, validate, transcribe | CPU/GPU-bound if self-hosted whisper; isolate |
| `ai` | LLM calls for answering, learning redaction, eval runs | scale with AI load; rate-limit per provider |
| `outbound` | send messages to Meta (respect 24h window, retry on 5xx) | rate-limit per page |
| `import` | CSV dry-run + confirm, image fetch, re-index | bursty; low priority |
| `indexing` | embeddings + chunk upserts | low priority |
| `notifications` | email/in-app/push dispatch | |
| `events` | outbox relay + event consumers | always-on |
| `maintenance` (cron) | lifecycle idle/close sweeper, retention deletion, quota period rollover, token-expiry checks, analytics rollups, partition management, stale-lock cleanup | single instance (leader lock) |

## 3. Job design rules
- Payload = ids + `tenant_id` + `trace_id` (never big blobs or secrets).
- **Idempotent** (job_id = deterministic key, e.g. `stt:{message_id}`), **timeout**, **max retries** with exponential backoff + jitter, classified errors (retryable vs permanent).
- On permanent failure → `job_failures` + `error_events` + DLQ; admin retry.
- Tenant fairness: per-tenant concurrency limit for `ai`/`stt` (Redis semaphore) so one tenant cannot starve others.
- Observability: job duration/failure metrics, trace propagation from enqueuer.

## 4. Scheduled jobs (cron)
| Job | Frequency | Config key |
|---|---|---|
| Conversation idle/close sweeper | 1 min | `lifecycle.idle_after_minutes`, `lifecycle.close_after_hours` |
| Retention purge (audio, transcripts, logs, exports) | hourly | `retention.*` |
| Quota period rollover / usage aggregation | hourly + monthly | `billing.period` |
| Subscription past-due / suspend / expire | hourly | `billing.grace_days`, `billing.suspend_after_days` |
| Meta token expiry check | daily | `channels.token_warning_days` |
| Analytics daily rollup | nightly | — |
| Outbox cleanup / partition maintenance | daily | — |

## 5. Realtime fan-out
Workers publish UI events to Redis pub/sub channel `rt:t:{tenant_id}` → API SSE endpoint streams to connected seller/admin clients.
