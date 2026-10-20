# Phase 04 — Frontend Foundation

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 04. Area: `frontend/apps/web`, `frontend/packages/*`. No git/Docker.

## Goal
A working web app shell: design system, generated API client, i18n (bn/en), auth UI wired to Phase 03, route groups with guards, schema-driven form renderer, error handling, SSE client, legal pages (Privacy/Terms — required for Meta review).

## Prerequisites
Phase 03.

## Requirements covered
PDF §3–6 public site base, §15 Privacy/Terms. Docs 03, 23.

## Scope
**In:** Next.js app, Tailwind + shadcn/ui, design tokens, `packages/api-client` generation script, `packages/i18n`, `packages/shared`, auth pages (login, register, verify, forgot/reset), app shells for (public)/(seller)/(admin), tenant switcher, user settings page (schema-driven), legal pages (content from templates/CMS-lite API), error boundaries, GlitchTip client, SSE hook, PWA manifest stub.
**Out:** pricing page (P05), public catalogue (P06), feature pages.

## Tasks
1. Next.js 15 App Router, TypeScript strict, ESLint boundaries plugin (feature isolation).
2. `packages/design-tokens` → Tailwind preset; shadcn/ui components in `shared/ui`; dark/light theme.
3. `packages/api-client`: script `pnpm gen:api` (openapi-typescript from backend OpenAPI) + typed `openapi-fetch` client with auth/tenant/trace headers and error mapping.
4. `packages/i18n`: bn.json, en.json, error-code translations; next-intl setup with locale detection + user setting.
5. Auth BFF route handlers (`app/api/auth/*`) converting tokens ↔ httpOnly cookies; middleware guarding route groups; silent refresh.
6. Layouts: public header/footer, seller sidebar (feature links hidden by permission), admin layout.
7. `shared/ui/schema-form`: renders settings definitions (JSON Schema + UI hints), handles permission/entitlement disabled states.
8. User settings page (`/settings/me`) using schema-form + `/api/v1/me/settings`.
9. Legal pages: Privacy, Terms, Data deletion instructions (content served by backend `public` module from templates, versioned).
10. Error boundaries per route group, toast system mapping `error.code`, GlitchTip browser SDK.
11. `shared/lib/sse.ts` + `useRealtime` hook updating TanStack Query cache.
12. Accessibility baseline (axe in tests).

## Tests
Vitest: api-client error mapping, schema-form rendering, auth hooks. Playwright: register → verify (Mailpit) → login → create business → switch language.

## Acceptance criteria
- [x] Auth flow works end-to-end in browser (cookies only, no tokens in JS)
- [x] Language switch bn/en across shell
- [x] User settings page generated from schema
- [x] Privacy/Terms/Data-deletion pages publicly reachable

## Rules checklist
- [x] R-FE-01..08 · R-API-01 (generated client) · a11y · i18n · PROGRESS_LOG · no git/Docker
