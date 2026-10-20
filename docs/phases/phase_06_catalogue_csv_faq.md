# Phase 06 — Catalogue, CSV Import & FAQ

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 06. Modules: `catalogue`, `faq`, `public`. No git/Docker.

## Goal
Sellers manage products manually or via CSV (template → upload → dry-run → confirm) with rich columns that power non-LLM answers; FAQ management; public catalogue; change events for cache invalidation and indexing.

## Prerequisites
Phase 05 (entitlements: `catalogue.csv`), Phase 01 storage.

## Requirements covered
PDF §11.5, §25 (template, dry-run create/update/skip/error, duplicates sku → name+variant, rich columns features/specs/delivery_info/return_policy, external_id reserved), §21 FAQ step, §3 public catalogue, §28 external_id.

## Scope
**In:** categories, products, variants, images, min_price, stock, rich columns, custom fields, CSV template download (bn/en headers), upload (presigned), dry-run job, confirm job, per-row results, column-mapping templates, product versions, FAQ CRUD (question, answer, keywords, locale), public catalogue pages (SEO), search (FTS + trigram), events.
**Out:** embeddings/RAG indexing (P12/P16), external sync (future).

## Tasks
1. Domain: Product (sku optional, name, variant, price Money, min_price Money, stock, features, specs, delivery_info, return_policy, custom_fields, external_id, status), Category, ProductImage, ImportBatch, ImportRow, Faq.
2. Invariants: `price >= min_price`; duplicate key = sku (tenant) else lower(name)+variant (configurable `catalogue.duplicate_rule`).
3. CSV: template generator; parser with Pydantic row model; mapping templates; dry-run classifies create/update/skip/error with reasons; confirm applies in chunks; limits (`catalogue.csv_max_rows`, `catalogue.csv_max_mb`); CSV formula-injection safe export.
4. Jobs on `import` queue; progress via realtime events; result report downloadable.
5. FAQ CRUD + keywords + locale; ordering/priority.
6. Events: `catalogue.product.created/updated/deleted`, `catalogue.import.completed`, `faq.entry.changed`; tenant version bump `ver:catalogue`, `ver:faq`.
7. Public catalogue: `/api/v1/public/tenants/{slug}/products` + web pages (ISR), only published products, hides min_price/stock if configured.
8. Seller web: product list (TanStack Table, filters), product form (rich fields, images), CSV wizard (template → upload → dry-run review → confirm), FAQ manager.

## DB changes
`categories`, `products`, `product_variants`, `product_images`, `product_versions`, `csv_import_batches`, `csv_import_rows`, `csv_mapping_templates`, `faqs`, `faq_versions`; indexes per doc 05 §3.

## Settings & templates
Tenant: `catalogue.duplicate_rule`, `catalogue.show_stock`, `catalogue.price_display`, `catalogue.discount_allowed_max_percent`, `catalogue.public_enabled`. Platform bounds: `catalogue.csv_max_rows`, `catalogue.csv_max_mb`, `catalogue.max_products` (also plan entitlement).

## Tests
CSV decision table (all classifications, duplicates, malformed, encoding UTF-8/BOM, Bangla text), large file performance, min_price invariant, tenant isolation, public catalogue never leaks hidden fields.

## Acceptance criteria
- [ ] Seller downloads template, uploads 1,000-row CSV, sees dry-run counts, confirms, products appear
- [ ] Re-upload updates by sku, falls back to name+variant
- [ ] Product change bumps catalogue version (cache invalidation ready)
- [ ] FAQ CRUD works; public catalogue visible without login

## Rules checklist
- [ ] R-DB-04/07 · R-SEC-04 (uploads) · R-CFG-01 · R-EVT-01 · tests · PROGRESS_LOG · no git/Docker
