# 23 — Multi-Client & Mobile-App Readiness

> Apply `docs/GLOBAL_RULES.md` (esp. R-API-01, R-API-07, R-FE-01, R-FE-08).

## 1. Goal
Allow converting/adding a native mobile app (Android/iOS) later **without backend refactoring**. The Next.js web app is just one client.

## 2. Built-in from day 1
| Area | Design |
|---|---|
| API-first | All business logic in backend; Next.js only renders/proxies; OpenAPI single contract |
| Auth | Web: httpOnly cookies via Next.js route handlers. Mobile: Bearer access + rotating refresh (secure storage). Same backend endpoints (`/auth/login`, `/auth/refresh`) return tokens; BFF converts to cookies for web |
| Sessions | `device_sessions` with client type, device name; list/revoke per device |
| Push | `NotificationChannel` port; push adapter (FCM / Expo Push, free) added in Phase 24; `device_push_tokens` reserved |
| Realtime | SSE endpoint with documented event schema; WebSocket adapter optional; mobile can also rely on push + refetch |
| Sync-friendly APIs | cursor pagination, `updated_since` delta sync, compact payloads, ETag/If-None-Match |
| Uploads | presigned upload URLs (MinIO/S3) for images, audio, CSV, payment proofs |
| Errors / i18n | backend returns stable `error.code`; clients translate from `packages/i18n` |
| Settings UI | schema-driven (`/settings/schema`) — mobile renders the same definitions |
| Versioning | `X-App-Version` header; `/api/v1/app/config` returns `min_supported_version`, `latest_version`, feature flags, maintenance banner → force-update capability |
| Deprecation | ≥ 90-day deprecation window for breaking API changes |

## 3. Shared frontend packages (platform-neutral, no DOM / Next.js imports)
- `packages/api-client` — generated types + fetch client (works in RN)
- `packages/shared` — Zod schemas, enums, error-code map, formatters
- `packages/i18n` — bn/en catalogues
- `packages/design-tokens` — tokens consumed by Tailwind (web) and RN styles (mobile)

## 4. Migration path
1. **PWA** (Phase 24a): manifest, service worker, installable seller panel, web push (optional). Cheapest step.
2. **Expo / React Native** app (Phase 24b) in `frontend/apps/mobile`: seller inbox, take-over, notifications, orders, quick settings; reuse packages; Expo Router; secure storage for tokens; push via Expo.
3. Store release (Play Store first for Bangladesh market).

## 5. Rules for every feature (so mobile stays possible)
- Feature fully usable through API alone.
- No business logic in Next.js server actions or components.
- Endpoints work with cookie and Bearer auth.
- No web-only assumptions in payloads (HTML strings, CSS) — return data, not markup.
