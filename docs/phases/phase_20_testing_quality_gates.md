# Phase 20 — Testing & Quality Gates (full suites)

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 20. Unit/integration/contract tests were written in every phase; this phase completes cross-cutting suites. No git/Docker.

## Goal
Confidence for production: full e2e journeys, load/soak, chaos-lite, contract/OpenAPI checks, coverage targets, one-command local quality gate.

## Prerequisites
Phases 00–19.

## Requirements covered
Chat: testing strategy, independently testable components. Doc 14.

## Scope
**In:** Playwright e2e for all critical journeys, backend e2e API suites, tenant-isolation sweep across all modules, load tests (k6 or Locust) for webhook → reply path and inbox, soak test (2 h), failure injection (AI provider down, Redis restart, Meta 5xx), OpenAPI breaking-change diff, migration up/down on prod-sized data, coverage enforcement, `make`-like task runner (`just`/`task` or scripts) for the full gate.

## Tasks
1. Journeys: visitor → pricing → signup → subscription → admin approve/verify → active; connect sandbox → CSV import → rules → persona → chat (text + voice) → handoff/take-over → order confirm → learning approve → analytics.
2. Tenant isolation sweep generated from route registry (every tenant endpoint called with foreign ids → 404/403).
3. Load: target e.g. 50 inbound msgs/s, p95 targets doc 12 §6; identify bottlenecks; record results.
4. Failure injection scenarios + expected degradation (soft handoff, retries, DLQ).
5. Quality gate script: lint, types, import-linter, tests, coverage, audits, OpenAPI diff.

## Acceptance criteria
- [ ] All journeys green; coverage targets met (R-TEST-01)
- [ ] Load targets met or tuned with ADR
- [ ] Failure scenarios degrade gracefully

## Rules checklist
- [ ] R-TEST-01..07 · PROGRESS_LOG · no git/Docker
