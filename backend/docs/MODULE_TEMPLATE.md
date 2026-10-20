# Backend module template

Apply `docs/GLOBAL_RULES.md` (R-ARCH-01..03).

## Layout

```
modules/<name>/
  domain/          entities, value objects, events, repository ports
  application/     use cases, DTOs, public facade, outbound ports
  infrastructure/  ORM models, adapters, handlers, jobs
  api/             FastAPI routers and schemas
  settings.py      SettingDefinition declarations
  templates.py     message template keys
  permissions.py   permission constants
```

Dependencies flow inward: `api → application → domain`, `infrastructure → application/domain`.

## Generator

```bash
cd backend
uv run python scripts/new_module.py <module_name>
```

After generation, register the module in `backend/.importlinter` contracts and add routers in `app/main/app_factory.py` when the module exposes HTTP APIs.

## Checklist

- [ ] Domain has no FastAPI/SQLAlchemy/Redis imports
- [ ] Cross-module access only via `application.facade` or events
- [ ] Settings keys declared in `settings.py`
- [ ] Unit tests for use cases with in-memory port fakes
