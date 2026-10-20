# 20 — Domain Model & State Machines

> Apply `docs/GLOBAL_RULES.md`. Every transition writes a `*_status_history` row and emits an event (R-DB-06). All timers/thresholds come from settings (R-CFG-01).

## 1. Core aggregates
```mermaid
classDiagram
  Tenant "1" --> "*" Membership
  User "1" --> "*" Membership
  Tenant "1" --> "1" Subscription
  Subscription "*" --> "1" PlanVersion
  Tenant "1" --> "*" ChannelConnection
  Tenant "1" --> "*" Product
  Tenant "1" --> "*" Faq
  Tenant "1" --> "1" ConversationRules
  Tenant "1" --> "*" Customer
  Customer "1" --> "*" Conversation
  Conversation "1" --> "*" Message
  Message "1" --> "0..1" VoiceTranscript
  Conversation "1" --> "*" Order
  Tenant "1" --> "*" KnowledgeItem
  Tenant "1" --> "*" UsageLedgerEntry
```

## 2. Subscription (PDF §3–6)
```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> PendingPayment: submit_request
  PendingPayment --> PendingReview: payment_proof_submitted_or_gateway_paid
  PendingReview --> NeedsInfo: reviewer_requests_info
  NeedsInfo --> PendingReview: seller_responds
  PendingReview --> Active: review_approved_and_payment_verified
  PendingReview --> Rejected: reviewer_rejects
  Active --> PastDue: period_end_unpaid
  PastDue --> Active: payment_verified
  PastDue --> Suspended: grace_days_exceeded
  Suspended --> Active: payment_verified_and_admin_reinstates
  Suspended --> Expired: suspend_days_exceeded
  Rejected --> Draft: resubmit
  Expired --> Draft: renew
```
Live AI features require `Active`. Public discovery never requires a subscription.

## 3. Conversation lifecycle (PDF §22)
```mermaid
stateDiagram-v2
  [*] --> ACTIVE
  ACTIVE --> HUMAN_HANDOFF: handoff_trigger_or_threshold_action
  HUMAN_HANDOFF --> ACTIVE: staff_resumes_ai
  ACTIVE --> IDLE: no_activity_idle_after
  IDLE --> ACTIVE: customer_message
  IDLE --> CLOSED: no_activity_close_after
  HUMAN_HANDOFF --> CLOSED: staff_closes
  CLOSED --> ACTIVE: customer_message_reopen
  ACTIVE --> BLOCKED: guard_or_rule_threshold_blocked
  HUMAN_HANDOFF --> BLOCKED: staff_blocks
  BLOCKED --> ACTIVE: staff_unblocks
```
Conversation attributes: `responder` (AI | HUMAN | WAITING), `ai_paused`, `urgency_score`, `spam_score`, `consecutive_irrelevant_count`, `assigned_user_id`, `last_activity_at`, `version`.

## 4. Responder / handoff (no AI + human double reply)
```mermaid
stateDiagram-v2
  [*] --> AI
  AI --> WAITING: handoff_requested
  WAITING --> HUMAN: staff_takes_over
  AI --> HUMAN: staff_takes_over
  HUMAN --> AI: staff_resumes_ai
  WAITING --> AI: timeout_policy_or_staff_returns
```
Invariant: an outbound auto-reply is sent only if `responder == AI` **at send time** (checked with row version / lock); a human reply while `responder == AI` forces `HUMAN` first.

## 5. Inbound message decision (PDF §26, §27.2)
| Condition | Outcome | LLM? |
|---|---|---|
| Conversation BLOCKED/CLOSED-by-policy | store only | no |
| Guard: rate limit / spam_score ≥ threshold | store, count spam_block (not quota), maybe BLOCKED | no |
| Voice STT failed / empty / low confidence | soft "please type" template or human alert | no |
| Forbidden keyword | apply threshold logic, log reason | no |
| Not in allowed topics, count < threshold | one soft redirect (template), increment counter | no |
| Count ≥ threshold | seller action: Pause AI / Handoff / BLOCKED | no |
| Relevant + deterministic hit (DB/FAQ/Cache) | reply | no |
| Relevant + miss + quota/budget OK | LLM short context → safety → reply | yes |
| Relevant + miss + quota exhausted | soft handoff template (never fake) | no |
Message is **always stored**; only the auto-reply changes. Relevant message resets `consecutive_irrelevant_count`.

## 6. Order (PDF §8, §11)
```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> AwaitingConfirmation: summary_sent_to_customer
  AwaitingConfirmation --> Confirmed: customer_confirms
  AwaitingConfirmation --> Cancelled: customer_declines_or_timeout
  Confirmed --> Processing: seller_accepts
  Processing --> Shipped
  Shipped --> Delivered
  Confirmed --> Cancelled: seller_cancels
  Processing --> Cancelled: seller_cancels
```
Price per item ≥ `min_price` enforced in domain; order total recomputed from DB, never from LLM text.

## 7. Learning item (PDF §10)
`Candidate (from staff reply) → Redacted → PendingApproval → Approved/Published (versioned) → RolledBack`; Rejected terminal. Only Published versions are retrievable; tenant-scoped only.

## 8. CSV import batch (PDF §25)
`Uploaded → Validating → DryRunReady (create/update/skip/error counts) → Confirmed → Applying → Completed | Failed | Cancelled`. Duplicate key: `sku` within tenant, else `lower(name) + variant`.

## 9. Channel connection
`Pending → Connected → TokenExpiring → Expired | Disconnected | Error`.
