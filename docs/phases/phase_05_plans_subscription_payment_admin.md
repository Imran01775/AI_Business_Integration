# Phase 05 — Plans, Subscription, Payment, Entitlements & Admin Console

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 05. Modules: `billing`, `admin`, `public`, `settings`, `audit`, `notifications` (basic). No git/Docker.

## Goal
Implement the key product rule: public discovery open; activation requires admin approval + verified payment. Plans and entitlements drive every feature gate. Admin console for review, payments, plans, platform settings, audit and errors.

## Prerequisites
Phases 03–04.

## Requirements covered
PDF §3–7 (public site, subscription, statuses, admin, plans & feature matrix), §13 payments (verified gateway or manual transfer), §24 top-up/overage (purchase side). Docs 20 §2, 24 §6.

## Scope
**In:** plans + versions + entitlements, public pricing + feature matrix page, subscription request flow, full status machine (Draft → … → Expired), manual payment with proof upload, payment gateway port (fake adapter now), invoices, top-up packs purchase flow, entitlement checker, admin console (review queue, payment verification, plans editor, platform settings UI, audit log viewer, error events viewer, jobs/DLQ viewer, impersonation), basic notifications (in-app + email).
**Out:** quota consumption (P08), real gateway adapters (later, via port).

## Tasks
1. `billing` domain: Plan, PlanVersion (immutable once published), Entitlement (key → value/limit), Subscription aggregate with state machine (doc 20 §2), Payment (method manual/gateway, amount, trx_id, proof object key, status), Invoice, TopUp.
2. Use cases: PublishPlan, RequestSubscription, SubmitPaymentProof, GatewayCallback (port), RequestInfo, RespondInfo, ApproveReview, VerifyPayment, RejectSubscription, Activate (saga: review ✔ + payment ✔), MarkPastDue/Suspend/Expire (cron), PurchaseTopUp, GenerateInvoice.
3. `EntitlementChecker` facade: `has(tenant, key)`, `limit(tenant, key)` cached; feature gate dependency for routes.
4. `public` module: `/api/v1/public/plans`, `/public/feature-matrix` (from plan entitlements + content labels).
5. Web: pricing page with feature matrix (ISR), subscription request wizard, payment proof upload (presigned), subscription status page with history.
6. Admin console (web `(admin)`): review queue with documents/proofs, approve/reject/needs-info, payment verification (finance role), plans editor (draft → publish new version), **platform settings UI** (schema-form for platform scope), templates editor (bn/en), audit log viewer, error events viewer + resolve, jobs/DLQ viewer + retry, tenant list + impersonation (time-boxed, banner, audited).
7. Notifications (basic): `NotificationService` with in-app + email channels; events → notifications (status changes, needs-info).
8. Seed default plans: Starter, Business, Pro, Enterprise with entitlements from PDF §7 (voice, CSV, rules, token engine, abuse guard basic/advanced, channels later).

## DB changes
`plans`, `plan_versions`, `plan_entitlements`, `subscriptions`, `subscription_status_history`, `subscription_reviews`, `payments`, `payment_proofs`, `invoices`, `top_ups`, `notifications`, `notification_deliveries`, `impersonation_sessions`.

## Settings & templates
Platform: `billing.grace_days`, `billing.suspend_after_days`, `billing.expire_after_days`, `billing.manual_methods`, `billing.vat_percent`, `billing.invoice_template`. Templates: subscription status emails, needs-info, payment received/verified/rejected (bn/en).

## Tests
State machine property tests (no illegal transition); activation saga requires both approvals; entitlement gating; role separation (reviewer cannot verify payment unless permitted); impersonation audit; tenant isolation.

## Acceptance criteria
- [ ] Visitor sees pricing + matrix without login
- [ ] Seller requests plan → uploads proof → reviewer approves → finance verifies → Active
- [ ] Past Due/Suspended/Expired transitions run via cron with configured days
- [ ] Admin edits a platform setting and a template without code change
- [ ] All transitions in history + audit

## Rules checklist
- [ ] R-CFG-01 (plan values from DB) · R-DB-04/06 · R-SEC-06 · R-API-06 (idempotent payments) · tests · PROGRESS_LOG · no git/Docker
