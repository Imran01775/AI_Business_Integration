# Phase 03 — Auth, Workspace & RBAC

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 03. Modules: `identity`, `tenancy`, `settings` (user chain), `audit`. No git/Docker.

## Goal
Users can register, verify email, log in (web cookie + mobile bearer), create a business (tenant), invite team members with roles; platform admin roles exist; user-level settings work.

## Prerequisites
Phases 01–02.

## Requirements covered
PDF §11.2 auth, workspace, multi-tenant isolation; §6 role separation. Docs 06, 23, 24 §5/§8.

## Scope
**In:** register/login/logout/refresh, email verification, password reset, device sessions, tenant creation, memberships (owner/manager/agent), invitations, platform roles (super_admin, reviewer, payment_verifier, support, content_manager), permission + tenant dependencies, user settings API, onboarding state record.
**Out:** MFA (P19), social login (future), UI (P04).

## Tasks
1. `identity` domain: User, Credential, RefreshToken (family, rotation, reuse detection), DeviceSession; Argon2id hasher port.
2. Use cases: Register, VerifyEmail, Login (returns tokens + session), Refresh, Logout (session/all), RequestPasswordReset, ResetPassword, ListSessions, RevokeSession.
3. JWT service (EdDSA or RS256 keys from env), claims per doc 06.
4. Auth dependency: reads `Authorization: Bearer` **or** cookie (`access_token`), builds `Principal`; CSRF check for cookie-auth writes.
5. `tenancy`: Tenant (name, slug, timezone, locale, currency), Membership, Invitation (email, role, token, expiry), OnboardingState; use cases CreateTenant (creator = owner), InviteMember, AcceptInvitation, ChangeRole, RemoveMember.
6. Tenant dependency: `X-Tenant-Id` → membership check → `SET LOCAL app.tenant_id`.
7. Permission registry (`permissions.py` per module) + role→permission mapping (default in code, override via platform settings).
8. Platform roles + `require_platform_role` dependency; seed first super admin via CLI.
9. User settings: `/api/v1/me/settings` (GET schema + values, PATCH) using user chain.
10. Rate limits on auth endpoints; templates: `identity.verify_email`, `identity.reset_password`, `tenancy.invitation` (bn/en).
11. Events: `identity.user.registered`, `tenancy.tenant.created`, `tenancy.member.added`.
12. SSE endpoint now authenticated.

## DB changes
`users`, `credentials`, `refresh_tokens`, `device_sessions`, `device_push_tokens` (reserved), `email_verifications`, `password_resets`, `tenants` (extend), `memberships`, `invitations`, `onboarding_states`, `platform_role_assignments`.

## Settings & templates
User chain: `user.locale`, `user.theme`, `user.timezone_display`, `user.notifications.*`, `user.availability_status`. Platform: `auth.access_token_minutes`, `auth.refresh_token_days`, `auth.max_sessions`.

## Tests
Unit: token rotation/reuse detection, role permissions matrix (doc 06 §4). Integration: tenant isolation for memberships; cookie + bearer both work on the same endpoint; CSRF enforced for cookie writes.

## Acceptance criteria
- [ ] Register → verify → login → create business → invite agent → agent logs in with limited permissions
- [ ] Same endpoints work with cookie and Bearer
- [ ] Session list/revoke per device
- [ ] All actions audited

## Rules checklist
- [ ] R-SEC-01/02/06/07 · R-API-07 · R-TEN-02 · R-CFG-03 (user chain) · tests · OpenAPI updated · PROGRESS_LOG · no git/Docker
