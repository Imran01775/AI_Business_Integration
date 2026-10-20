# GLOBAL ENGINEERING RULES — AI Sales Agent Platform

> **Status:** MANDATORY. These rules apply by default to **every** command, prompt, implementation task, feature request, architectural decision, code review and generated artefact.
> If a task conflicts with a rule, **stop and raise it** — do not silently break a rule. A rule can only be changed through an ADR (`docs/adr/`).

Rule IDs (e.g. `R-ARCH-01`) must be referenced in PR descriptions, ADRs and code reviews when relevant.

---

## 0. How to use these rules

- Every implementation prompt implicitly starts with: *"Apply docs/GLOBAL_RULES.md."*
- Every phase file ends with a **Rules Checklist** — all items must pass before a phase is marked done.
- Priority order when rules compete: **Security > Tenant isolation > Correctness > Maintainability > Performance > Cost > Convenience.**

---

## 1. Architecture (R-ARCH)

| ID | Rule |
|----|------|
| R-ARCH-01 | The backend is a **modular monolith**. Each business capability is a module under `backend/src/app/modules/<module>/`. |
| R-ARCH-02 | Each module has 4 layers: `domain` → `application` → `infrastructure` / `api`. Dependencies point **inward only**. `domain` imports nothing from frameworks (no FastAPI, no SQLAlchemy, no Redis). |
| R-ARCH-03 | Modules communicate **only** through (a) the other module's public `application` interface (facade/service port) or (b) domain events. **Never** import another module's `domain`, `infrastructure` or ORM models. Enforced by `import-linter`. |
| R-ARCH-04 | Every external system (DB, Redis, LLM, STT, Meta, payment, email, storage) sits behind a **port (interface)** with one or more **adapters**. Business code depends on ports only. |
| R-ARCH-05 | Each module owns its own tables. No module reads/writes another module's tables directly. Cross-module data = API call or event-fed read model. |
| R-ARCH-06 | Design every module so it can be **extracted into a microservice** without changing its domain/application code (only the adapter of the caller changes from in-process to HTTP/event). |
| R-ARCH-07 | No premature microservices. Extraction needs an ADR with a measured reason (scale, team ownership, isolation). |
| R-ARCH-08 | Composition root (`backend/src/app/main/`) is the **only** place that wires adapters to ports (dependency injection). |
| R-ARCH-09 | Prefer composition over inheritance, small interfaces (ISP), SOLID, explicit over implicit. |
| R-ARCH-10 | Every architectural decision (new library, new pattern, new infra component, rule change) requires an ADR in `docs/adr/NNNN-title.md`. |

## 2. Multi-tenancy (R-TEN)

| ID | Rule |
|----|------|
| R-TEN-01 | Every tenant-owned table has a non-null `tenant_id` column, indexed, and a PostgreSQL **Row-Level Security** policy. |
| R-TEN-02 | Every query runs inside a tenant context (`SET app.tenant_id`). Repositories must require a `TenantContext`; no "global" repository methods except in explicitly marked platform-admin code. |
| R-TEN-03 | Cache keys, storage paths, queue payloads, logs and metrics carry `tenant_id`. Cache key format: `t:{tenant_id}:{module}:{entity}:{id}:v{n}`. |
| R-TEN-04 | **No cross-tenant learning, retrieval, caching or analytics** — ever. RAG retrieval always filters by `tenant_id`. |
| R-TEN-05 | Every tenant-scoped feature has an automated **tenant-isolation test** (tenant A cannot read/modify tenant B). |

## 3. AI / LLM (R-AI)

