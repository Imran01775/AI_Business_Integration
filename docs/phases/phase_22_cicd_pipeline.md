# Phase 22 — CI/CD Pipeline (DEFERRED)

> **Status: DEFERRED.** Do **not** create git hooks, workflow files or push anything until the owner explicitly starts this phase (R-PROC-04).
> **Prompt header (when started):** Apply `docs/GLOBAL_RULES.md`. Phase: 22. Git/CI actions explicitly approved.

## Goal
Automated quality gates and deployments per doc 15.

## Prerequisites
Phase 21; repository hosting decided (GitHub / Forgejo / Gitea); explicit approval.

## Scope (when started)
`.gitignore`, branch protection, PR template, Conventional Commits, CI workflows (path-filtered backend / ai-platform / frontend jobs), security scans, OpenAPI diff, migration check, image build + push + SBOM, staging deploy with migrations + smoke e2e, manual approval to production, release tagging + changelog.

## Tasks
1. Repo init + ignore rules + secrets scanning pre-commit.
2. CI jobs mirroring Phase 20 quality gate.
3. CD: staging auto-deploy, production with approval; rollback job.

## Acceptance criteria
- [ ] PR cannot merge with failing gates
- [ ] Main → staging deploy automatic; production by approval; rollback tested

## Rules checklist
- [ ] R-SEC-08 · R-DB-02 · PROGRESS_LOG
