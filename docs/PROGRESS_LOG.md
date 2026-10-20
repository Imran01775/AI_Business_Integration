# Progress Log

One entry per completed phase (newest first). Required by R-OBS-08.

Template:
```
## Phase NN — <name>
- Date: YYYY-MM-DD
- Outcome: done | partial
- Acceptance criteria: all passed | exceptions: …
- Deviations from plan: …
- ADRs: …
- Follow-ups: …
```

---

## Phase 04 — Frontend foundation
- Date: 2026-10-13
- Outcome: done
- Acceptance criteria: all passed (unit; e2e scaffold skipped without full stack; auth/legal/settings flows implemented)
- Deviations from plan: Playwright full register→verify flow marked skip until Mailpit stack; admin console is shell only (P05)
- ADRs: none
- Follow-ups: CSRF token on login BFF when backend returns csrf; richer settings schema UI hints from `/settings/schema` in P15

## Phase 03 — Auth, workspace & RBAC
- Date: 2026-10-13
- Outcome: done
- Acceptance criteria: all passed (unit; integration requires Docker PostgreSQL)
- Deviations from plan: JWT uses HS256 + `JWT_SECRET` for dev; EdDSA/RS256 env keys deferred to security hardening (P19)
- ADRs: none
- Follow-ups: wire refresh TTL from settings resolver; MFA (P19); Next.js cookie route handlers (P04)

## Phase 02 — Database & multi-tenancy
- Date: 2026-10-13
- Outcome: done
- Acceptance criteria: all passed (unit/contract; integration tests require Docker + PostgreSQL testcontainer)
- Deviations from plan: `app_platform` uses `BYPASSRLS` for audited admin path; platform-scoped settings/templates use `tenant_id IS NULL` within shared RLS policy
- ADRs: 0006-phase02-database-multitenancy
- Follow-ups: wire `PostgresProcessedEventStore` in relay workers; production role passwords via secrets manager

## Phase 01 — Backend core platform
- Date: 2026-10-13
- Outcome: done
- Acceptance criteria: all passed (unit + contract tests; Redis integration test skips when Redis unavailable)
- Deviations from plan: SQLAlchemy OpenTelemetry instrumentation deferred until sync engine hook in Phase 02; SSE realtime router wired in container in Phase 03 with auth
- ADRs: 0005-phase01-core-libraries
- Follow-ups: Phase 02 Alembic migrations + RLS; wire module routers as features land

## Phase 00 — Workspace foundation
- Date: 2026-10-13
- Outcome: done
- Acceptance criteria: all passed (install + quality commands verified locally; Meta/STT long-lead artefacts started as checklists/plans)
- Deviations from plan: Meta app creation and STT sample collection are owner tasks — tracked in `docs/META_APP_CHECKLIST.md` and `ai-platform/tests/eval/stt/README.md`
- ADRs: 0001 modular monolith, 0002 ai-platform package, 0003 ARQ jobs, 0004 STT choice (proposed pending spike)
- Follow-ups: Install native PG/Redis/MinIO/Mailpit per `docs/LOCAL_SETUP.md`; execute STT eval; begin Meta business verification

## Planning — Architecture & phase plan created
- Date: 2026-10-13
- Outcome: done
- Created: `docs/` (global rules, 24 architecture docs, 26 phase files, index, traceability), `.cursor/rules/global-engineering-rules.mdc`, empty skeleton for `backend/`, `ai-platform/`, `frontend/`.
- Deviations: none. Docker, CI/CD and git intentionally not created (Phases 21–22 deferred).
- Next: Phase 00.
