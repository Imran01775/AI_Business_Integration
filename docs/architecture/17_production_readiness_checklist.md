# 17 — Production-Readiness Checklist

> Apply `docs/GLOBAL_RULES.md`. Every item must be ✅ before go-live (Phase 23).

## Product (PDF v1.5 MVP)
- [ ] Public site, feature matrix, plans, public catalogue live
- [ ] Auth, workspace, multi-tenant isolation verified (isolation test suite green)
- [ ] Subscription request → admin review → payment verification → Active; all statuses incl. Past Due/Suspended/Expired automated
- [ ] Messenger: page connect, webhook signature, 24h window, data-deletion callback, Meta app review approved
- [ ] Manual catalogue + CSV (template, dry-run, duplicates, rich columns, external_id)
- [ ] Seller Conversation Rules (keyword gate, no generative LLM)
- [ ] Voice: validate → STT → same pipeline; out-of-rule ignored; STT metered
- [ ] Token-efficient engine (DB → Rules → FAQ → Cache → LLM), cache invalidation on product change
- [ ] Handoff state machine (no double reply), lifecycle statuses, Abuse Guard thresholds
- [ ] Learning queue + rollback; no cross-tenant learning
- [ ] Order capture + customer confirmation; `min_price` enforced
- [ ] UsageLedger, quotas, 80% warning, 100% behaviour, top-up/overage
- [ ] Seller Panel: Status, Responder, Urgency, voice badge, transcript toggle, Take-over, widgets
- [ ] Admin console, audit log, plan management, role separation
- [ ] Privacy, Terms, retention (audio/transcript), sandbox
- [ ] Hooks for store sync reserved

## Configuration
- [ ] All business values come from settings/templates (no hardcoded values — code search check)
- [ ] Platform defaults + bounds seeded; templates seeded bn + en
- [ ] Settings schema API drives settings UIs

## Security
- [ ] OWASP ASVS L2 checklist subset passed; ZAP baseline clean
- [ ] Secrets in encrypted store; master key rotation procedure tested
- [ ] MFA for platform admins + owners (optional for owners)
- [ ] Rate limits on auth/webhook/public endpoints
- [ ] Dependency scans clean (no critical CVEs)
- [ ] Impersonation audited and time-boxed

## Reliability
- [ ] Backups + PITR configured; **restore drill done**
- [ ] Health/readiness probes; graceful shutdown for workers
- [ ] DLQ visible + replay works; retries/backoff tuned
- [ ] AI provider fallback + circuit breaker tested; kill switch tested
- [ ] Load test: target peak (e.g. 50 msg/s) with p95 targets met

## Observability
- [ ] Logs, metrics, traces, errors flowing with trace_id correlation
- [ ] Dashboards 1–7 (doc 12) and alerts configured, alert routing tested
- [ ] Uptime monitoring for site, API, webhook

## Data & compliance
- [ ] Retention jobs active; deletion callback tested end-to-end
- [ ] Data export works for tenants
- [ ] Terms/Privacy acceptance recorded

## Operations
- [ ] Runbooks: incident, deploy, rollback, restore, secret rotation, provider outage, Meta token expiry
- [ ] On-call/alert contacts defined
- [ ] `docs/PROGRESS_LOG.md` and `docs/CHANGELOG.md` up to date; ADRs complete
