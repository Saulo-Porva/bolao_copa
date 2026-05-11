# WhatsApp Message Types

## Incoming Message Types (from webhook)

| type | Payload key | Use in this project |
|------|------------|---------------------|
| `text` | `msg["text"]["body"]` | Intent keywords, Q&A, PIN codes |
| `image` | `msg["image"]["id"]` | CMR photos, ADR certificates |
| `document` | `msg["document"]["id"]` | PDF invoices, CMR PDFs |
| `location` | `msg["location"]` | Eco-zone location check |
| `interactive` | `msg["interactive"]` | Button replies (OK / Recusar) |
| `audio` | `msg["audio"]["id"]` | Ignored in current pipeline |
| `video` | `msg["video"]["id"]` | Ignored in current pipeline |
| `sticker` | — | Ignored |
| `reaction` | — | Ignored |

## Intent Mapping (from intent_classifier.py)

```python
# Message type drives initial routing
if message_type in ("image", "document"):
    return "cmr_scan"           # → Gemini vision extraction
elif message_type == "location":
    return "location_check"     # → eco_zone_handler
elif message_type == "interactive":
    return "confirm"            # → button reply handler
elif message_type == "text":
    return classify_text(body)  # → keyword matching
```

## Text Intent Keywords

| Intent | Triggers |
|--------|---------|
| `checklist` | "checklist", "inspecao", "inspection", "dvir", ... |
| `eco_zone` | "lez", "ztl", "ecozone", "zona", "restricao", ... |
| `pin_liberacao` | "pin", "liberar", "release", "liberacao", ... |
| `pin_confirm` | NATO-NNNN pattern: `ALFA-1234`, `BRAVO-4817` |
| `adr_register` | "adr", "perigoso", "dangerous", "hazmat", ... |
| `general` | Anything else → LLM Q&A |

## Interactive Message (Button Reply)

Sent by `wa_gateway` with "OK" and "Recusar" buttons. Incoming reply:

```json
{
  "type": "interactive",
  "interactive": {
    "type": "button_reply",
    "button_reply": {"id": "ok", "title": "OK"}
  }
}
```

The `button_reply.id` is the intent signal — `"ok"` = confirm, `"recusar"` = reject.

## Media Message Flow

```
1. Webhook arrives with media_id (NOT the actual bytes)
2. GET /{media_id} → temporary download URL (valid ~5 min)
3. GET {download_url} → raw bytes
4. Pass bytes to Gemini vision extraction
```

Important: media download URL expires. Download immediately in the handler, not later.

## Location Message

```json
{
  "type": "location",
  "location": {
    "latitude": 52.3676,
    "longitude": 4.9041,
    "name": "Amsterdam",
    "address": "Amsterdam, Netherlands"
  }
}
```

Used by `eco_zone_handler` to query city emission zone restrictions.

## WhatsAppWebhookMessage Schema

Flat Pydantic model after parsing (from `shared/schemas/cmr.py`):

```python
class WhatsAppWebhookMessage(BaseModel):
    message_id: str           # wamid.xxx — idempotency key
    from_number: str          # E.164 format: +5511999999999
    sender_name: str | None   # from contacts[].profile.name
    message_type: str         # text | image | document | location | interactive
    timestamp: datetime
    text_body: str | None
    media_id: str | None      # for image/document
    media_mime_type: str | None
    location: WhatsAppLocationMessage | None
    button_reply_id: str | None  # for interactive button replies
    tenant_id: str
```
