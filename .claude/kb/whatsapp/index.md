# WhatsApp Business API — Knowledge Base

> Meta WhatsApp Cloud API for building data pipelines via conversational interfaces

---

## Domain Overview

The Meta WhatsApp Business Platform enables bidirectional messaging that feeds structured data into the pipeline. In this project, WhatsApp is the **primary data ingestion channel** — drivers send documents, images, and structured messages that flow into BigQuery via Pub/Sub.

```
Driver (WhatsApp)
      │
      ▼ webhook POST
 wa_gateway (Cloud Run)
      │
      ├── intent_classifier (keyword + type routing)
      │
      ├── cmr_handler      → Gemini extraction → BigQuery
      ├── checklist_handler → structured form   → BigQuery
      ├── eco_zone_handler  → LLM Q&A           → wa_reply
      ├── pin_handler       → PIN validation    → Firestore
      └── adr_handler       → cert registration → BigQuery
```

---

## Core Concepts

| Concept | File | Summary |
|---------|------|---------|
| Webhook payload parsing | [concepts/webhooks.md](concepts/webhooks.md) | HMAC verification + nested JSON flattening |
| Message types | [concepts/message-types.md](concepts/message-types.md) | text, image, document, location, interactive |
| Phone numbers & WABA | [concepts/phone-numbers-waba.md](concepts/phone-numbers-waba.md) | E.164, WABA, phone number IDs |
| Message templates | [concepts/message-templates.md](concepts/message-templates.md) | HSM templates for outbound notifications |
| Meta API overview | [concepts/meta-api-overview.md](concepts/meta-api-overview.md) | Auth, rate limits, versioning |

---

## Patterns

| Pattern | File | Summary |
|---------|------|---------|
| Webhook handler | [patterns/webhook-handler.md](patterns/webhook-handler.md) | Signature verification + payload parsing |
| Intent-based routing | [patterns/message-routing.md](patterns/message-routing.md) | Keyword + type classifier → handler dispatch |
| Media processing | [patterns/media-processing.md](patterns/media-processing.md) | Download → Gemini vision → structured data |
| Error handling | [patterns/error-handling.md](patterns/error-handling.md) | Retry, DLQ, user-facing error messages |

---

## Quick Reference

See [quick-reference.md](quick-reference.md) for API endpoints, payload shapes, and env vars.

---

## Project-Specific Config

| Variable | Purpose |
|----------|---------|
| `WHATSAPP_PHONE_NUMBER_ID` | Phone number ID for sending messages |
| `WHATSAPP_ACCESS_TOKEN` | Meta System User access token |
| `WHATSAPP_APP_SECRET` | For HMAC-SHA256 webhook verification |
| `WHATSAPP_VERIFY_TOKEN` | Webhook registration challenge token |

Phone Number ID: `988336007706186`
WABA: stored in Secret Manager (`hub-whatsapp-dev`)

---

## API Reference

- Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
- Webhooks: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
- Message types: https://developers.facebook.com/docs/whatsapp/cloud-api/messages
- Media: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media
