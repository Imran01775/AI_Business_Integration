# Phase 19 — Security, Privacy & Compliance Hardening

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 19. Baseline security exists since Phases 01–03. No git/Docker.

## Goal
Bring the platform to OWASP ASVS L2 (subset), complete privacy/retention/deletion, MFA, secret rotation, and Meta/Platform compliance.

## Prerequisites
Phases 01–18.

## Requirements covered
PDF §12–15 (encrypt secrets, webhook signatures, backups, privacy, terms), §27.4 voice data retention, §11.15. Doc 13.

## Scope
**In:** TOTP MFA (platform admins mandatory, owners optional via setting), session security review, CSP tightening, rate-limit review, SSRF/upload review, prompt-injection test suite, secret rotation (master key re-wrap job), retention jobs for all data classes, tenant data export + closure deletion, buyer opt-out, Terms/Privacy versioning with acceptance records, dependency/vulnerability scans, ZAP baseline scan, pen-test checklist, incident response + secret rotation runbooks.

## Tasks
1. MFA (TOTP + recovery codes); enforce by role/setting.
2. Security headers/CSP final; CORS allow-list from settings.
3. Prompt-injection & jailbreak test set (bn/en) in eval harness; verify Safety Validator blocks price manipulation.
4. Key rotation job: re-encrypt secrets to new `key_version`.
5. Retention engine: per data class from settings (`retention.*`), purge + audit; legal hold flag.
6. Tenant closure: export → grace period → deletion job; buyer data deletion (Meta callback) end-to-end.
7. Legal docs versioning + acceptance (`legal_acceptances`).
8. Scans: pip-audit, pnpm audit, gitleaks-style secret scan (local), Semgrep OSS, ZAP baseline — results recorded.

## DB changes
`mfa_factors`, `recovery_codes`, `legal_documents`, `legal_acceptances`, `retention_runs`, `legal_holds`.

## Acceptance criteria
- [ ] ASVS L2 subset checklist passed
- [ ] Retention + deletion verified with tests and audit entries
- [ ] Master key rotation tested
- [ ] No critical findings open

## Rules checklist
- [ ] R-SEC-01..10 · R-CFG-06 · tests · PROGRESS_LOG · no git/Docker
