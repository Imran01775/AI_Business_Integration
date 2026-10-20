# 14 — Testing Strategy

> Apply `docs/GLOBAL_RULES.md` (esp. R-TEST-*).

## 1. Test pyramid
| Level | Scope | Tools | Where |
|---|---|---|---|
| Unit | domain + application with in-memory fakes | pytest, hypothesis | `backend/tests/unit/<module>/` |
| Contract | each adapter satisfies its port (fake and real) | pytest parametrized suites, respx fixtures | `backend/tests/contract/`, `ai-platform/tests/contract/` |
| Integration | repositories, RLS, outbox, jobs with real PG/Redis/MinIO | testcontainers / local services | `backend/tests/integration/` |
| API / e2e backend | HTTP flows via httpx AsyncClient | pytest | `backend/tests/e2e/` |
| Frontend unit | components/hooks | Vitest, Testing Library, MSW | `frontend/apps/web/tests/unit/` |
| Frontend e2e | critical user journeys | Playwright | `frontend/apps/web/tests/e2e/` |
| AI evaluation | prompts, routing, RAG quality (bn/en/banglish) | eval harness | `ai-platform/tests/eval/` |
| Non-functional | load, soak, security | k6 / Locust, OWASP ZAP baseline | phase 20 |

## 2. Mandatory suites
- **Tenant isolation** suite per tenant-scoped module (R-TEN-05).
- **Pipeline decision table tests** for Guard + Seller Rules (PDF §27.2 cases: forbidden hit, not-allowed first times, threshold exceeded, STT garbage).
- **State machine tests** (subscription, conversation lifecycle, handoff, order) — property-based: no invalid transition, no AI+human double reply.
- **Safety validator tests**: price/stock/discount mismatch, `min_price` violation.
- **CSV import tests**: template, dry-run classification (create/update/skip/error), duplicate rules (sku first, else name+variant), rich columns, malformed files, large files.
- **Quota/usage tests**: 80% warning, 100% behaviours, fair-use exclusion of spam, STT metering.
- **Settings resolver tests**: layering, clamping to bounds, scope separation (tenant vs user), entitlement gating.
- **Webhook tests**: signature validation, dedupe, 24h window behaviour.

## 3. Test data & fakes
Factories (polyfactory) per aggregate; fakes for every port in `backend/tests/fakes/`; `FakeClock`; deterministic `FakeLLMProvider` (scripted responses), `FakeSTTProvider` (transcript + confidence), `FakeChannelAdapter`.

## 4. Quality gates (local now, CI later)
ruff, mypy strict, import-linter, pytest (coverage ≥ 80% domain/application; ≥ 90% critical modules), ESLint, tsc, Vitest, Playwright smoke, `pip-audit`/`pnpm audit`, OpenAPI diff check (no unintended breaking changes), migration up/down check.

## 5. Definition of done (per phase)
All new use cases tested; contract tests for new adapters; tenant-isolation tests updated; e2e for new critical journeys; acceptance criteria demonstrated in sandbox; Rules Checklist passed.
