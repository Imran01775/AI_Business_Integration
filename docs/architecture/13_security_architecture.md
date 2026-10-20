# 13 — Security Architecture

> Apply `docs/GLOBAL_RULES.md` (esp. R-SEC-*, R-TEN-*, R-CFG-06).

## 1. Threat model (STRIDE summary)
| Threat | Example | Controls |
|---|---|---|
| Spoofing | fake Meta webhook, stolen token | HMAC signature verification, short JWT, refresh rotation + reuse detection, MFA (owners/admins) |
| Tampering | price manipulation via prompt injection | Safety Validator vs DB, `min_price` hard rule, tool allow-list, order confirmation |
| Repudiation | admin approves fake payment | append-only audit_log with actor + before/after |
| Information disclosure | cross-tenant leak | RLS, tenant-scoped cache/storage/RAG, tenant isolation tests |
| DoS / cost abuse | message floods, voice spam | Conversation Guard rate-limit, spam score, quotas, budgets, kill switch, max audio duration |
| Elevation | agent changes billing | RBAC + policies + entitlements, deny by default |

## 2. Controls by layer
- **Edge:** TLS (Caddy auto-HTTPS), HSTS, security headers (CSP, X-Frame-Options, Referrer-Policy), request size limits, IP rate limits, optional Cloudflare free tier/WAF.
- **App:** Pydantic/Zod validation, output encoding, CSRF (web), CORS allow-list, SSRF protection on any URL fetch (Meta media URLs only from allow-listed hosts), upload validation (MIME sniffing, size, audio duration, CSV row limits, formula-injection escaping on export).
- **Data:** RLS, least-privilege DB roles, encryption at rest for secrets (envelope: data key per record, master key from env/KMS, key rotation via `key_version`), backups encrypted.
- **Secrets:** never in code/repo/logs/frontend; `.env` only for local; secrets table for tenant/provider secrets; Vault/Infisical later.
- **AI-specific:** prompt-injection defense (strict system prompt, no tenant-controlled system prompt, delimiters, tool allow-list), PII redaction before provider calls (configurable), no cross-tenant memory, output validation, LLM never executes actions without deterministic checks (orders need customer confirmation).
- **Supply chain:** pinned lockfiles (uv.lock, pnpm-lock), `pip-audit`, `pnpm audit`, Trivy image scan (later), Dependabot/Renovate, SBOM (later).

## 3. Privacy & compliance
- Privacy Policy + Terms pages (versioned, user acceptance recorded) — required for Meta app review.
- Meta **data deletion callback** + user-facing deletion instructions; buyer opt-out ("stop").
- Retention per data class (settings, platform bounds): audio (short, e.g. 7–30 days), transcripts, messages, logs, exports; enforced by cron.
- Data export for tenants; data deletion on tenant closure (grace period).
- Bangladesh data protection considerations + Meta Platform Terms compliance.

## 4. Security operations
Audit log review, admin login alerts, failed-login monitoring, dependency updates monthly, pen-test checklist before go-live (OWASP ASVS L2 subset), incident response runbook, secret rotation runbook.
