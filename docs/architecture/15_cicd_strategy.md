# 15 — CI/CD Strategy

> Apply `docs/GLOBAL_RULES.md`. **DEFERRED:** no workflow files are created until Phase 22 is explicitly started (R-PROC-04).

## 1. Repository model
Single monorepo (`backend/`, `ai-platform/`, `frontend/`, `docs/`). Trunk-based development, short-lived feature branches, PRs with required review, Conventional Commits, semantic versioning per deployable.

## 2. Pipeline stages (planned)
```mermaid
flowchart LR
  pr[PullRequest] --> lint[Lint_Type_Boundaries]
  lint --> unit[UnitAndContractTests]
  unit --> integ[IntegrationTests_PG_Redis]
  integ --> fe[FrontendTests_Build]
  fe --> sec[SecurityScans]
  sec --> api[OpenAPI_diff_Migration_check]
  api --> merge[Merge_main]
  merge --> build[BuildImages_SBOM]
  build --> staging[DeployStaging_migrate]
  staging --> smoke[SmokeE2E]
  smoke --> approve[ManualApproval]
  approve --> prod[DeployProduction]
```
- **Path filters:** only run backend jobs when `backend/**` changes, etc. (Turborepo for frontend caching).
- **Security:** pip-audit, pnpm audit, Trivy (images), gitleaks (secrets), Semgrep OSS.
- **Artifacts:** versioned container images (`api`, `worker`, `ai-gateway`, `web`), OpenAPI spec, generated api-client.
- **Database:** migrations run as a separate pre-deploy job; expand/contract enforced.
- **Environments:** `dev` (local), `staging` (prod-like, sandbox Meta app), `production`.
- **Release:** tagged releases, changelog from commits, rollback = previous image + backward-compatible schema.

## 3. Tooling options (free)
GitHub Actions (free minutes for private repos limited) or self-hosted Forgejo/Gitea Actions / Woodpecker CI (OSS). Container registry: GHCR or self-hosted.

## 4. Until Phase 22
Run the same gates locally via documented commands (`uv run ruff check`, `uv run mypy`, `uv run pytest`, `pnpm -r lint test build`).
