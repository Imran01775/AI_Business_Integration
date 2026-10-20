# Phase 12 — Token-Efficient Answering Engine & Safety

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 12. Modules: `answering`, `agent_settings`; uses `AIClient`, `usage`, `catalogue`, `faq`. No git/Docker.

## Goal
Answer relevant messages with the cheapest correct path: DB → FAQ → Cache → LLM (short memory + tools) only if needed and quota allows; persona/style; Safety Validator grounds facts; `min_price` hard rule; cache invalidation on product change.

## Prerequisites
Phases 07, 08, 11.

## Requirements covered
PDF §8 (ground facts in DB, min_price hard rule), §11.8, §21 (DB → Rules → FAQ → Cache, hit → no LLM, miss + quota OK → short memory + tools → LLM, never full history, invalidate cache on product change, tenant filter), §2 "reply in style". Docs 07, 08, 11.

## Scope
**In:** intent detection (deterministic first: keyword/pattern for price, stock, delivery, return, order intent, greeting, human request), DB answerers (product lookup by name/sku/fuzzy), FAQ matcher (keyword + trigram + optional embedding), deterministic answer cache, LLM path with tool calls (`search_products`, `get_product`, `get_policy`), short memory window, persona injection, Safety Validator, handoff triggers, answer traces, product/FAQ embedding indexing (RAG base), agent settings UI.
**Out:** learned knowledge (P16), orders (P14).

## Tasks
1. `agent_settings`: persona keys (bot_name, tone, reply_language auto/bn/en/banglish, greeting, sign_off, emoji_level, max_reply_chars), mode (auto/suggest/off), off-hours behaviour, handoff keywords/order value, deterministic-only.
2. Engine stage chain (`AnswerStrategy` interface, ordered by settings): `GreetingStrategy`, `HumanRequestStrategy`, `ProductFactStrategy` (DB), `FaqStrategy`, `CacheStrategy`, `LlmStrategy`. First confident result wins.
3. Templated deterministic replies (bn/en) for price/stock/delivery/return using rich columns.
4. LLM path: `UsageFacade.check` → `AIClient.complete(prompt_key="answering.reply", vars=persona + facts, messages=last N (setting))`, tools executed by engine (tenant-filtered), result → Safety Validator.
5. Safety Validator: extract prices/discounts/stock claims → compare with DB; reject if mismatch, price < min_price, discount > allowed, unknown product claims; on fail → regenerate once or handoff (setting).
6. Suggest-only mode: draft reply shown to staff instead of sending.
7. Cache: answer cache keyed by normalised question + versions; invalidated by version bump.
8. Indexing jobs: embed products/FAQ on change events (for semantic FAQ match + LLM retrieval).
9. `answer_traces`: path (db/faq/cache/llm), sources, tokens, cost, safety result → visible in conversation view.
10. Web: Agent settings page (persona preview using sandbox), answer trace viewer.

## Settings & templates
Tenant: `agent.*`, `answering.memory_messages` (bounded), `answering.strategy_order`, `answering.cache_ttl_seconds`, `answering.safety_fail_action`. Platform: `answering.memory_messages_max`. Templates: price/stock/delivery/return/greeting/human-request/handoff/not-found replies (bn/en). Prompts: `answering.reply`, `answering.intent_fallback`.

## Tests
Strategy order; deterministic hit never calls AIClient; LLM receives ≤ N messages; Safety Validator matrix; min_price enforcement; cache invalidation on product update; quota exhausted → soft handoff; eval harness golden set (bn/en/banglish) ≥ target accuracy.

## Acceptance criteria
- [ ] Common questions answered without LLM (measured deterministic ratio in traces)
- [ ] LLM answers grounded; wrong price never sent
- [ ] Product price change → next answer reflects new price (cache invalidated)
- [ ] Persona changes reflected without code change

## Rules checklist
- [ ] R-AI-02/04/05/06/08/11 · R-CFG-01/05 · R-TEN-04 · tests + eval · PROGRESS_LOG · no git/Docker
