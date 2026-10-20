# Phase 15 — Seller Panel (Status, Urgency, Take-over) & Settings Centre

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 15. Area: web `(seller)`, modules `conversations` (urgency), `notifications`, `settings`, `tenancy` (onboarding). No git/Docker.

## Goal
A real-time, mobile-friendly seller workspace: inbox with Status, Responder, Urgency, Last activity, media type, Take-over; widgets; canned replies; notification centre; onboarding wizard with health checklist; unified Seller Settings Centre.

## Prerequisites
Phases 09–14.

## Requirements covered
PDF §11.14, §23 (per conversation: Status, Responder AI/Human/Waiting, Urgency, Last activity, media type text/voice, Take-over; widgets: waiting-for-human, remaining quota, cache-hit, STT usage, blocked today), §2 human control. Doc 24 (Settings Centre).

## Scope
**In:** urgency scoring service, realtime inbox (SSE), conversation view (messages, transcript toggle, answer traces, orders, customer info), take-over/resume/assign/block/close actions, canned replies (with variables), suggest-mode drafts approval, widgets, notification centre (in-app list, read state, preferences link), onboarding wizard (connect page → load products → set rules → persona → test in sandbox → go live) with health checklist, Settings Centre (all business settings grouped, schema-driven, role-aware).
**Out:** analytics deep dives (P17).

## Tasks
1. Urgency: score = weighted(wait time since last customer msg, handoff requested, order intent, VIP flag, negative sentiment keyword list) with `urgency.weights`; recomputed on events + every minute for waiting conversations; level badges.
2. Inbox UI: virtualized list, filters (status, responder, urgency, media type, assigned to me), sort by urgency/last activity, unread counts, sound alerts (user setting).
3. Conversation UI: timeline (text/voice with badge + player + transcript toggle), AI decision badges (ignored/redirected/answered by DB/FAQ/LLM), composer with canned replies, take-over banner, keyboard shortcuts.
4. Widgets: waiting-for-human, remaining quota, cache-hit rate, STT usage, blocked today, orders today.
5. Canned replies CRUD (tenant), insert with variables.
6. Notification centre + preference shortcuts (user chain).
7. Onboarding wizard + `onboarding_states` health checklist visible until complete.
8. Settings Centre: groups from registry (`ui.group`), shows inherited value/bounds/source layer, reset-to-default, history + rollback.

## DB changes
`canned_replies`, `customer_flags` (VIP), extend `onboarding_states`.

## Settings & templates
Tenant: `urgency.weights`, `urgency.levels`, `inbox.default_filters`. User: `user.sound_alerts`, `user.inbox_default_view`, `user.inbox_filters`, `user.reply_signature`.

## Tests
Urgency scoring unit tests; realtime e2e (message arrives without refresh); take-over race e2e; settings centre shows correct inherited source; role-based visibility (agent read-only settings).

## Acceptance criteria
- [ ] New message appears in < 2 s without reload, ordered by urgency
- [ ] Take-over from panel prevents any AI reply
- [ ] New seller can complete onboarding wizard to go-live
- [ ] All business settings editable in Settings Centre per role

## Rules checklist
- [ ] R-FE-01..08 · R-CFG-02/03/07 · a11y · i18n · tests · PROGRESS_LOG · no git/Docker
