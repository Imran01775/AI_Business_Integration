# 12 — Monitoring & Observability

> Apply `docs/GLOBAL_RULES.md` (esp. R-OBS-*). Error/history details: doc 22.

## 1. Three pillars + business signals
| Signal | Tooling | Content |
|---|---|---|
| Logs | structlog JSON → Loki (Promtail/Alloy) | `ts, level, msg, trace_id, request_id, tenant_id, user_id, module, event` — PII redacted |
| Metrics | Prometheus client → Prometheus → Grafana | RED per endpoint/job, USE per resource, business KPIs |
| Traces | OpenTelemetry SDK (FastAPI, SQLAlchemy, httpx, Redis, ARQ) → Tempo | spans across API → worker → AI gateway |
| Errors | GlitchTip (Sentry SDK) backend + frontend | grouped exceptions with trace_id |
| Uptime | Uptime Kuma | public site, API health, webhook endpoint |
| LLM traces (opt.) | Langfuse | prompt/response traces with redaction |

## 2. Health endpoints
`/health/live` (process), `/health/ready` (DB, Redis, storage, AI gateway reachability), `/metrics` (internal only).

## 3. Key metrics
**Platform:** request rate/latency/errors, queue depth & job latency per queue, DLQ size, DB connections/slow queries, Redis memory, outbox lag.
**Business (PDF §17, §23, §24):** messages in/out, deterministic vs LLM ratio, cache-hit rate, tokens & cost per tenant/plan, **STT success rate & cost**, spam blocks, out-of-rule ignored count, handoff count & wait time, waiting-for-human count, quota remaining, orders created/confirmed, CSV import success rate, Meta send failures, token-expiry warnings.

## 4. Dashboards (Grafana)
1. Platform overview (golden signals) 2. Queues & workers 3. AI cost & usage (by provider/model/tenant tier) 4. Voice/STT quality 5. Conversations & handoff 6. Billing/subscriptions funnel 7. Errors (error_events by code).

## 5. Alerting (Grafana Alerting → email/Telegram/Slack)
| Alert | Condition |
|---|---|
| API error rate | 5xx > 2% for 5 min |
| Latency | p95 > 800 ms for 10 min |
| Webhook backlog | inbound queue lag > 60 s |
| DLQ growth | > N in 15 min |
| AI provider down | circuit open > 5 min |
| AI spend anomaly | hourly cost > 3× baseline / global budget 80% |
| STT failure rate | > 20% over 30 min |
| Meta token expiring | < 7 days |
| DB | disk > 80%, replication lag, backup failed |

## 6. SLOs (initial targets)
API availability 99.5% → 99.9% later; webhook-to-reply p95 (deterministic) < 5 s, (LLM) < 12 s; voice reply p95 < 20 s.

## 7. Correlation
`trace_id` generated at edge (or from `traceparent`), propagated into jobs, events, AI calls, error_events, audit_log and error envelope → one id finds everything.
