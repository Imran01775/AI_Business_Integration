# Phase 25 — Future Extensions (Phase 2 / 3+ roadmap)

> **Status: FUTURE.** Each item starts with an ADR and its own phase file (`phase_25x_<name>.md`). **Prompt header:** Apply `docs/GLOBAL_RULES.md`.

## Hooks already reserved
`ChannelAdapter` port + registry, `products.external_id`, `sync_connections`/`sync_jobs` tables, pipeline `PipelineStage` slots (e.g. image), `NotificationChannel` port, `PaymentGateway` port, `IdentityProvider` port, AI provider registry, settings registry + entitlements, white-label-ready theming via design tokens.

## Roadmap items (from PDF §11 Phase 2 / Phase 3+)
| Item | Approach | Main touch points |
|---|---|---|
| Instagram DM | new `InstagramChannelAdapter` (Meta Graph, same webhook infra) | `channels` only |
| WhatsApp Business (Cloud API) | `WhatsAppChannelAdapter`, template messages for out-of-window | `channels`, templates |
| Courier integration (Pathao, Steadfast, RedX, etc.) | `CourierProvider` port + adapters; order → shipment | `orders` (+ new `shipping` module) |
| Richer analytics & roles | custom roles (permission sets), cohort analytics, Metabase (OSS) | `tenancy`, `analytics` |
| Store sync (WooCommerce / Shopify / any-site) | `StoreConnector` port; `SyncConnection` + `SyncJob`; mapping via `external_id`; webhooks + scheduled pulls | new `sync` module, `catalogue` |
| Image recognition (customer sends product photo) | `ImageStage` in pipeline → `AIClient.vision` capability → product match via embeddings | `ai_platform`, `answering` |
| Advanced coach (reply quality suggestions for staff) | analysis jobs over human replies, suggestions in panel | `learning` |
| White-label | per-tenant/partner branding via design tokens + custom domain + email domain | `tenancy`, `settings`, web |
| Online payment gateways (SSLCommerz, bKash PGW, Nagad) | `PaymentGateway` adapters | `billing` |
| Social/OIDC login, Keycloak | `IdentityProvider` adapters | `identity` |

## Microservice extraction (when metrics justify — ADR required)
1. **AI platform** → already separate; switch `AI_MODE=remote`, scale gateway pods.
2. **Channel ingress** (webhook spikes) → separate service publishing `channels.message.received` to broker.
3. **Analytics** → separate read service + replica DB.
4. Event bus Redis Streams → NATS JetStream / Kafka (adapter swap).
Procedure: freeze module facade → generate HTTP client adapter → move tables to own DB → dual-run → cut over.

## Rules checklist
- [ ] ADR per item · no core business logic change for new channels/providers (adapter-only) · PROGRESS_LOG
