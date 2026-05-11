# Meta WhatsApp Cloud API — Overview

## Architecture

```
Meta Infrastructure
      │
      ├── WhatsApp Business Account (WABA)
      │     └── Phone Number (phone_number_id)
      │
      └── App (APP_ID)
            ├── Webhook subscription → Cloud Run
            └── System User → Access Token
```

## Authentication

### Access Token Types

| Type | Validity | Use case |
|------|---------|---------|
| Temporary User Token | ~60 days | Development testing |
| System User Token | Never expires | Production |
| App Token (`APP_ID|APP_SECRET`) | Permanent | Webhook management only |

**This project:** System User token stored in Secret Manager as `whatsapp-access-token`.

### API Version

Current: `v21.0`. Pin to a specific version in production — Meta deprecates old versions with ~2 years notice.

```python
GRAPH_API_BASE = "https://graph.facebook.com/v21.0"
PHONE_NUMBER_ID = "988336007706186"
```

## Request Pattern

```python
import httpx

@dataclass
class WhatsAppCloudAdapter:
    phone_number_id: str
    access_token: str
    _client: httpx.Client = field(default_factory=httpx.Client)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def send_text(self, to: str, text: str) -> str:
        resp = self._client.post(
            f"{GRAPH_API_BASE}/{self.phone_number_id}/messages",
            headers=self._headers(),
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["messages"][0]["id"]
```

## Rate Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Messages/second | 80 per phone | Aggregate across all recipients |
| Media downloads | No explicit limit | URLs expire in ~5 min |
| API calls | 200 calls/hour per token | Graph API limit |
| Message template sends | Varies by tier | Tier 1: 1,000/day |

## Phone Number Business Tiers

Determines how many unique users you can message per 24h:

| Tier | Limit |
|------|-------|
| 1 | 1,000 unique users |
| 2 | 10,000 |
| 3 | 100,000 |
| 4 | Unlimited |

Tier upgrades happen automatically based on messaging quality.

## Conversation-Based Pricing

Meta charges per **conversation** (24h window), not per message:

| Type | Who opens | Cost |
|------|-----------|------|
| User-initiated | User messages first | ~$0.0042 (Brazil) |
| Business-initiated | You message first | Higher cost by category |

**This project:** Primarily user-initiated (drivers message first) = lower cost.

## Webhook vs Polling

Meta **only supports webhooks** — there is no polling API for incoming messages. The webhook endpoint must be:
- Publicly accessible HTTPS
- Respond with 200 within 20 seconds
- Handle duplicate deliveries (at-least-once)

## Error Handling Strategy

```python
# From shared/adapters/whatsapp.py pattern
try:
    wamid = adapter.send_text(to=phone, text=message)
    logger.info("message_sent", extra={"wamid": wamid, "to": phone})
except httpx.HTTPStatusError as e:
    if e.response.status_code == 131047:  # Undeliverable
        logger.warning("message_undeliverable", extra={"to": phone})
        # Don't retry — user may have blocked or deactivated number
    elif e.response.status_code == 131030:  # Rate limited
        raise  # Let Pub/Sub retry via DLQ
    else:
        raise
```
