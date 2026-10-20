# Backup & restore runbook

> Targets from doc 05: RPO ≤ 15 min, RTO ≤ 2 h. Production tooling (pgBackRest / WAL-G) is configured outside this repo.

## 1. Scope
- PostgreSQL cluster (all tenant data, platform tables, `ai` schema when added).
- Continuous WAL archiving to object storage.
- Monthly restore drill.

## 2. Backup policy
| Type | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| Full base backup | Daily | 30 days | Object storage (S3-compatible) |
| WAL segments | Continuous | 15 days | Same bucket, separate prefix |
| Logical dump (sanity) | Weekly | 7 days | Encrypted object storage |

## 3. Pre-requisites
- `app_owner` credentials stored in secrets manager (never in git).
- Backup agent runs as OS user with read access to PG data directory or uses `pg_basebackup` remotely.
- Bucket versioning enabled; cross-region replication for production.

## 4. Full backup (pgBackRest example)
```bash
pgbackrest --stanza=main backup --type=full
pgbackrest --stanza=main info
```

## 5. Point-in-time recovery (outline)
1. Stop API and workers.
2. Restore latest full backup to a clean data directory.
3. Configure `recovery_target_time` and `restore_command` for WAL replay.
4. Start PostgreSQL in recovery mode; verify `pg_is_in_recovery()` until complete.
5. Run `alembic current` — schema version must match release tag.
6. Smoke test: health endpoints, one tenant-scoped read with `app_rw`, outbox relay dry-run.
7. Resume traffic.

## 6. Logical restore (dev / single-tenant export)
```bash
pg_dump -Fc "$DATABASE_OWNER_URL" -f sales_agent.dump
pg_restore -d "$DATABASE_OWNER_URL" --clean --if-exists sales_agent.dump
```

## 7. Verification checklist
- [ ] Row counts for `tenants`, `setting_definitions` match expectations
- [ ] RLS enabled on tenant tables (`SELECT relrowsecurity FROM pg_class WHERE relname = 'secrets'`)
- [ ] Secrets decrypt with current `SECRETS_KEY_VERSION`
- [ ] `outbox_events` pending count stable after relay start

## 8. Incident contacts
Document on-call rotation and cloud provider support in internal ops wiki (not in repo).
