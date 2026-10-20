# Local development setup

> Apply `docs/GLOBAL_RULES.md`. Native services on Windows or WSL — no Docker required for day-to-day dev (integration tests optionally use Docker via testcontainers).

Use this guide when cloning the repo on a **new machine**. Install tools first, then language dependencies, then infrastructure services, then database migrations and seeds.

## Quick start (new machine)

From the repository root (`AI_Business_Integration/`):

```bash
# 1) Python packages (order matters: ai-platform before backend)
cd ai-platform && uv sync && cd ..
cd backend && uv sync && cd ..

# 2) Frontend
cd frontend && corepack enable && pnpm install && cd ..

# 3) Environment files
cp backend/.env.example backend/.env
cp frontend/apps/web/.env.example frontend/apps/web/.env.local

# 4) Start PostgreSQL, Redis, MinIO, Mailpit (sections below), then:
cd backend
uv run alembic upgrade head
uv run python -m app.main.cli seed
uv run python -m app.main.cli seed-super-admin --email admin@localhost --password 'ChangeMeNow123!'

# 5) Run API + web
uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src
# separate terminal:
cd ../frontend/apps/web && pnpm dev
```

**PowerShell (Windows)** — use `Copy-Item` instead of `cp`:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\apps\web\.env.example frontend\apps\web\.env.local
```

---

## Prerequisites (system tools)

| Tool | Minimum version | Pin / notes | Install |
|------|-----------------|-------------|---------|
| **Git** | 2.40+ | — | [git-scm.com](https://git-scm.com/) |
| **Python** | **3.12+** | Backend + `ai-platform` | [python.org](https://www.python.org/downloads/) or `uv python install 3.12` |
| **[uv](https://docs.astral.sh/uv/)** | latest | Manages venv + lock sync | `pip install uv` or [uv installer](https://docs.astral.sh/uv/getting-started/installation/) |
| **Node.js** | **22+** | LTS recommended | [nodejs.org](https://nodejs.org/) |
| **pnpm** | **9.15.4** | Matches `frontend/package.json` `packageManager` | `corepack enable` then `corepack prepare pnpm@9.15.4 --activate` |
| **PostgreSQL** | **16+** | Extensions below | [postgresql.org](https://www.postgresql.org/download/) |
| **Redis** | **7+** | Or Valkey 7+ | Memurai (Windows) or WSL `redis-server` |
| **MinIO** | latest | S3-compatible API | [min.io/download](https://min.io/download) |
| **Mailpit** | latest | Dev SMTP + inbox UI | [mailpit.axllent.org](https://mailpit.axllent.org/docs/install/) |
| **Docker** | optional | Only for `pytest -m integration` (testcontainers) | Docker Desktop / Engine |

### PostgreSQL extensions (required)

Migrations enable these on the app database:

| Extension | Purpose |
|-----------|---------|
| `vector` | pgvector (RAG / embeddings, Phase 02+) |
| `pg_trgm` | Fuzzy text search |
| `citext` | Case-insensitive email (auth) |
| `pgcrypto` | Crypto helpers |

`alembic upgrade head` runs `CREATE EXTENSION IF NOT EXISTS …` when the DB user can create extensions (typical for local `sales_agent` owner).

---

## Monorepo install (language packages)

Always install **`ai-platform` before `backend`** (editable path dependency in `backend/pyproject.toml`).

```bash
cd ai-platform
uv sync          # installs runtime + dev group (default)

cd ../backend
uv sync          # installs runtime + dev group (default)

