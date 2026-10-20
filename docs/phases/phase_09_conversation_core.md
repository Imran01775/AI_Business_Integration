# Phase 09 — Conversation Core, Channel Interface & Sandbox

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 09. Modules: `customers`, `conversations`, `channels` (interface + sandbox adapter). No git/Docker.

## Goal
The heart of messaging, independent of Meta: customers, conversations, messages, lifecycle + handoff state machines, idle/close scheduler, channel adapter interface, **sandbox simulator channel** (seller can test the bot in the browser), and the inbound pipeline skeleton with pluggable stages.

## Prerequisites
Phases 06–08.

## Requirements covered
PDF §8 state machine prevents AI+human double reply, §9 handoff + pause/resume, §11.15 sandbox, §22 statuses ACTIVE | HUMAN_HANDOFF | IDLE | CLOSED | BLOCKED, §15 pipeline shape. Doc 20 §3–§5.

## Scope
**In:** Customer + CustomerIdentity, Conversation aggregate (status, responder, ai_paused, counters, urgency placeholder, version), Message (direction, media_type text/voice/image, body, attachments), state machines + history, handoff events, `ChannelAdapter` port (`parse_inbound`, `send`, `capabilities`, `messaging_window`), `SandboxChannelAdapter`, inbound pipeline orchestrator with `PipelineStage` interface (stages registered: store → [voice slot] → guard slot → rules slot → engine slot → safety slot → send), outbound message service with responder check at send time, idle/close cron, basic inbox API.
**Out:** Messenger adapter (P10), guard/rules logic (P11), engine (P12), voice (P13), rich panel UI (P15).

## Tasks
1. Domain + invariants: one open conversation per customer per channel connection; status transitions only via domain methods; auto-reply allowed only if `responder == AI and not ai_paused and status == ACTIVE` at send time (optimistic lock).
2. Handoff use cases: RequestHandoff, TakeOver, ResumeAI, Assign, Block, Unblock, Close, Reopen — each writes history + audit + realtime event.
3. Pipeline orchestrator: per-conversation sequential processing (Redis lock), stage results (`continue | reply | stop | handoff`), `guard_decisions`/`answer_traces` hooks, trace_id propagation.
4. `channels`: `ChannelAdapter` port, registry by channel type, `ChannelConnection` aggregate (generic), outbound queue `outbound`.
5. Sandbox adapter: web chat simulator (`/api/v1/sandbox/conversations/{id}/messages`) behaving like a channel (customer side) + SSE replies; marked `is_sandbox` (excluded from billing quota optionally via `usage.count_sandbox`).
6. Lifecycle cron: ACTIVE → IDLE after `lifecycle.idle_after_minutes`; IDLE → CLOSED after `lifecycle.close_after_hours`; reopen on new customer message per `lifecycle.reopen_policy`.
7. Inbox API: list conversations (filters: status, responder, assigned, media type, urgency), conversation detail with messages (cursor), staff reply endpoint (forces HUMAN responder).
8. Web: minimal inbox + conversation view + sandbox simulator page (full panel in P15).

## DB changes
`customers`, `customer_identities`, `conversations`, `messages` (partition-ready), `conversation_status_history`, `handoff_events`, `guard_decisions`, `answer_traces`, `channel_connections` (generic), `webhook_events`, `outbound_messages`.

## Settings & templates
Tenant: `lifecycle.idle_after_minutes`, `lifecycle.close_after_hours`, `lifecycle.reopen_policy`, `conversations.assignment_strict`, `usage.count_sandbox`. Templates: `conversations.handoff_ack` (customer-facing when handed off).

## Tests
Property tests for state machines; concurrency test: AI reply and human take-over racing → never both sent; pipeline stage ordering; sandbox end-to-end; idle/close timers with FakeClock; tenant isolation.

## Acceptance criteria
- [ ] Seller chats with own bot in sandbox (echo/placeholder engine), sees messages in inbox
- [ ] Take-over stops AI immediately; resume returns control
- [ ] Idle/close transitions happen per settings; history recorded

## Rules checklist
- [ ] R-ARCH-04 (channel port) · R-DB-06 · R-EVT-02/04 · R-AI-03 slots · tests · PROGRESS_LOG · no git/Docker
