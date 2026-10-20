# 21 — Requirements Traceability Matrix

> Every requirement from the chat brief and from `AI_Sales_Agent_Final_Plan_v1_5.pdf` maps to at least one architecture doc and one phase. Update this file when scope changes.

## A. Chat brief — 20 deliverables
| # | Deliverable | Architecture doc | Phase(s) |
|---|---|---|---|
| 1 | Complete system architecture | 01 | all |
| 2 | Technology stack | 02 | 00 |
| 3 | Frontend architecture | 03, 23 | 04, 15, 24 |
| 4 | Backend architecture | 04 | 01 |
| 5 | Database architecture | 05 | 02 + each feature |
| 6 | Authentication & authorization | 06 | 03, 19 |
| 7 | AI/LLM platform | 07 | 07 |
| 8 | RAG architecture | 08 | 07, 12, 16 |
| 9 | Event-driven architecture | 09 | 01 + all |
| 10 | Background processing | 10 | 01 + all |
| 11 | Caching strategy | 11 | 01, 06, 12 |
| 12 | Monitoring & observability | 12, 22 | 01, 18 |
| 13 | Security architecture | 13 | 01–03, 19 |
| 14 | Testing strategy | 14 | all, 20 |
| 15 | CI/CD strategy | 15 | 22 (deferred) |
| 16 | Docker & deployment | 16 | 21 (deferred), 23 |
| 17 | Production-readiness checklist | 17 | 23 |
| 18 | Folder structures | 18 | 00 (skeleton exists) |
| 19 | Global engineering rules | `GLOBAL_RULES.md`, `.cursor/rules/global-engineering-rules.mdc` | all |
| 20 | Phase-based Markdown files | `docs/phases/*` | 00–25 |

## B. Chat brief — cross-cutting requirements
| Requirement | Where |
|---|---|
| Modular monolith → microservice migration | 01 §7, 04, phase 25 |
| Provider-agnostic, independently scalable AI layer | 07 §2, phase 07 |
| Prompt mgmt, provider abstraction, token tracking, cost tracking, caching, RAG | 07 §5–9, 08, phases 07/08/16 |
| Independently testable components | 14, R-TEST-03 |
| API design standards | 19 |
| Infrastructure recommendations, cost-effective OSS | 02, 16 |
| Error logging & history | 22, phases 01/02/05/18 |
| Future mobile app | 23, phase 24 |
| Everything configurable (business + user + admin) | 24, phases 01/02/05/15 |

## C. PDF v1.5 — MVP scope (§11 / §30)
| PDF item | Phase |
|---|---|
| Public site + feature matrix + plans | 04 (shell, legal), 05 (pricing/matrix), 06 (public catalogue) |
| Auth, workspace, multi-tenant isolation | 02, 03 |
| Subscription request → admin approval → payment verification → entitlements | 05 |
| Statuses Draft…Expired | 05 (doc 20 §2) |
| Admin dashboard, review, plan mgmt, audit log, role separation | 05, 03 |
| Facebook Messenger (webhook, signature, messaging window) | 10 |
| Manual catalogue + CSV (template, dry-run, duplicates, rich columns, external_id) | 06 |
| Seller Conversation Rules (keyword gate, no gen. LLM) | 11 |
| Voice: STT → same pipeline; out-of-rule ignored | 13 |
| Token-efficient engine DB → Rules → FAQ → Cache → LLM | 12 |
| Never full history, tenant filter, invalidate cache on product change | 12 (+ 11 caching doc) |
| Human handoff + AI pause/resume state machine (no double reply) | 09 |
| Learning queue + rollback, no cross-tenant learning | 16 |
| Basic order capture + customer confirmation, min_price | 14, 12 |
| Usage quotas, UsageLedger (incl. STT), 80% warn, 100% pause/top-up/overage/BYO | 08 (+ 05 top-up, 07 BYO) |
| Conversation Lifecycle & Abuse Guard (statuses, rate-limit, spam_score, consecutive_irrelevant_count, configurable thresholds) | 09, 11 |
| Seller Panel: Status, Responder, Urgency, Last activity, media type, Take-over; widgets | 15 |
| Privacy, Terms, monitoring, sandbox | 04, 19, 18, 09 |
| Retention incl. audio/transcript | 13, 19 |
| Metrics incl. STT success rate & cost, cache-hit, spam blocks, budget_remaining | 08, 17, 18 |
| Plans matrix (Abuse Guard basic vs advanced, voice per plan) | 05 (entitlements), 11 |
| Meta assets early | 00, 10 |
| Test 2–3 STT providers early; provider behind interface | 00 (spike), 07 |
| Payments: verified gateway or manual transfer | 05 |
| Encrypt secrets, webhook signatures, backups | 02, 10, 19, 23 |
| Stack: Python 3.11+ FastAPI, PostgreSQL, pgvector, Redis + ARQ, Next.js | 02 |
| Hooks for future store sync (external_id, SyncConnection/SyncJob) | 02, 06, 25 |
| Phase 2: Instagram, WhatsApp, courier, richer analytics/roles | 25 |
| Phase 3+: WooCommerce/any-site sync, image recognition, advanced coach, white-label | 25 |

## D. Additions from review (implied by PDF / recommended)
| Item | Phase |
|---|---|
| FAQ management | 06 |
| Messenger page connect, token expiry alerts | 10 |
| Meta data-deletion callback | 10, 19 |
| Agent persona / reply style | 12 |
| Fair-use (spam not counted), quota-end soft handoff | 08 |
| Admin roles + seller team roles | 03, 05 |
| Customer (buyer) profiles | 09 |
| Safety validator (DB-grounded facts) | 12 |
| Urgency scoring, idle/close scheduler | 15, 09 |
| Sandbox simulator channel | 09 |
| Realtime panel (SSE), object storage, email, notification centre | 01, 15 |
| Bangla/Banglish normalisation | 11 |
| Canned replies, onboarding wizard | 15 |
| AI kill switch, budgets, cheap-model routing, eval harness | 07 |
| Data export, admin impersonation | 17, 05 |
| Settings registry, Settings Centre, user vs business scope | 01, 02, 03, 05, 15 |
| Mobile readiness (bearer auth, device sessions, app config, shared packages) | 03, 04, 24 |

## E. Configuration inventory → phase
| Settings group (doc 24) | Registered in phase |
|---|---|
| platform.*, flags.* | 01 |
| auth.*, user.* | 03 |
| plans.*, billing.*, content, admin roles | 05 |
| catalogue.* | 06 |
| ai.*, prompts | 07 |
| usage.* | 08 |
| lifecycle.*, conversations.* | 09 |
| channels.* | 10 |
| rules.*, guard.* | 11 |
| agent.*, answering.* | 12 |
| voice.* | 13 |
| orders.* | 14 |
| urgency.*, inbox.*, canned replies | 15 |
| learning.*, rag.* | 16 |
| retention.* | 13, 19 |
| app.min_supported_version | 04 / 24 |
