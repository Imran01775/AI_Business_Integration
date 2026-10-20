# Phase 11 — Conversation Guard & Seller Conversation Rules

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 11. Module: `guard_rules`. No git/Docker.

## Goal
Cheap, deterministic gate before any answering: Conversation Guard (status, rate limit, spam score, consecutive irrelevant count) and Seller-Defined Conversation Rules (allowed/forbidden keywords, redirect message, threshold, threshold action). **No generative LLM** in this gate.

## Prerequisites
Phase 09 (pipeline slots, state machines), Phase 06 (product/FAQ lookup for relevance).

## Requirements covered
PDF §11.6, §11.13, §22 (guard, configurable thresholds, "many messages alone ≠ spam"), §26 runtime, §27.2 decision table, §7 Abuse Guard basic vs advanced.

## Scope
**In:** Bangla/Banglish text normaliser, keyword matcher (compiled per tenant, cached), guard stage, rules stage, threshold actions (Pause AI / Handoff / BLOCKED), soft redirect once, counters, decisions log, rules editor UI + rule tester, advanced guard (entitlement) e.g. weighted spam signals.
**Out:** answering (P12).

## Tasks
1. `TextNormaliser`: Unicode NFC, lowercase, Bangla digit ↔ ASCII, punctuation/emoji strip, repeated-char squeeze, Banglish transliteration map (configurable dictionary), synonyms list per tenant.
2. Matcher: Aho-Corasick / regex word-boundary matcher compiled from allowed + forbidden keywords + product names/SKUs + FAQ keywords; cached by `ver:rules|catalogue|faq`.
3. Guard stage: status check (BLOCKED/CLOSED-policy → store only), rate limit (`guard.rate_limit_per_minute`), spam score (weights: duplicates, links, gibberish ratio, burst — not volume alone), outcome → `guard.message.rejected` (spam_block, not quota).
4. Rules stage (PDF §26): normalise → forbidden check → allowed/product/FAQ check → else: if counter < threshold → one soft redirect (template) + increment; if ≥ threshold → `rules.threshold_action` (pause_ai | handoff | blocked). Relevant → reset counter. Message always stored.
5. Every decision → `guard_decisions` (reason code) for seller visibility + analytics.
6. Seller web: Rules editor (allowed/forbidden chips, redirect template bn/en, threshold slider, action select), **rule tester** (type a sample → see decision), block list management.
7. Admin: platform bounds for guard values.

## DB changes
`conversation_rules`, `conversation_rules_history`, `guard_block_list`, `normaliser_dictionaries` (platform + tenant).

## Settings & templates
Tenant: `rules.allowed_keywords`, `rules.forbidden_keywords`, `rules.irrelevant_threshold`, `rules.threshold_action`, `guard.rate_limit_per_minute`, `guard.spam_score_threshold`, `guard.advanced.*` (entitlement `guard.advanced`). Templates: `rules.redirect_message`.

## Tests
Decision table from PDF §27.2 (all rows), normaliser cases (বাংলা, Banglish variants, digits), spam vs high-volume legit customer, threshold actions trigger state machine correctly, performance (< 5 ms per message), no LLM invoked (assert fake AIClient untouched).

## Acceptance criteria
- [ ] Out-of-rule messages never reach engine/LLM
- [ ] One soft redirect then threshold action as configured
- [ ] Rule tester shows identical decision to runtime

## Rules checklist
- [ ] R-AI-02/03 · R-CFG-01/05 · R-TEST-01 (≥ 90% critical) · PROGRESS_LOG · no git/Docker
