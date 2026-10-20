# Phase 14 — Order Capture & Customer Confirmation

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 14. Module: `orders`; integrates with `answering`, `customers`, `notifications`. No git/Docker.

## Goal
Capture basic orders from conversations (AI-assisted or staff-created), always confirmed by the customer, priced from DB with `min_price` enforced, managed by the seller.

## Prerequisites
Phase 12.

## Requirements covered
PDF §8 (order needs customer confirm, min_price hard rule), §11.11, §30.11. Doc 20 §6.

## Scope
**In:** order intent detection (deterministic + LLM tool `create_order_draft`), slot filling for required fields (name, phone, address, items, qty, variant, delivery area) via templates, order summary → customer confirmation (quick replies "Confirm/Cancel" or keyword), confirmation timeout, seller order management (statuses, notes), delivery charge calculation, buyer payment option selection (COD, bKash — informational), notifications on new/confirmed orders, order list in conversation view.
**Out:** courier integration (future), online payment collection from buyers (future).

## Tasks
1. Domain: Order (items with unit price from DB at draft time, delivery charge, total recomputed, status machine doc 20 §6), invariants: price ≥ min_price, stock check (configurable hard/soft).
2. Draft creation from engine (tool) or staff UI; missing fields asked via templates; Bangladesh phone validation.
3. Confirmation: summary template → customer reply parsing (deterministic yes/no keywords bn/en) → Confirmed/Cancelled; timeout cron.
4. Seller web: orders list/filter/export, order detail, status changes, create order from conversation.
5. Events + notifications (`orders.order.created/confirmed`) to subscribed users.

## DB changes
`orders`, `order_items`, `order_status_history`, `order_confirmations`.

## Settings & templates
Tenant: `orders.required_fields`, `orders.delivery_charges`, `orders.payment_options`, `orders.confirmation_timeout_minutes`, `orders.stock_policy`, `orders.custom_statuses`. Templates: `orders.ask_field.*`, `orders.summary`, `orders.confirmed`, `orders.cancelled`.

## Tests
LLM-provided price ignored (DB price used); min_price violation impossible; confirmation parsing bn/en; timeout; idempotent creation (Idempotency-Key); tenant isolation.

## Acceptance criteria
- [ ] Customer orders via chat, receives summary, confirms → seller notified
- [ ] Total always equals DB-based calculation

## Rules checklist
- [ ] R-AI-08 · R-DB-04/06 · R-API-06 · tests · PROGRESS_LOG · no git/Docker
