# Phase 16 — Learning Queue, Versioned Knowledge & RAG

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 16. Module: `learning`; uses `ai_platform.rag`, `answering`. No git/Docker.

## Goal
Learn only from reviewed staff replies: staff reply → candidate → redact → approve → versioned knowledge → used by RAG; rollback anytime; no cross-tenant learning.

## Prerequisites
Phase 15 (staff replies, take-over), Phase 12 (engine + indexing).

## Requirements covered
PDF §10 (staff reply → redact → approve → versioned knowledge, no cross-tenant learning), §11.10 learning approval queue + rollback. Doc 08.

## Scope
**In:** candidate creation from human replies (configurable: all / flagged / suggest-mode edits), Q/A pair extraction (customer question + staff answer), PII redaction (deterministic regex + optional LLM redaction via `AIClient` with prompt `learning.redact`), approval queue UI (edit, approve, reject), knowledge versions, publish → index chunks, rollback → deactivate, knowledge used in engine (new `KnowledgeStrategy` before LLM or as RAG context), hybrid retrieval, retrieval eval set.
**Out:** advanced coach (future).

## Tasks
1. Domain: LearningCandidate (state machine doc 20 §7), KnowledgeItem, KnowledgeVersion.
2. Candidate capture on `conversations.message.stored` (direction=out, sender=human) per `learning.auto_suggest`.
3. Redaction pipeline: phone/email/address/name patterns (bn/en) → optional LLM redaction → diff shown to approver.
4. Approval UI with side-by-side original/redacted, edit, approve/reject, approver role check (`learning.approvers`).
5. Publish: new version → chunk + embed (indexing queue) → `learning.knowledge.published` → answering cache bump.
6. Rollback: activate previous version / deactivate item → `learning.knowledge.rolled_back`.
7. Engine: hybrid retriever (pgvector + trigram, RRF) tenant-filtered; `KnowledgeStrategy` (high-similarity direct answer) and RAG context for `LlmStrategy` within `rag.max_context_tokens`.
8. Eval: retrieval golden sets per tenant sample; groundedness check.

## DB changes
`learning_candidates`, `knowledge_items`, `knowledge_versions`, `knowledge_chunks` (vector + HNSW index).

## Settings & templates
Tenant: `learning.auto_suggest`, `learning.approvers`, `learning.redaction_rules`, `rag.top_k`, `rag.min_score`, `rag.max_context_tokens`. Prompts: `learning.redact`, `answering.reply` (RAG variant).

## Tests
Redaction cases; no unapproved knowledge ever retrieved; rollback immediate; cross-tenant retrieval impossible (isolation test); retrieval recall@k on golden set.

## Acceptance criteria
- [ ] Staff answer → approved → next similar customer question answered from knowledge
- [ ] Rollback removes it from answers immediately
- [ ] No PII in published knowledge (test corpus)

## Rules checklist
- [ ] R-TEN-04 · R-SEC-05 · R-AI-05/07 · R-DB-07 · tests · PROGRESS_LOG · no git/Docker
