# 06 — Authentication & Authorization

> Apply `docs/GLOBAL_RULES.md` (esp. R-SEC-*, R-API-07, R-TEN-*).

## 1. Identity model
- **User** = a person (email, password, name, locale). A user can belong to many **tenants** (businesses) through **memberships** with a role.
- **Platform admins** are users with a platform role (separate from tenant roles).
- `IdentityProvider` port: in-house implementation now; Keycloak/OIDC/social login adapters later without changing modules.

## 2. Authentication
| Item | Design |
|---|---|
| Password hashing | Argon2id (tuned params), breached-password check optional |
| Access token | JWT (EdDSA/RS256), 10–15 min, claims: `sub`, `sid` (session), `roles`, `ten` (active tenant optional), `ver` |
| Refresh token | Opaque random, stored hashed in `refresh_tokens`, rotated on every use, **reuse detection** → revoke session family |
| Web client | Tokens in httpOnly Secure SameSite=Lax cookies via Next.js route handlers; CSRF protection with double-submit token for state-changing requests |
| Mobile client | `Authorization: Bearer`; refresh token in secure storage (Keychain/Keystore) |
| Sessions | `device_sessions` (device name, client type web/mobile, IP, UA, last_seen) — user can list/revoke |
| Email verification & reset | Single-use hashed tokens with expiry; templates from template store |
| MFA (later) | TOTP for owners and platform admins (planned, Phase 19 hardening) |
| Rate limiting | Login/reset/register per IP + per account; lockout with backoff |

## 3. Tenant context
Active tenant comes from `X-Tenant-Id` header (validated against memberships) or token claim. The tenant dependency sets `SET LOCAL app.tenant_id` for RLS for the transaction.

## 4. Authorization model
**RBAC + permission strings + policies + entitlements**

- Permissions: `<module>:<action>` e.g. `catalogue:write`, `settings.business:write`, `billing:manage`, `conversations:takeover`.
- Tenant roles (default, configurable mapping in settings):

| Permission area | Owner | Manager | Agent |
|---|---|---|---|
| Billing, plan, top-up | ✔ | ✘ | ✘ |
| Team & roles | ✔ | invite agents only | ✘ |
| Channels connect/disconnect, secrets/BYO key | ✔ | ✘ | ✘ |
| Business settings (persona, rules, FAQ, templates, catalogue, orders, urgency) | ✔ | ✔ | read |
| Conversations (reply, take-over, assign) | ✔ | ✔ | ✔ |
| Learning approval | ✔ | ✔ | ✘ |
| Data export / deletion | ✔ | ✘ | ✘ |
| Personal user settings | ✔ | ✔ | ✔ |

- Platform roles: `super_admin`, `reviewer` (subscription review), `payment_verifier`, `support` (read + impersonate with consent/time-box), `content_manager` (public site, templates).
- **Policies** (attribute checks) in application layer: e.g. agent can only reply to conversations assigned to them if tenant setting `conversations.assignment_strict = true`.
- **Entitlements** (from plan): checked by `EntitlementChecker` before feature use, e.g. `voice.enabled`, `guard.advanced`, `byo_key.allowed`.
- **Subscription gate:** live AI features require subscription status `Active` (public discovery stays open).

## 5. Enforcement points
1. Route dependency: `require(permission="catalogue:write", entitlement=None)`.
2. Use case: policy checks needing domain data.
3. Database: RLS (defense in depth).
4. UI: hides controls by permission (cosmetic only — never trusted).

## 6. Impersonation
Support/super_admin can start a time-boxed (e.g. 30 min) read-only or full impersonation session; banner shown in UI; every action audited with `impersonator_id`.

## 7. Webhook & service auth
- Meta webhooks: verify token (subscribe) + `X-Hub-Signature-256` HMAC.
- Payment gateway callbacks: signature/IPN validation.
- Internal AI gateway (when remote): mTLS or signed service JWT + network policy.

## 8. Audit
Login, logout, failed login, token reuse, role change, impersonation, permission denial (sampled) → `audit_log`.
