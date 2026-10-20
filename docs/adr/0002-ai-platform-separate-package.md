# ADR 0002 — AI platform as separate Python package

- Status: accepted
- Date: 2026-10-13
- Phase: 00
- Related rules: R-AI-01, R-ARCH-04, R-ARCH-06

## Context

LLM, STT, embeddings, prompts, and evaluation harnesses must not leak provider SDKs into business modules. The same AI capabilities may run in-process inside the API today and as a dedicated gateway service later.

## Options considered

1. **AI code inside `backend/src/app/modules/answering`** — simple, but couples provider SDKs to the monolith and complicates reuse and independent scaling.
2. **`ai-platform` installable package** — `ai_platform` imported only via `AIClient` port; providers isolated under `ai_platform/providers/`.
3. **External SaaS-only** — no first-party package; violates provider-pluggability and Bangla/STT evaluation needs.

## Decision

Ship **`ai-platform/`** as an independent uv project (`pyproject.toml`, package `ai_platform`). The backend depends on it as an **editable** path dependency (`tool.uv.sources` in `backend/pyproject.toml`). Business modules call **`AIClient`** only (implemented in Phase 07); provider SDKs stay under `ai_platform/providers/`.

## Consequences

- **Positive:** Enforced R-AI-01 boundary, shared eval harness (`ai-platform/tests/eval/`), optional HTTP gateway without rewriting domain logic.
- **Negative:** Two Python projects to version and test; release coordination until CI (Phase 22).
- **Follow-ups:** Phase 07 client + providers; STT choice ADR 0004 after evaluation spike.
