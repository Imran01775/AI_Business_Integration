# Phase 07 — AI Platform Core

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 07. Package: `ai-platform/src/ai_platform/*`. No git/Docker.

## Goal
Reusable, provider-agnostic, independently scalable AI platform: `AIClient` (in-process + HTTP), LLM/STT/embedding providers, model router with fallback, prompt registry with versions + eval gate, token & cost tracking, AI cache, budgets + kill switches, BYO key, RAG ports.

## Prerequisites
Phases 01–02 (settings, secrets, events), Phase 05 (entitlements for BYO key / model tier).

## Requirements covered
Chat: provider abstraction, prompt management, token tracking, cost tracking, caching, future RAG, independent scaling. PDF §8 BYO key, §21 track tokens, §27.4 STT behind interface. Doc 07, 08.

## Scope
**In:** everything in doc 07 §3–§14; gateway service app; seed prompts; admin UI pages for providers, routing, model prices, prompts (versions/promote/rollback), eval runs, AI requests explorer.
**Out:** business use of AI (P12+), knowledge indexing (P12/P16).

## Tasks
1. `contracts/`: `AIClient` protocol, DTOs, `AICallContext`, errors (`ProviderError`, `BudgetExceededError`, `PromptNotFound`), capability enums.
2. Providers: `llm/openai_compatible.py` (base_url configurable → OpenAI, Groq, Together, OpenRouter, vLLM, Ollama), `llm/anthropic.py`, `llm/gemini.py`, `llm/fake.py`; `stt/faster_whisper.py`, `stt/google.py` (or provider chosen in ADR 0004), `stt/fake.py`; `embeddings/openai_compatible.py`, `embeddings/local_tei.py`, `embeddings/fake.py`. Raw SDK/HTTP use **only here**.
3. `ModelRouter`: resolve `(provider, model)` from `ai.routing.<feature>` + `task_tier` + tenant overrides; fallback chain; circuit breaker per provider.
4. `prompts/`: DB-backed registry (`ai.prompts`, `ai.prompt_versions`), YAML seeds in `ai-platform/prompts/`, sandboxed rendering, variables schema validation, lifecycle draft → candidate → active → retired, rollback.
5. `usage/`: token counting, cost from `ai.model_prices` (effective dated), `UsageRecord` → `ai.ai_requests` + event `ai.usage.recorded`.
6. `cache/`: exact cache with version tags (catalogue/faq/rules/persona/prompt), optional semantic cache; cache-hit records.
7. `BudgetGuard`: global + tenant kill switch, global + tenant daily budget, per-feature caps.
8. BYO key: resolve tenant secret via `SecretsStore`; `billed_to` tracking.
9. `rag/`: `Retriever`, `Indexer`, `VectorStore` ports + pgvector adapter skeleton (used later).
10. `client/`: `InProcessAIClient`, `HttpAIClient` (signed service token); backend composition root chooses by `AI_MODE=inprocess|remote`.
11. `gateway/`: FastAPI app `/v1/chat`, `/v1/stt`, `/v1/embed`, health, metrics.
12. Eval harness: golden-set runner (bn/en/banglish), result store `ai.eval_runs`, promotion gate.
13. Admin web: Providers & keys, Routing editor, Model prices, Prompts (diff, eval score, promote/rollback), Eval runs, AI requests explorer (cost by tenant/model), kill switch toggle.

## DB changes (schema `ai`)
`provider_configs`, `model_prices`, `prompts`, `prompt_versions`, `ai_requests` (partition-ready), `eval_runs`, `eval_cases`.

## Settings
Platform: `ai.providers.enabled`, `ai.routing.*`, `ai.global_budget_daily`, `ai.kill_switch`, `ai.cache.ttl_seconds`, `ai.timeouts.*`, `ai.embeddings.model`. Tenant: `ai.use_byo_key`, `ai.tenant_budget_daily`, `ai.model_tier`, `ai.tenant_kill_switch`.

## Tests
Contract suite every provider must pass (fake + recorded fixtures); router fallback/circuit tests; budget/kill switch; cost calculation precision (Decimal); prompt rendering errors; cache invalidation by version tag; in-process vs HTTP client parity test.

## Acceptance criteria
- [ ] Switch default LLM provider via admin setting with no code change
- [ ] Every call recorded with tokens + cost; ledger event emitted
- [ ] Kill switch and budget block calls and return typed errors
- [ ] Prompt version promote/rollback works with eval gate
- [ ] Same test suite passes with `AI_MODE=inprocess` and `remote`

## Rules checklist
- [ ] R-AI-01/05/06/07/10 · R-CFG-01/06 · R-TEST-02/05 · ADR for providers · PROGRESS_LOG · no git/Docker
