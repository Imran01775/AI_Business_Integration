# Phase 08 — Usage Ledger & Quotas

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 08. Modules: `usage`, `billing` (top-up/overage link), `notifications`. No git/Docker.

## Goal
Meter everything (AI conversations, LLM tokens, STT seconds, cache hits, spam blocks) in an append-only UsageLedger; enforce per-plan quotas with 80% warning and configurable 100% behaviour (pause / soft handoff / top-up / overage / BYO key); fair-use (spam not counted); budgets visible.

## Prerequisites
Phases 05 (plans, top-ups), 07 (`ai.usage.recorded`).

## Requirements covered
PDF §8 quotas (80% warn, 100% pause/top-up/overage/BYO key, track tokens + STT cost), §24 (included quota + fair-use, meter STT/LLM separately or one allowance, quota end ≠ fake customer, track tokens, STT units, cache_hits, spam_blocks, budget_remaining), §27.3.

## Scope
**In:** ledger, quota counters per billing period, "AI conversation" definition (configurable: conversation-day or reply count), metering modes (separate STT allowance or unified), quota check facade used by pipeline, threshold events, top-up application, overage accounting, usage APIs + seller usage page + admin usage explorer.
**Out:** pipeline integration (P12/P13 call the facade).

## Tasks
1. Domain: `UsageLedgerEntry(kind, quantity, unit_cost, cost, ref, period)`, `QuotaCounter`, `QuotaPolicy` (from entitlements + settings), `UsageKind` enum: `ai_conversation`, `llm_tokens_in/out`, `stt_seconds`, `stt_requests`, `embedding_tokens`, `cache_hit`, `spam_block`, `topup_credit`.
2. Consumers: `ai.usage.recorded`, `guard.message.rejected` (spam_block — not counted toward quota), `answering.reply.generated` (conversation counting, cache_hit).
3. Facade: `UsageFacade.check(tenant, kind) -> QuotaDecision(allowed, remaining, mode)` (Redis counters, PG source of truth), `UsageFacade.consume(...)`.
4. Thresholds: emit `usage.quota.threshold_reached` at `usage.warn_threshold_percent` (default 80) and 100%; notifications to owner (+ users who subscribed).
5. 100% behaviours per `usage.on_exhausted`: `pause_ai`, `soft_handoff` (template `usage.exhausted_message`), `auto_topup` (if payment method on file — later), `overage` (if entitlement), `byo_key` (if configured).
6. Period rollover cron; budgets view (`budget_remaining`).
7. Seller web: usage page (quota bars, STT usage, cache-hit rate, spam blocks, cost estimate), top-up purchase CTA; admin: usage explorer per tenant/plan.

## DB changes
`usage_ledger` (partition-ready), `quota_counters`, `budget_caps`, `overage_charges`.

## Settings & templates
Platform/plan: quotas, `usage.metering_mode` (`unified|separate_stt`), `usage.conversation_definition`. Tenant: `usage.warn_threshold_percent`, `usage.on_exhausted`, template `usage.exhausted_message`, `usage.warning_notification`.

## Tests
Counting correctness under concurrency; spam excluded; thresholds fire once per period; each 100% mode; rollover; tenant isolation.

## Acceptance criteria
- [ ] Ledger shows LLM tokens, STT seconds, cache hits, spam blocks per tenant
- [ ] 80% warning sent once; 100% applies configured behaviour
- [ ] Quota exhausted never produces a fake answer (soft handoff template)

## Rules checklist
- [ ] R-AI-05/06 · R-CFG-01 · R-EVT-02 · R-DB-04 · tests · PROGRESS_LOG · no git/Docker
