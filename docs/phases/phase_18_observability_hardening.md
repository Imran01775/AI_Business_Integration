# Phase 18 — Observability Hardening

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 18. Basics (logs, trace_id, metrics endpoint, error envelope, error_events) exist since Phase 01–02. No Docker files yet — run tools natively or document configs.

## Goal
Complete monitoring per doc 12 and error/history per doc 22: dashboards, alerts, SLOs, end-to-end trace correlation, admin error tooling.

## Prerequisites
Phases 01–17.

## Requirements covered
Chat: monitoring & observability. PDF §15 monitoring, §17 metrics. Docs 12, 22.

## Scope
**In:** Prometheus scrape config, Grafana dashboards 1–7 (as JSON in `docs/observability/dashboards/`), alert rules, Loki/Tempo configuration docs, GlitchTip projects (backend, web), Uptime Kuma checks, Langfuse optional, trace propagation verified across API → worker → AI gateway, business metrics instrumentation review, admin error/DLQ tools polish, runbooks for top alerts.
**Out:** containerized deployment of the stack (Phase 21/23).

## Tasks
1. Instrumentation audit: every module exports RED metrics; every job has duration/failure metrics; AI metrics (tokens, cost, cache-hit) labeled by tenant tier (not tenant id for cardinality).
2. Dashboards + alert rules (doc 12 §4–5) committed as files.
3. SLO definitions + error budget panel.
4. Trace correlation test: single trace_id links webhook → pipeline → AI → send → error_event.
5. Runbooks: `docs/runbooks/` (API errors, queue backlog, AI provider outage, Meta token expiry, DB disk, DLQ growth).

## Acceptance criteria
- [ ] One trace_id finds logs, trace, error event and audit for a message
- [ ] Alerts fire in a simulated failure (provider down, queue backlog)
- [ ] Dashboards show PDF business metrics

## Rules checklist
- [ ] R-OBS-01..08 · PROGRESS_LOG · no git/Docker
