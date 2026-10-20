# 18 — Recommended Folder Structures

> Apply `docs/GLOBAL_RULES.md`. The skeleton below already exists in the workspace (folders + empty `__init__.py`). Files are added phase by phase.

## Repository root
```
AI_Business_Integration/
  .cursor/rules/global-engineering-rules.mdc   always-applied AI rule
  docs/
    00_INDEX.md  GLOBAL_RULES.md  CHANGELOG.md  PROGRESS_LOG.md
    architecture/   01..24 reference docs
    phases/         phase_00..phase_25 execution plans
    adr/            architecture decision records (0000-template.md)
  backend/          core API + workers (modular monolith)
  ai-platform/      reusable AI package + optional gateway service
  frontend/         pnpm/Turborepo workspace (web now, mobile later)
  requirements.txt  (legacy — ignored, do not touch)
```

## Backend (`backend/`)
```
backend/
  pyproject.toml            (Phase 00)
  alembic.ini               (Phase 02)
  .env.example              (Phase 00)
  src/app/
    main/                   app factory, DI container, routers, worker settings, CLI (seed, admin)
    core/
      config/ db/ logging/ errors/ security/ cache/ events/ jobs/ storage/ email/
      realtime/ http/ clock/ ids/ observability/ ratelimit/ idempotency/
    shared/                 kernel: entity, value_object, domain_event, money, tenant_context, pagination, result
    modules/
      identity/ tenancy/ settings/ billing/ catalogue/ faq/ customers/ channels/
      conversations/ guard_rules/ agent_settings/ answering/ orders/ learning/
      usage/ analytics/ admin/ audit/ notifications/ public/
        └─ each: domain/ application/ infrastructure/ api/ (+ settings.py, templates.py, permissions.py)
    workers/                queue worker entrypoints + cron registration
  migrations/               Alembic versions
  tests/
    unit/<module>/  integration/<module>/  contract/  e2e/  fakes/  factories/  conftest.py
```

## AI platform (`ai-platform/`)
```
ai-platform/
  pyproject.toml            (Phase 07)
  prompts/                  seed prompt YAMLs (Phase 07)
  src/ai_platform/
    contracts/  providers/{llm,stt,embeddings}/  prompts/  usage/  cache/  rag/  gateway/  client/
  tests/
    unit/  contract/  eval/ (golden sets)
```

## Frontend (`frontend/`)
```
frontend/
  package.json  pnpm-workspace.yaml  turbo.json  tsconfig.base.json   (Phase 00/04)
  apps/
    web/
      src/
        app/(public)/ (auth)/ (seller)/ (admin)/ api/
        features/
          auth onboarding settings catalogue faq customers conversations rules agent_settings
          sandbox orders billing usage analytics notifications admin platform_settings learning
            └─ each: components/ hooks/ api/ schemas/ index.ts
        shared/ui/ lib/ config/ hooks/
      tests/unit/ e2e/
    mobile/                 RESERVED (Phase 24)
  packages/
    api-client/             generated OpenAPI client
    shared/                 zod schemas, types, constants, error codes
    i18n/                   bn.json, en.json catalogues
    design-tokens/          tokens (CSS vars + TS)
```

## Naming conventions
| Item | Convention |
|---|---|
| Python modules/files | `snake_case` |
| Classes | `PascalCase`; use cases are verbs: `ApproveSubscription` |
| DB tables | plural `snake_case` |
| API paths | `/api/v1/kebab-case-plural` |
| Events | `module.entity.verb_past` |
| Settings keys | `module.group.name` e.g. `rules.irrelevant_threshold` |
| Template keys | `module.purpose` e.g. `rules.redirect_message` |
| Permissions | `module:action` |
| TS components | `PascalCase.tsx`; hooks `useThing.ts` |
