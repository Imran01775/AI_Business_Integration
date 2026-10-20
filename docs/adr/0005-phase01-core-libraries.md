# ADR 0005 — Phase 01 core platform library choices

## Status
Accepted (2026-10-13)

## Context
Phase 01 needs metrics, error tracking, object storage, templating, and time-sortable IDs without pulling business logic into adapters.

## Decision
| Need | Library | Rationale |
|------|---------|-----------|
| `/metrics` | `prometheus-client` | De-facto Prometheus exposition; ASGI mount |
| GlitchTip / Sentry | `sentry-sdk` | GlitchTip is Sentry-compatible; optional DSN |
| S3 / MinIO | `minio` | Official MinIO Python SDK; presigned URLs |
| Message templates | `jinja2` (`SandboxedEnvironment`) | Sandboxed rendering per doc 24 |
| UUIDv7 | `uuid6` | Sortable IDs on Python 3.12 (stdlib UUIDv7 later) |

OpenTelemetry uses existing `opentelemetry-*` packages from Phase 00.

## Consequences
- MinIO adapter is sync SDK wrapped with `asyncio.to_thread` for I/O (no extra aioboto3 dependency in P01).
- Sentry init is no-op when `GLITCHTIP_DSN` is empty.
