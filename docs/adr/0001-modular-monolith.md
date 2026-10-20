# ADR 0001 — Modular monolith backend

- Status: accepted
- Date: 2026-10-13
- Phase: 00
- Related rules: R-ARCH-01, R-ARCH-02, R-ARCH-03, R-ARCH-06, R-ARCH-07

## Context

The platform must support many business capabilities (catalogue, conversations, billing, AI answering, channels) with strong tenant isolation, testability, and a path to scale without premature microservice complexity.

## Options considered

1. **Single layered codebase** — one `services/` folder; fast initially, boundaries erode under pressure.
2. **Modular monolith** — bounded modules with domain/application/infrastructure/api layers and import-linter enforcement.
3. **Microservices from day one** — independent deployables per capability; high operational cost before traffic justifies it.

## Decision

Adopt a **modular monolith** under `backend/src/app/modules/<module>/` with inward-only dependencies, cross-module access only via `application` facades or domain events, and `import-linter` contracts (see `backend/.importlinter`). Extraction to a separate service requires an ADR and changes only caller adapters (R-ARCH-06).

## Consequences

- **Positive:** Clear ownership per module, enforceable boundaries, single deployable for MVP cost profile, aligns with GLOBAL_RULES and phase vertical slices.
- **Negative:** Discipline required on imports and schema ownership; shared database needs RLS and module-owned tables (Phase 02).
- **Follow-ups:** Phase 01 composition root; module generator; tenant-isolation tests per module (R-TEN-05).