cd ../frontend
corepack enable
corepack prepare pnpm@9.15.4 --activate
pnpm install     # all workspace packages (web, api-client, shared, …)
```

### Without `uv`

```bash
cd ai-platform && pip install -e ".[dev]"   # if you add optional extras manually
cd ../backend && pip install -e ".[dev]"
```

Prefer **`uv sync`** so versions match `pyproject.toml` / lockfile.

---

## Python packages (`backend`)

Source: `backend/pyproject.toml`. `uv sync` installs **runtime + dev** (`default-groups = ["dev"]`).

### Runtime dependencies

| Package | Constraint |
|---------|------------|
| ai-platform | local editable `../ai-platform` |
| alembic | >=1.14 |
| argon2-cffi | >=23.1 |
| arq | >=0.26 |
| asyncpg | >=0.30 |
| cryptography | >=44.0 |
| email-validator | >=2.2 |
| fastapi | >=0.115 |
| httpx | >=0.28 |
| jinja2 | >=3.1 |
| minio | >=7.2 |
| opentelemetry-api | >=1.29 |
| opentelemetry-exporter-otlp-proto-http | >=1.29 |
| opentelemetry-instrumentation-fastapi | >=0.50b0 |
| opentelemetry-instrumentation-httpx | >=0.50b0 |
| opentelemetry-instrumentation-redis | >=0.50b0 |
| opentelemetry-instrumentation-sqlalchemy | >=0.50b0 |
| opentelemetry-sdk | >=1.29 |
| prometheus-client | >=0.21 |
| pydantic | >=2.10 |
| pydantic-settings | >=2.7 |
| pyjwt | >=2.10 |
| redis | >=5.2 |
| sentry-sdk | >=2.19 |
| sqlalchemy[asyncio] | >=2.0.36 |
| structlog | >=24.4 |
| tenacity | >=9.0 |
| uuid6 | >=2024.7 |
| uvicorn[standard] | >=0.34 |

### Dev dependencies (backend)

| Package | Constraint |
|---------|------------|
| hypothesis | >=6.120 |
| import-linter | >=2.1 |
| mypy | >=1.14 |
| pip-audit | >=2.7 |
| polyfactory | >=2.18 |
| pytest | >=8.3 |
| pytest-asyncio | >=0.25 |
| pytest-cov | >=6.0 |
| respx | >=0.22 |
| ruff | >=0.9 |
| testcontainers | >=4.9 |

List exact resolved versions on your machine:

```bash
cd backend && uv pip list
```

---

## Python packages (`ai-platform`)

Source: `ai-platform/pyproject.toml`.

### Runtime

| Package | Constraint |
|---------|------------|
| httpx | >=0.28 |
| pydantic | >=2.10 |
| structlog | >=24.4 |
| tenacity | >=9.0 |

### Dev

| Package | Constraint |
|---------|------------|
| hypothesis | >=6.120 |
| mypy | >=1.14 |
| pytest | >=8.3 |
| pytest-asyncio | >=0.25 |
| pytest-cov | >=6.0 |
| respx | >=0.22 |
| ruff | >=0.9 |

---

## Node packages (`frontend`)

Source: workspace `package.json` files. **`pnpm install`** at `frontend/` installs the full tree (including transitive deps).

| Workspace | Role |
|-----------|------|
| `frontend/` (root) | turbo, prettier, typescript |
| `frontend/apps/web` | Next.js 15, React 19, TanStack Query, Radix, Sentry, next-intl, Playwright, Vitest |
| `frontend/packages/api-client` | openapi-fetch, openapi-typescript |
| `frontend/packages/shared` | zod |
| `frontend/packages/design-tokens` | tailwindcss |
| `frontend/packages/i18n` | shared i18n helpers |
| `frontend/packages/eslint-config` | eslint 9, typescript-eslint |
| `frontend/packages/prettier-config` | shared Prettier config |

Pinned at repo root: **`pnpm@9.15.4`** (`packageManager` in `frontend/package.json`).

List direct deps for the web app:

```bash
cd frontend/apps/web && pnpm list --depth 0
```

Regenerate API client after backend OpenAPI changes:

```bash
cd frontend && pnpm gen:api
```

---

## PostgreSQL 16

### Windows (installer)

1. Install PostgreSQL 16 from [postgresql.org](https://www.postgresql.org/download/windows/).
2. Install **pgvector** for your PG major version, or use WSL (below) if the extension is easier there.
3. Create role and database:

```sql
CREATE USER sales_agent WITH PASSWORD 'sales_agent';
CREATE DATABASE sales_agent OWNER sales_agent;
\c sales_agent
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

### WSL (Ubuntu)

```bash
sudo apt update
sudo apt install -y postgresql-16 postgresql-16-pgvector
sudo service postgresql start
sudo -u postgres psql -c "CREATE USER sales_agent WITH PASSWORD 'sales_agent';"
sudo -u postgres psql -c "CREATE DATABASE sales_agent OWNER sales_agent;"
sudo -u postgres psql -d sales_agent -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d sales_agent -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
sudo -u postgres psql -d sales_agent -c "CREATE EXTENSION IF NOT EXISTS citext;"
sudo -u postgres psql -d sales_agent -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
```

**Connection string** (default in `backend/.env.example`):

`postgresql+asyncpg://sales_agent:sales_agent@localhost:5432/sales_agent`

**Migrations** (from `backend/`):

```bash
uv run alembic upgrade head
```

