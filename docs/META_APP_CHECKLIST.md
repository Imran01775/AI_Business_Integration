# Meta (Facebook) developer app checklist

> Start in Phase 00 — business verification and app review can take weeks.  
> Product: Messenger channel for seller–customer conversations (Phase 10).

## Ownership & tracking

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Meta Business Portfolio created | ☐ | | Legal business name matches verification docs |
| Business verification submitted | ☐ | | Allow 1–4+ weeks |
| Developer app created | ☐ | | Type: **Business** |
| App admin / emergency contact assigned | ☐ | | At least two admins recommended |
| Privacy policy URL live | ☐ | | Public HTTPS, describes Messenger data use |
| Data deletion instructions URL | ☐ | | Required for app review |
| Terms / support contact on policy page | ☐ | | |

## App configuration

| Item | Status | Notes |
|------|--------|-------|
| **Messenger** product added | ☐ | |
| Facebook Page linked to app | ☐ | Test Page for dev, production Page later |
| Webhooks URL planned | ☐ | `https://<api-host>/api/v1/webhooks/messenger` (Phase 10) |
| Webhook verify token stored in secrets store | ☐ | Not in settings JSON or frontend |
| App mode: Development → Live | ☐ | Only after review |

## Permissions (request in app review)

| Permission | Purpose | Review artefact |
|------------|---------|-----------------|
| `pages_messaging` | Send/receive customer messages | Screencast: seller inbox + automated reply |
| `pages_manage_metadata` | Subscribe Page to webhooks | Screencast: connect Page in seller settings |
| `pages_show_list` | List Pages user can connect | Screencast: Page picker in onboarding |

Optional later (not MVP unless needed):

- `pages_read_engagement` — only if product needs read-side Page insights in-app.

## App review screencast plan

Record one continuous flow (English or Bangla UI captions):

1. Seller logs into the platform (sandbox acceptable before production URL).
2. Seller connects a Facebook Page (OAuth / Page selection).
3. Customer sends a Messenger message; message appears in seller conversation inbox.
4. AI or seller reply is delivered back to Messenger (show delivery in Messenger client).
5. Seller disconnects Page or revokes access (data deletion path mentioned).

Include on-screen captions for: what data is collected, retention, and how to request deletion.

## Security & compliance notes

- Verify webhook signatures on every inbound request (Phase 10).
- Store Page access tokens only in the **encrypted secrets store** (R-CFG-06).
- Log `tenant_id` on all channel operations; never mix Pages across tenants.
- Document data flows in privacy policy: message content, profile metadata, voice attachments (STT).

## Links

- [Meta for Developers](https://developers.facebook.com/)
- [Messenger Platform overview](https://developers.facebook.com/docs/messenger-platform/)
- [App Review](https://developers.facebook.com/docs/app-review/)
