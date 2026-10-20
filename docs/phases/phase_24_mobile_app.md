# Phase 24 — Mobile App (FUTURE)

> **Status: FUTURE.** Start only after production is stable. **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 24. Area: `frontend/apps/mobile`, `frontend/packages/*`, `notifications` (push adapter).

## Goal
Deliver the seller experience on phones: first as an installable PWA, then as an Expo/React Native app reusing the same API and shared packages — no backend refactor.

## Prerequisites
Phase 23. Architecture doc 23 rules respected in all previous phases.

## Scope
**24a — PWA:** manifest, service worker (offline shell, cached static assets), install prompt, web push (optional, VAPID), responsive audit of seller panel.
**24b — Native (Expo):** Expo Router app in `apps/mobile`; auth with Bearer + refresh in SecureStore; screens: inbox, conversation (text/voice playback, transcript), take-over/resume, orders, notifications, quick settings (schema-driven); push notifications via Expo Push/FCM (`device_push_tokens`, `PushNotificationChannel` adapter); `X-App-Version` + `/app/config` force-update; Play Store release first.

## Tasks
1. Verify shared packages have no DOM/Next.js imports; add RN-compatible build targets.
2. Implement push channel adapter + user push preferences.
3. Build screens reusing `api-client`, `shared`, `i18n`, `design-tokens`.
4. E2E (Detox/Maestro OSS) for login → inbox → take-over.

## Acceptance criteria
- [ ] Mobile app performs core seller flows using only existing APIs
- [ ] Push notifications for handoff/new order
- [ ] Old app versions can be forced to update

## Rules checklist
- [ ] R-FE-01/08 · R-API-01/07 · PROGRESS_LOG