Optional: set `DATABASE_OWNER_URL` to a superuser URL if extensions fail under `sales_agent` (see `backend/migrations/env.py`).

---

## Redis

### Windows

- [Memurai](https://www.memurai.com/) (Redis-compatible), or Redis in WSL:

```bash
sudo apt install -y redis-server
sudo service redis-server start
redis-cli ping   # PONG
```

URL: `redis://localhost:6379/0`

---

## MinIO

### Windows binary

1. Download from [min.io](https://min.io/download).
2. Run:

```powershell
minio server C:\minio-data --console-address ":9001"
```

3. Console: http://localhost:9001 — create bucket **`sales-agent`**, keys per `backend/.env.example`.

API: `http://localhost:9000`

### WSL

```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
mkdir -p ~/minio-data
./minio server ~/minio-data --console-address ":9001"
```

---

## Mailpit

### Windows

Download from [mailpit.axllent.org](https://mailpit.axllent.org/docs/install/), run `mailpit`.

- SMTP: `localhost:1025`
- Web UI: http://localhost:8025

### WSL / Go

```bash
go install github.com/axllent/mailpit@latest
mailpit
```

---

## Environment files

```bash
cp backend/.env.example backend/.env
cp frontend/apps/web/.env.example frontend/apps/web/.env.local
```

| File | Purpose |
|------|---------|
| `backend/.env` | DB, Redis, S3, SMTP, JWT, secrets encryption |
| `frontend/apps/web/.env.local` | `BACKEND_URL`, `NEXT_PUBLIC_API_BASE_URL` |

Generate strong dev secrets (example):

```bash
# JWT_SECRET — at least 16 chars; production: openssl rand -hex 32
# SECRETS_ENCRYPTION_KEY — 32+ bytes for AES-GCM envelope
```

Optional backend vars (defaults exist): `JWT_ACCESS_TOKEN_TTL_SECONDS`, `JWT_REFRESH_TOKEN_TTL_DAYS`, `AUTH_MAX_SESSIONS`, `USE_IN_MEMORY_ADAPTERS` (skips Redis/SQL adapters for some tests).

If PostgreSQL or Redis runs in **WSL** while the API runs on **Windows**, point URLs at `localhost` with correct port forwarding or the WSL host IP.

---

## Database seed & platform admin

From `backend/` (after `alembic upgrade head`):

```bash
uv run python -m app.main.cli seed
uv run python -m app.main.cli seed-super-admin --email admin@localhost --password 'YourSecurePassword123!'
```

`seed` syncs setting definitions and default message templates (bn/en).  
`seed-super-admin` creates or promotes a verified super-admin user.

---

## Run development servers

### API (`backend/`)

```bash
uv run uvicorn app.main.app_factory:create_app --factory --reload --app-dir src
```

- OpenAPI: http://localhost:8000/api/v1/docs  
- Health: http://localhost:8000/api/v1/health (if routed)

### Web (`frontend/apps/web/`)

```bash
pnpm dev
```

- App: http://localhost:3000

### Workers (optional, when jobs are wired)

```bash
cd backend
uv run arq app.workers.arq_settings.WorkerSettings
```

---

## Quality commands

### Backend (`backend/`)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run lint-imports
uv run pytest                    # unit + contract; integration may skip without Docker
uv run pytest -m integration     # needs Docker for PostgreSQL testcontainers
uv run pip-audit
```

### AI platform (`ai-platform/`)

```bash
uv run ruff check .
uv run mypy src
uv run pytest
```

### Frontend (`frontend/`)

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm audit
```

---

## Troubleshooting (new machine)

| Issue | What to check |
|-------|----------------|
| `uv sync` fails on `ai-platform` | Run `cd ai-platform && uv sync` first; path `../ai-platform` must exist relative to `backend/`. |
| `email-validator` / import errors | Re-run `cd backend && uv sync` (listed in `pyproject.toml`). |
| Alembic / extension errors | DB user must allow `CREATE EXTENSION`; or use `DATABASE_OWNER_URL` with a superuser. |
| Redis connection errors | Start Redis/Memurai; or set `USE_IN_MEMORY_ADAPTERS=true` only for limited local testing. |
| Integration tests skip | Install Docker; tests use `testcontainers` for PostgreSQL 16. |
| pnpm version mismatch | `corepack prepare pnpm@9.15.4 --activate` |

---

## Long-lead external work (start early)

- Meta Messenger app: `docs/META_APP_CHECKLIST.md`
- Bangla STT evaluation: `ai-platform/tests/eval/stt/README.md`
