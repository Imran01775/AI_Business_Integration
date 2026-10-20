# Phase 17 — Analytics, Metrics & Data Export

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 17. Module: `analytics` (read models). No git/Docker.

## Goal
Business metrics for sellers and the platform from event-fed read models; data export.

## Prerequisites
Phases 08–16 (events exist).

## Requirements covered
PDF §17 metrics (incl. STT success rate & cost), §23 widgets, §24 (tokens, STT units, cache_hits, spam_blocks, budget_remaining), Phase 2 "richer analytics" groundwork.

## Scope
**In:** event consumers → `daily_tenant_metrics`, `platform_daily_metrics`; seller analytics page (messages, deterministic vs LLM ratio, cache-hit, cost, STT success/cost, handoffs & wait time, out-of-rule ignored, spam blocked, orders & conversion, top asked products/questions); admin platform dashboard (tenants by status, MRR estimate from plans, AI cost vs revenue per plan, provider mix, error rates); CSV export jobs (conversations, orders, products, usage) with expiring download links.
**Out:** BI tooling (Metabase optional later, OSS).

## Tasks
1. Read-model consumers (idempotent), nightly rollup + near-real-time counters (Redis).
2. Analytics API (date range, granularity) with caching.
3. Web: seller analytics (Recharts), admin platform dashboard.
4. Export jobs (`import` queue) → object storage → signed URL, retention `retention.exports_days`; formula-injection safe CSV.

## DB changes
`daily_tenant_metrics`, `platform_daily_metrics`, `export_jobs`.

## Tests
Metric correctness from replayed event fixtures; exports tenant-scoped; large export performance.

## Acceptance criteria
- [ ] Seller sees cost, cache-hit, STT success, handoff and order metrics
- [ ] Admin sees platform health and AI cost vs plan revenue
- [ ] Exports download and expire

## Rules checklist
- [ ] R-EVT-02 · R-TEN-04 · R-PERF-03 · tests · PROGRESS_LOG · no git/Docker
