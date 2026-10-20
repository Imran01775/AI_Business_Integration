# Phase 23 — Deployment & Production Readiness

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 23. Requires Phases 21–22 to be approved/started for container-based deploy.

## Goal
Go live safely on cost-effective infrastructure (doc 16 stage S1) and pass the production-readiness checklist (doc 17).

## Prerequisites
Phases 00–22; Meta app review approved; production domain + email sending domain.

## Requirements covered
Chat: deployment, production readiness, infrastructure recommendations. PDF §15 monitoring, §19 recommendation "validate with real sellers".

## Scope
**In:** VM provisioning (Hetzner/DO/Contabo), OS hardening (SSH keys, firewall, fail2ban, unattended upgrades), Caddy TLS, DNS + SPF/DKIM/DMARC, production env/secrets, DB backups + PITR + offsite, restore drill, monitoring stack live, alert routing, seed production data (plans, settings, templates, admin), Meta app live mode, pilot program with 5–10 real sellers (feature flags), go-live checklist sign-off.

## Tasks
1. Infrastructure runbook `docs/runbooks/provision_vm.md`.
2. Deploy stack (compose prod), run migrations + seeds.
3. Backup + **restore drill**; record RPO/RTO.
4. Complete doc 17 checklist — every item ✅ with evidence link.
5. Pilot: onboard sellers, collect feedback, monitor cost per conversation, tune settings (not code).

## Acceptance criteria
- [ ] Doc 17 checklist complete
- [ ] Pilot sellers live with monitored cost and quality
- [ ] Incident + rollback runbooks rehearsed

## Rules checklist
- [ ] All R-* sections · CHANGELOG release entry · PROGRESS_LOG