| ID | Rule |
|----|------|
| R-AI-01 | Business code calls AI **only** through the `AIClient` port (`ai_platform.client`). Never import a provider SDK (openai, anthropic, google, etc.) outside `ai-platform/src/ai_platform/providers/`. |
| R-AI-02 | **Deterministic first:** Guard → Seller Rules → DB → FAQ → Cache must run **before** any LLM call. The LLM is the last resort. |
| R-AI-03 | Out-of-rule, blocked, closed, spam or empty-transcript messages **never** reach the LLM or costly retrieval. |
| R-AI-04 | Never send full conversation history. Use a bounded short-memory window (configurable) + tool/DB facts. |
| R-AI-05 | Every AI call (LLM, STT, embeddings) records: tenant_id, provider, model, prompt key + version, input/output tokens or STT units, cost, latency, cache hit, trace_id → `ai_requests` + `UsageLedger`. |
| R-AI-06 | Every AI call checks **quota and budget before** execution and respects the global + tenant **kill switch**. |
| R-AI-07 | Prompts are **never hardcoded** in business code. They live in the prompt registry with a key, version, locale and variables schema. A new prompt version must pass the evaluation harness before promotion. |
| R-AI-08 | Every LLM output that states a fact (price, stock, discount, delivery, policy) passes the **Safety Validator** against DB data. `min_price` can never be violated. Orders always require customer confirmation. |
| R-AI-09 | Voice transcripts enter the **same** text pipeline. No parallel LLM path for voice. |
| R-AI-10 | AI providers must have timeout, retry with backoff, circuit breaker and fallback route. Provider failure must degrade to soft handoff, never a fake answer. |
| R-AI-11 | The AI must never invent facts. If grounded data is missing → say so / hand off. |

## 4. Configuration (R-CFG)

| ID | Rule |
|----|------|
| R-CFG-01 | **No business value is hardcoded.** Thresholds, limits, timers, texts, prices, model names, provider choices, quotas and feature availability come from the **settings resolver**, **template store**, **entitlements** or **prompt registry**. |
| R-CFG-02 | Every setting is declared once in the settings registry with: key, scope (`tenant` chain or `user` chain), type/JSON schema, default, min/max bounds, overridable layers, edit role, required entitlement, `is_secret`. |
| R-CFG-03 | Business chain: `code default → platform → plan → tenant → channel → conversation`. User chain: `code default → platform → user`. The chains never mix. |
| R-CFG-04 | Lower layers are **clamped** to bounds set by upper layers (platform/plan). |
| R-CFG-05 | Every customer-facing text is a **message template** (per locale, versioned). |
| R-CFG-06 | Secrets (API keys, page tokens, payment keys, BYO keys) are stored only in the encrypted secrets store, never in settings, logs, responses or the frontend. |
| R-CFG-07 | Every settings change is audited, versioned and rollback-able, and emits `settings.changed` to invalidate caches. |
| R-CFG-08 | Infrastructure config (DB URL, Redis URL, etc.) comes from environment variables validated by a typed `Settings` class at startup. Fail fast on invalid config. |

## 5. API design (R-API)

| ID | Rule |
|----|------|
| R-API-01 | **API-first.** OpenAPI is the single contract. All features must be usable through the public API alone (web and future mobile). |
| R-API-02 | Versioned under `/api/v1`. Breaking changes require a new version and a deprecation period. |
| R-API-03 | Resource-oriented REST, plural nouns, kebab-case paths, snake_case JSON fields. |
| R-API-04 | Standard error envelope: `{ "error": { "code", "message", "details", "trace_id" } }`. Clients translate by `code`. No stack traces to clients. |
| R-API-05 | Cursor-based pagination (`?cursor=&limit=`), `updated_since` filter for delta sync on list endpoints. |
| R-API-06 | `Idempotency-Key` header required on POST that create money/orders/messages; webhooks are de-duplicated by provider event id. |
| R-API-07 | Every endpoint works for both **cookie auth (web)** and **Bearer auth (mobile)**. |
| R-API-08 | Request/response schemas are Pydantic models in the module's `api` layer; never expose ORM models. |
| R-API-09 | Every endpoint declares required permission and entitlement explicitly. |

## 6. Data & database (R-DB)

| ID | Rule |
|----|------|
| R-DB-01 | Schema changes **only** via Alembic migrations. No manual DDL in any environment. |
| R-DB-02 | Migrations are backward compatible (**expand → migrate → contract**). Never drop/rename a column in the same release that stops using it. |
| R-DB-03 | Primary keys: UUIDv7. Every table has `created_at`, `updated_at` (timestamptz, UTC). Soft delete (`deleted_at`) for user-facing entities. |
| R-DB-04 | Money stored as `NUMERIC(14,2)` + currency code. Never float. |
| R-DB-05 | Every foreign key and every filter column used in hot queries has an index. Every new query on a large table is checked with `EXPLAIN`. |
| R-DB-06 | Status changes on Subscription, Conversation, Order, Handoff write a row to the matching `*_status_history` table. |
| R-DB-07 | Versioned entities (products import batches, rules, prompts, knowledge, settings, templates) keep history and support rollback. |
| R-DB-08 | Cross-module side effects use the **transactional outbox** (same transaction as the state change). |

