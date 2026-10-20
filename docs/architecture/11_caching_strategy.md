# 11 — Caching Strategy

> Apply `docs/GLOBAL_RULES.md` (esp. R-TEN-03, R-PERF-03).

## 1. Principles
Cache read-heavy, tenant-scoped data; **explicit invalidation via events**; versioned keys (bump version instead of deleting many keys); never cache secrets or cross-tenant data; cache failures degrade to source (cache is never the source of truth).

## 2. Layers
| Layer | Tech | Examples |
|---|---|---|
| HTTP/CDN | Caddy / CDN, Next.js ISR | public pages, pricing, public catalogue, static assets |
| Client | TanStack Query | per-tenant query cache, SSE-driven updates |
| Application | Redis | settings resolution, entitlements, plan data, product lookups, FAQ index, rules compiled matchers |
| AI | Redis | answer cache (exact + semantic), embedding cache (doc 07 §9) |
| DB | PostgreSQL buffer cache, materialized views | analytics |

## 3. Key conventions
`t:{tenant_id}:{module}:{entity}:{id}:v{version}` — tenant version counters: `t:{tenant}:ver:catalogue`, `t:{tenant}:ver:faq`, `t:{tenant}:ver:rules`, `t:{tenant}:ver:settings`. Changing catalogue increments `ver:catalogue`, implicitly invalidating all dependent keys (including AI answer cache — PDF: "invalidate cache on product change").

## 4. Catalogue of cached items
| Item | TTL | Invalidated by |
|---|---|---|
| Resolved settings per scope | 5 min | `settings.changed` |
| Entitlements per tenant | 5 min | `billing.subscription.status_changed`, plan change |
| Compiled seller-rule matcher | 10 min | `settings.changed` (rules) |
| Product by id / sku | 10 min | `catalogue.product.*` |
| FAQ match index | 10 min | `faq.entry.changed` |
| Deterministic answer (DB/FAQ hit) | `answering.cache_ttl_seconds` | catalogue/faq/rules/persona version bump |
| LLM answer cache | `ai.cache.ttl_seconds` | same + prompt version |
| Public plans/feature matrix | 1 h (ISR) | plan publish |
| Rate-limit counters | sliding window | n/a |

## 5. Patterns
Cache-aside with single-flight (Redis lock) to prevent stampede; stale-while-revalidate for public data; write-through not used.

## 6. Metrics
Hit ratio per cache family (Prometheus), AI cache-hit rate per tenant (PDF metric) exposed in seller widget and admin dashboard.
