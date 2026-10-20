# Phase 10 — Facebook Messenger Channel

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 10. Module: `channels` (Messenger adapter). No git/Docker.

## Goal
Production Messenger integration: connect pages, receive webhooks securely, map to the conversation core, send replies within Meta policy, handle data deletion, monitor token health.

## Prerequisites
Phase 09; Meta app (Phase 00 checklist) in development mode at least.

## Requirements covered
PDF §11.4 (webhook, signature, messaging window), §12 Meta assets early, §15 privacy, §27.1 voice attachment receipt (download in P13).

## Scope
**In:** Facebook Login for Business / OAuth page connect, page selection, long-lived page token stored in secrets, webhook subscribe/verify, `X-Hub-Signature-256` validation, event persistence + dedupe, inbound mapping (text, audio attachment, image placeholder, postbacks, read/delivery), outbound Send API (text, quick replies), 24-hour window enforcement + configurable behaviour outside window (allowed message tags only / notify staff), rate limits per page, data deletion callback + status URL, deauthorize callback, token expiry checks.
**Out:** Instagram/WhatsApp (P25), voice transcription (P13).

## Tasks
1. `MessengerChannelAdapter` implementing `ChannelAdapter`; Graph API client (httpx, retries, circuit breaker), API version from settings.
2. Webhook endpoint `/api/v1/webhooks/meta`: GET verify; POST signature check → persist `webhook_events` (unique provider id) → 200 within 1 s → enqueue processing.
3. Mapping: PSID → CustomerIdentity; page → ChannelConnection → tenant; message types → Message(media_type); echo messages from page inbox (human replied in Meta inbox) → mark HUMAN responder to avoid double reply.
4. Outbound: `outbound` queue, respect window (`last_customer_message_at + 24h`), handle errors (token invalid → connection Error + notify; rate limit → backoff).
5. Page connect UI (owner only): connect, list pages, enable AI per page, disconnect; connection health badge.
6. Data deletion callback (`/api/v1/webhooks/meta/data-deletion`): signed request parse → enqueue deletion of customer data for that PSID → confirmation code + status page.
7. Cron: token expiry check → `channels.connection.token_expiring` notification.
8. Sandbox remains available for testing without Meta.

## DB changes
Extend `channel_connections` (provider page id, scopes, token secret ref, expires_at, status), `data_deletion_requests`.

## Settings & templates
Platform: `channels.meta.app_id` (secret: app secret, verify token), `channels.meta.graph_version`, `channels.token_warning_days`. Tenant/page: `channels.ai_enabled`, `channels.outside_window_behaviour`. Templates: `channels.outside_window_notice` (staff-facing).

## Tests
Signature valid/invalid; dedupe of retried webhooks; mapping fixtures (recorded payloads); echo handling prevents double reply; window enforcement; deletion callback flow; contract test adapter vs `ChannelAdapter`.

## Acceptance criteria
- [ ] Owner connects a page; customer message on Messenger appears in inbox in < 2 s
- [ ] Reply sent via Send API; outside-window replies blocked per policy
- [ ] Data deletion callback works end-to-end
- [ ] Invalid signature rejected and logged in error_events

## Rules checklist
- [ ] R-SEC-03 · R-API-06 (dedupe) · R-PERF-01 (ACK < 1 s) · R-CFG-06 (tokens in secrets) · tests · PROGRESS_LOG · no git/Docker