## 7. Security (R-SEC)

| ID | Rule |
|----|------|
| R-SEC-01 | Deny by default. Every endpoint requires authentication unless explicitly marked public. |
| R-SEC-02 | Passwords: Argon2id. Access tokens short-lived (≤15 min); refresh tokens rotated with reuse detection. |
| R-SEC-03 | All webhooks verify signatures (Meta `X-Hub-Signature-256`, payment gateways). Reject unsigned/invalid requests. |
| R-SEC-04 | Validate all input at the boundary (Pydantic/Zod). Validate uploads (type, size, duration, content sniffing). |
| R-SEC-05 | No PII or secrets in logs. Redaction is applied by the logging pipeline and by the learning queue. |
| R-SEC-06 | Least privilege: RBAC + tenant policies; admin impersonation is time-boxed and fully audited. |
| R-SEC-07 | Rate limiting on auth, public, webhook and AI-triggering endpoints. |
| R-SEC-08 | Dependencies pinned and scanned; no package with known critical CVE ships. |
| R-SEC-09 | Encrypt secrets at rest (envelope encryption, key from env/KMS); TLS everywhere outside localhost. |
| R-SEC-10 | Data retention and deletion policies (incl. audio + transcripts) are enforced by scheduled jobs. |

## 8. Error handling, logging & history (R-OBS)

| ID | Rule |
|----|------|
| R-OBS-01 | Never swallow exceptions. Catch only to add context, convert to a typed error, or handle meaningfully. |
| R-OBS-02 | Use the typed error catalogue (`DomainError`, `NotFoundError`, `PermissionDeniedError`, `ValidationError`, `ConflictError`, `QuotaExceededError`, `ExternalProviderError`, …) with stable `error_code`s. |
| R-OBS-03 | Structured JSON logs only (structlog) with `trace_id`, `request_id`, `tenant_id`, `module`. No `print`. |
| R-OBS-04 | Business-relevant failures (webhook, STT, LLM, payment, CSV row, job) are persisted in `error_events` with code and retry state. |
| R-OBS-05 | Every write use case emits an **audit entry** (who, what, when, tenant, before/after). |
| R-OBS-06 | Every module exposes metrics (RED: rate, errors, duration) and is traced with OpenTelemetry. |
| R-OBS-07 | Failed background jobs go to a dead-letter queue + `job_failures`, visible and retryable by admin. |
| R-OBS-08 | Every completed phase is recorded in `docs/PROGRESS_LOG.md`; every user-visible change in `docs/CHANGELOG.md`. |

## 9. Testing (R-TEST)

| ID | Rule |
|----|------|
| R-TEST-01 | Every use case has unit tests; domain + application coverage ≥ 80%, critical paths (guard, rules, engine, billing, quota, safety) ≥ 90%. |
| R-TEST-02 | Every adapter has a **contract test** against its port (fake + real/integration variant). |
| R-TEST-03 | Every module is testable in isolation using in-memory fakes of its ports. No test depends on another module's internals. |
| R-TEST-04 | Integration tests use real PostgreSQL + Redis (Testcontainers or local services), never SQLite substitutes. |
| R-TEST-05 | AI is tested with deterministic fake providers; prompt changes run the evaluation harness (golden sets, bn + en). |
| R-TEST-06 | Every bug fix adds a regression test. |
| R-TEST-07 | Tests are deterministic: no real network, fixed clocks (inject `Clock`), seeded randomness. |

## 10. Code quality (R-CODE)

