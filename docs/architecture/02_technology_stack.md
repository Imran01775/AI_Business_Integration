# 02 — Technology Stack

> Apply `docs/GLOBAL_RULES.md`. Preference: free & open-source, cost-effective, mature.

## Backend
| Concern | Choice | License | Notes |
|---|---|---|---|
| Language | Python 3.12 | PSF | PDF requires 3.11+ |
| Web framework | FastAPI | MIT | Async, OpenAPI native |
| Validation | Pydantic v2 + pydantic-settings | MIT | Typed config |
| ORM / SQL | SQLAlchemy 2.0 async + asyncpg | MIT | |
| Migrations | Alembic | MIT | |
| Package manager | uv | MIT/Apache | Fast, lockfile |
| Lint/format | Ruff | MIT | |
| Types | mypy (strict) | MIT | |
| Tests | pytest, pytest-asyncio, hypothesis, testcontainers, respx, freezegun/injected clock | MIT/Apache | |
| Boundaries | import-linter | BSD | Module boundary enforcement |
| DI | Explicit composition root (`dependency-injector` optional) | BSD | Keep simple |
| Logging | structlog | MIT/Apache | JSON logs |
| Background jobs | ARQ (Redis) behind `JobQueue` port | MIT | PDF: ARQ/Celery → ARQ chosen; Celery swappable |
| Events | Transactional outbox + Redis Streams behind `EventBus` port | — | NATS/Kafka later |
| HTTP client | httpx | BSD | |
| Resilience | tenacity (retry), custom circuit breaker | Apache | |
| CSV | Python `csv` + Pydantic row models (polars optional for big files) | — | |
| Crypto | `cryptography` (Fernet/AES-GCM envelope), argon2-cffi, PyJWT | Apache/MIT | |

## AI platform (`ai-platform/`)
| Concern | Choice | Notes |
|---|---|---|
| LLM adapters | OpenAI-compatible adapter (OpenAI, Groq, Together, OpenRouter, vLLM, Ollama), Anthropic, Gemini | Own interface; no lock-in |
| STT adapters | faster-whisper (self-host, OSS), Google STT, Azure Speech; others pluggable | Bangla quality to be evaluated (Phase 00 spike) |
| Embeddings | OpenAI-compatible embeddings, local `bge-m3` / `multilingual-e5` via sentence-transformers/TEI | Multilingual (bn) |
| Token counting | tiktoken / provider usage fields | |
| LLM tracing (optional) | Langfuse (self-host, MIT) | |
| Evaluation | pytest-based golden sets + optional promptfoo | |

## Data
| Concern | Choice | Notes |
|---|---|---|
| RDBMS | PostgreSQL 16 | RLS, JSONB, partitioning |
| Vectors | pgvector (HNSW) | RAG, semantic FAQ match |
| Full-text | PostgreSQL FTS + `pg_trgm` | Product/FAQ search, Banglish fuzzy |
| Cache / queue / rate limit / pub-sub | Redis 7 (or Valkey) | |
| Object storage | MinIO (S3 API) | CSV, audio, proofs, images |
| Connection pooling (later) | PgBouncer | |

## Frontend
| Concern | Choice |
|---|---|
| Monorepo | pnpm workspaces + Turborepo |
| Web | Next.js 15 (App Router), React 19, TypeScript strict |
| Styling / UI | Tailwind CSS, shadcn/ui (Radix), lucide icons |
| Server state | TanStack Query |
| Forms | react-hook-form + Zod |
| i18n | next-intl (bn, en) with catalogues in `packages/i18n` |
| API client | openapi-typescript + openapi-fetch (generated in `packages/api-client`) |
| Tables / charts | TanStack Table, Recharts |
| Realtime | EventSource (SSE) wrapper |
| Tests | Vitest, Testing Library, Playwright, MSW |
| Mobile (future) | PWA first → Expo / React Native reusing packages |

## Platform & operations
| Concern | Choice |
|---|---|
| Reverse proxy / TLS | Caddy (auto HTTPS) |
| Containers (deferred) | Docker + Docker Compose → k3s later |
| CI/CD (deferred) | GitHub Actions or Gitea/Forgejo Actions (OSS) |
| Metrics | Prometheus + Grafana |
| Logs | Loki + Promtail/Alloy |
| Traces | OpenTelemetry SDK + Tempo |
| Errors | GlitchTip (OSS, Sentry-compatible SDK) |
| Uptime | Uptime Kuma |
| Secrets | Env vars + encrypted secrets table; Vault/Infisical (OSS) later |
| Backups | pgBackRest or WAL-G → object storage |
| Email (dev) | Mailpit |
| Feature flags | Built-in (settings + entitlements); Unleash (OSS) optional later |

## Payments (Bangladesh)
Manual transfer (bKash/Nagad/bank, proof upload) at MVP; gateway port for SSLCommerz / bKash PGW / Nagad later.

## Cost profile (start)
Single VM (e.g. 4 vCPU / 8–16 GB) hosting API, workers, PG, Redis, MinIO, monitoring. LLM/STT pay-per-use with budgets. Scale out per §6 of doc 01 when metrics require.
