# 05 — Database Architecture

> Apply `docs/GLOBAL_RULES.md` (esp. R-DB-*, R-TEN-*).

## 1. Strategy
- **PostgreSQL 16** single cluster; each module owns its tables (prefix-free, ownership documented in module `infrastructure/models.py`). Optionally one PG schema per module later (`catalogue.products`) to ease extraction.
- **Multi-tenancy:** shared schema + `tenant_id` column + **RLS**. Policy: `USING (tenant_id = current_setting('app.tenant_id')::uuid)`. App DB role is non-superuser and `NOBYPASSRLS`; a separate `platform_admin` role path for admin queries with explicit audit.
- **IDs:** UUIDv7 (time-ordered, index-friendly). **Timestamps:** `timestamptz` UTC. **Money:** `NUMERIC(14,2)` + `currency`.
- **Soft delete** for user-facing entities; hard delete by retention jobs.
- **Optimistic locking** (`version` int) on aggregates edited concurrently (settings, products, rules, conversations state).

## 2. Core tables (by module)

| Module | Tables |
|---|---|
| identity | `users`, `credentials`, `refresh_tokens`, `device_sessions`, `device_push_tokens` (reserved), `email_verifications`, `password_resets` |
| tenancy | `tenants`, `memberships` (user_id, tenant_id, role), `invitations`, `onboarding_states` |
| settings | `setting_definitions` (seeded from code), `setting_values` (scope_type, scope_id, key, value jsonb, version), `setting_values_history`, `message_templates` (key, locale, scope, body, version, is_active), `message_templates_history`, `secrets` (scope, key, ciphertext, key_version) |
| billing | `plans`, `plan_versions`, `plan_entitlements`, `subscriptions`, `subscription_status_history`, `subscription_reviews`, `payments`, `payment_proofs`, `invoices`, `top_ups` |
| catalogue | `categories`, `products` (sku, name, variant, price, min_price, stock, features jsonb, specs jsonb, delivery_info, return_policy, external_id reserved, search tsvector, embedding vector), `product_variants`, `product_images`, `csv_import_batches`, `csv_import_rows`, `product_versions` |
| faq | `faqs` (question, answer, keywords, locale, embedding), `faq_versions` |
| customers | `customers` (tenant_id, display name, locale, opted_out), `customer_identities` (channel, external_id/PSID) |
| channels | `channel_connections` (page_id, status, token secret ref, expires_at), `webhook_events` (provider_event_id unique — dedupe), `outbound_messages` |
| conversations | `conversations` (status, responder, ai_paused, urgency_score, spam_score, consecutive_irrelevant_count, last_activity_at, assigned_user_id, version), `messages` (direction, media_type text/voice/image, body, transcript_id), `voice_transcripts` (audio object key, duration, transcript, confidence, provider, retention_until), `conversation_status_history`, `handoff_events` |
| guard_rules | `conversation_rules` (allowed_keywords, forbidden_keywords, redirect_template, irrelevant_threshold, threshold_action, version), `conversation_rules_history`, `guard_decisions` (message_id, decision, reason) |
| agent_settings | persona stored as settings keys; `agent_profiles` only if multi-persona needed later |
| answering | `answer_cache_entries` (optional PG fallback), `answer_traces` (message_id, path: db/faq/cache/llm, sources, safety result) |
| orders | `orders`, `order_items`, `order_status_history`, `order_confirmations` |
| learning | `learning_candidates`, `knowledge_items`, `knowledge_versions`, `knowledge_chunks` (embedding vector) |
| usage | `usage_ledger` (tenant_id, period, kind: llm_tokens/stt_seconds/conversation/cache_hit/spam_block, quantity, cost, ref_id), `quota_counters`, `budget_caps` |
| analytics | materialized views / read tables: `daily_tenant_metrics`, `platform_daily_metrics` |
| audit | `audit_log` (append-only, partitioned monthly), `error_events`, `job_failures` |
| notifications | `notifications`, `notification_deliveries` |
| platform | `outbox_events` (id, topic, payload, status, attempts), `idempotency_keys`, `feature_flags` |
| ai_platform (own schema `ai`) | `prompts`, `prompt_versions`, `ai_requests`, `provider_configs`, `model_prices`, `eval_runs` |
| future hooks | `sync_connections`, `sync_jobs` (reserved, empty) |

## 3. Indexing & search
- B-tree on `tenant_id` + FKs + hot filters (`conversations(tenant_id, status, last_activity_at desc)`, `messages(conversation_id, created_at)`).
- Unique: `products(tenant_id, sku) WHERE sku IS NOT NULL`, `products(tenant_id, lower(name), variant)`, `webhook_events(provider, provider_event_id)`.
- FTS: `tsvector` (simple config — Bangla has no stemmer) + `pg_trgm` GIN for fuzzy/Banglish.
- Vectors: pgvector **HNSW** with `vector_cosine_ops` on `knowledge_chunks.embedding`, `faqs.embedding`, `products.embedding`; always filtered by `tenant_id` first.

## 4. Partitioning & growth
Monthly range partitions (via `pg_partman`, OSS) for `messages`, `usage_ledger`, `audit_log`, `ai_requests`, `webhook_events`, `outbox_events` once volume warrants. Archive old partitions to object storage.

## 5. Migrations
- Alembic, async env, one linear history; revision message prefixed with module (`catalogue: add product_images`).
- Expand → migrate (backfill job) → contract across releases.
- RLS policies and grants are part of migrations.
- Seed data (plans, setting definitions, default templates, admin roles) via idempotent seed commands, not migrations.

## 6. Scaling path
PgBouncer (transaction pooling) → read replica for analytics/inbox reads → partitioning → per-module database on extraction.

## 7. Backup & recovery
Daily full + continuous WAL archiving (pgBackRest/WAL-G) to object storage; PITR; monthly restore drill; RPO ≤ 15 min, RTO ≤ 2 h (targets).

## 8. History & audit
See doc 22. All `*_status_history`, `*_versions`, `*_history` tables are append-only.