| ID | Rule |
|----|------|
| R-CODE-01 | Python 3.12, full type hints, `mypy --strict`, `ruff` (lint + format) clean. |
| R-CODE-02 | TypeScript `strict: true`, ESLint + Prettier clean, no `any` without a justified comment. |
| R-CODE-03 | Async I/O end-to-end in the backend; no blocking calls in the event loop (CPU-heavy work → worker). |
| R-CODE-04 | Functions do one thing; files stay focused; no god classes or "utils" dumping grounds. |
| R-CODE-05 | Naming: Python `snake_case`, classes `PascalCase`; TS components `PascalCase`, hooks `useX`; DB tables plural `snake_case`. |
| R-CODE-06 | Comments explain constraints and "why", not "what". Public interfaces have docstrings. |
| R-CODE-07 | No dead code, no commented-out code, no TODO without an issue reference. |
| R-CODE-08 | Dependencies: prefer free and open-source; every new dependency needs justification (license, maintenance, size). |

## 11. Frontend & clients (R-FE)

| ID | Rule |
|----|------|
| R-FE-01 | **No business rules in any client.** Clients render, validate input shape and call the API. |
| R-FE-02 | API access only via the generated client in `frontend/packages/api-client`. No hand-written fetch for API endpoints. |
| R-FE-03 | Feature-sliced structure: `src/features/<feature>/{components,hooks,api,schemas}`; shared code only in `src/shared` or `frontend/packages/*`. Features don't import each other's internals. |
| R-FE-04 | All UI text through i18n (`frontend/packages/i18n`, bn + en). No hardcoded user-facing strings. |
| R-FE-05 | Server state via TanStack Query; forms via react-hook-form + Zod; no global mutable stores for server data. |
| R-FE-06 | Accessibility: WCAG 2.1 AA, keyboard navigable, semantic HTML. |
| R-FE-07 | Settings UIs are schema-driven from `GET /api/v1/settings/schema`. |
| R-FE-08 | Shared packages (`api-client`, `shared`, `i18n`, `design-tokens`) must stay platform-neutral so the future mobile app (`frontend/apps/mobile`) can reuse them. |

## 12. Events & background jobs (R-EVT)

| ID | Rule |
|----|------|
| R-EVT-01 | Events are past-tense facts: `<module>.<entity>.<verb_past>` (e.g. `catalogue.product.updated`), versioned schema, with `event_id`, `tenant_id`, `occurred_at`, `trace_id`. |
| R-EVT-02 | Consumers are **idempotent** (dedupe by `event_id`). |
| R-EVT-03 | Jobs are small, idempotent, retryable with backoff, have a timeout, and carry `tenant_id` + `trace_id`. |
| R-EVT-04 | Anything slower than ~300 ms or calling external providers (STT, LLM, Meta send, CSV import, email) runs in a worker, not in the request path (except the synchronous sandbox simulator if explicitly designed). |

## 13. Performance & cost (R-PERF)

| ID | Rule |
|----|------|
| R-PERF-01 | API p95 < 300 ms for CRUD endpoints; webhook ACK < 1 s (process async). |
| R-PERF-02 | No N+1 queries; list endpoints paginated with bounded `limit`. |
| R-PERF-03 | Cache what is read-heavy and tenant-scoped, with explicit invalidation on change events. |
| R-PERF-04 | Every new AI feature includes a cost estimate (tokens/STT units per conversation) in its phase/ADR. |

## 14. Process (R-PROC)

| ID | Rule |
|----|------|
| R-PROC-01 | Implement phases **in order**. A phase is done only when its Acceptance Criteria and Rules Checklist pass. |
| R-PROC-02 | Each feature phase is a **vertical slice**: domain + API + web UI + tests + settings + docs. |
| R-PROC-03 | Every new capability ships behind a feature flag/entitlement until verified. |
| R-PROC-04 | **No git push, git commits, Docker, CI/CD files or deployment actions unless the current phase/command explicitly requests it.** |
| R-PROC-05 | Do not modify files outside the scope of the current task. Do not touch `requirements.txt` (legacy, ignored). |
| R-PROC-06 | When requirements are ambiguous, ask before implementing. When a requirement conflicts with these rules, raise it. |

---

## Default prompt header (copy into every task)

```
Apply docs/GLOBAL_RULES.md (all rules mandatory).
Phase: <phase file>   Module(s): <modules>
Constraints: modular monolith, ports & adapters, tenant isolation + RLS,
AI only via AIClient (deterministic first), no hardcoded business values (settings/templates),
API-first (web + mobile), typed errors + audit + trace_id, tests for every use case,
no git/docker actions unless requested.
```
