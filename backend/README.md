# Backend (modular monolith)

Python 3.12 · uv · FastAPI · SQLAlchemy async.

## Install

```bash
cd backend
uv sync
```

## Quality commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run lint-imports
uv run pytest
uv run pip-audit
```

See `docs/LOCAL_SETUP.md` for PostgreSQL, Redis, MinIO, and Mailpit.

## Run API (development)

```bash
uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src
```

Module scaffold: `uv run python scripts/new_module.py <name>` — see `docs/MODULE_TEMPLATE.md`.
