# WhatsApp Cloud API — Quick Reference

## API Base

```
https://graph.facebook.com/v21.0/
```

## Send Message

```python
POST /{phone_number_id}/messages
Authorization: Bearer {access_token}

# Text
{"messaging_product": "whatsapp", "to": "+5511999999999",
 "type": "text", "text": {"body": "Mensagem"}}

# Interactive buttons
{"messaging_product": "whatsapp", "to": "+5511999999999",
 "type": "interactive",
 "interactive": {
   "type": "button",
   "body": {"text": "Confirma o CMR?"},
   "action": {"buttons": [
     {"type": "reply", "reply": {"id": "ok",     "title": "OK"}},
     {"type": "reply", "reply": {"id": "recusar","title": "Recusar"}}
   ]}
 }}
```

## Get Media URL

```python
GET /{media_id}
Authorization: Bearer {access_token}
# Returns: {"url": "https://...", "mime_type": "image/jpeg", "file_size": 12345}
```

## Download Media

```python
GET {media_url}
Authorization: Bearer {access_token}
# Returns: raw bytes (valid ~5 minutes)
```

## Webhook Payload (minimal)

```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "id": "wamid.xxx",
          "from": "5511999999999",
          "type": "image|text|document|location|interactive",
          "timestamp": "1711234567",
          "image": {"id": "media_id", "mime_type": "image/jpeg"},
          "text": {"body": "mensagem"},
          "location": {"latitude": -23.5, "longitude": -46.6},
          "interactive": {"type": "button_reply", "button_reply": {"id": "ok"}}
        }],
        "contacts": [{"profile": {"name": "João Silva"}}]
      }
    }]
  }]
}
```

## Webhook Verification (GET)

```python
# Meta sends: ?hub.mode=subscribe&hub.challenge=xxx&hub.verify_token=TOKEN
# Must return: hub.challenge value as plain text with 200 OK
```

## HMAC Signature Verification

```python
import hashlib, hmac

def verify(payload: bytes, header: str, app_secret: str) -> bool:
    # header format: "sha256=abcdef..."
    expected = hmac.new(app_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", header)
```

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 100 | Invalid parameter | Check payload format |
| 131030 | Rate limit exceeded | Exponential backoff |
| 131047 | Message undeliverable | Check phone number |
| 131051 | Unsupported message type | Fallback to text |
| 190 | Token expired | Refresh access token |

## Rate Limits (Cloud API)

- Sending: 80 messages/second per phone number
- Media download URL validity: ~5 minutes
- Webhook delivery: Meta retries up to 20 times over 72 hours

## Message Status Flow

```
sent → delivered → read → [failed]
```

## Project Adapter Location

`functions/gcp/v1/src/shared/adapters/whatsapp.py`
- `WhatsAppCloudAdapter` — httpx-based implementation
- `WhatsAppAdapter` — Protocol for test mocking
- `verify_webhook_signature()` — HMAC helper
