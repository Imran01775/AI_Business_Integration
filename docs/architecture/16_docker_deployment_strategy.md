# 16 — Docker & Deployment Strategy

> Apply `docs/GLOBAL_RULES.md`. **DEFERRED:** no Dockerfile / compose / infra files are created until Phase 21 / 23 are explicitly started (R-PROC-04).

## 1. Deployable units
| Unit | Process | Scale independently |
|---|---|---|
| `api` | FastAPI (uvicorn workers, gunicorn optional) | yes (stateless) |
| `worker-*` | ARQ worker per queue group (inbound, stt, ai, outbound, import/indexing, notifications, events) | yes |
| `scheduler` | ARQ cron (leader-locked) | single |
| `ai-gateway` | `ai_platform.gateway` (when remote mode) | yes |
| `web` | Next.js standalone server | yes |
| stateful | PostgreSQL (+pgvector), Redis, MinIO | managed or self-hosted |
| observability | Prometheus, Grafana, Loki, Tempo, GlitchTip, Uptime Kuma | — |

## 2. Container principles (for Phase 21)
Multi-stage builds, slim/distroless base, non-root user, read-only FS where possible, healthchecks, one process per container, config via env, images tagged by git SHA + semver, SBOM, no secrets baked in.

## 3. Deployment stages (cost-effective growth path)
| Stage | Topology | Approx. trigger |
|---|---|---|
| S1 — MVP | 1 VM (4 vCPU/8–16 GB, e.g. Hetzner/DigitalOcean/Contabo): Docker Compose, Caddy, all services, nightly offsite backups | < ~200 tenants |
| S2 — Split data | App VM(s) + dedicated DB VM (or managed PG) + object storage service | DB CPU/IO > 60% |
| S3 — Horizontal | 2–3 app nodes behind LB, k3s, separate worker pools, PgBouncer, read replica, Redis HA | sustained load / HA need |
| S4 — Services | Extract AI gateway / channel ingress / analytics to own deployments; broker (NATS/Kafka) | team/scale needs (ADR) |

## 4. Environments
`local` (services run natively or via compose later), `staging`, `production`; identical config schema; feature flags for gradual rollout.

## 5. Release strategy
Rolling updates (S1: blue/green via Caddy upstream swap), migrations before deploy (expand), contract later; health-gated; instant rollback to previous image.

## 6. Self-hosted STT note
faster-whisper on CPU is cheap but slow; consider a small GPU node or provider API for production depending on Phase 00 evaluation and cost.
