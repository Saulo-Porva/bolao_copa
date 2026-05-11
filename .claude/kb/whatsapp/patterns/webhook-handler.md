# Pattern: Webhook Handler

## Problem

The Meta webhook delivers deeply-nested JSON at high frequency. The handler must:
1. Verify authenticity (HMAC) before touching the payload
2. Respond with 200 in < 20s (Meta drops and retries otherwise)
3. Handle duplicates idempotently
4. Decode the payload to a flat, typed model

## Pattern

```python
# functions/wa_gateway/webhook.py
import functions_framework
from flask import Request, Response

@functions_framework.http
def wa_gateway(request: Request) -> Response:
    # 1. Signature verification — reject before any parsing
    payload = request.get_data()
    if not validate_signature(payload, request.headers.get("X-Hub-Signature-256"), APP_SECRET):
        return Response("Unauthorized", 401)

    # 2. GET = webhook verification challenge
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return Response(request.args.get("hub.challenge", ""), 200)
        return Response("Forbidden", 403)

    # 3. Parse to flat model
    body = request.get_json(force=True, silent=True) or {}
    message = parse_webhook_payload(body, tenant_id="default")
    if message is None:
        return Response("OK", 200)  # Status update — discard

    # 4. Idempotency check
    if is_duplicate(message.message_id, db):
        return Response("OK", 200)

    # 5. Route to Pub/Sub (async) — never block on handler logic
    publish_to_pubsub(topic=ROUTING_TOPIC, message=message.model_dump())

    return Response("OK", 200)
```

## Payload Parsing

```python
# From webhook.py — flatten Meta's nested envelope
def parse_webhook_payload(body: dict, tenant_id: str) -> WhatsAppWebhookMessage | None:
    try:
        value = body["entry"][0]["changes"][0]["value"]
        messages = value.get("messages", [])
        if not messages:
            return None  # status callback

        msg = messages[0]
        contacts = value.get("contacts", [])

        return WhatsAppWebhookMessage(
            message_id=msg["id"],
            from_number=normalize_phone(msg["from"]),
            sender_name=contacts[0].get("profile", {}).get("name") if contacts else None,
            message_type=msg["type"],
            timestamp=datetime.fromtimestamp(int(msg["timestamp"]), tz=UTC),
            text_body=msg.get("text", {}).get("body"),
            media_id=msg.get("image", msg.get("document", {})).get("id"),
            media_mime_type=msg.get("image", msg.get("document", {})).get("mime_type"),
            location=parse_location(msg.get("location")),
            button_reply_id=msg.get("interactive", {}).get("button_reply", {}).get("id"),
            tenant_id=tenant_id,
        )
    except (KeyError, IndexError, TypeError):
        logger.warning("webhook_parse_error", extra={"body": str(body)[:200]})
        return None
```

## Key Invariants

- **Always verify HMAC first** — before `request.get_json()`
- **Always return 200** for valid, processed messages (even if routing fails)
- **Return 200 immediately** — async via Pub/Sub, never block on processing
- **Log parse failures** — don't silently swallow malformed payloads

## Testing

```python
def test_webhook_valid_image_message(client, app_secret):
    payload = json.dumps(SAMPLE_IMAGE_WEBHOOK).encode()
    sig = "sha256=" + hmac.new(app_secret.encode(), payload, "sha256").hexdigest()
    resp = client.post("/", data=payload, headers={"X-Hub-Signature-256": sig})
    assert resp.status_code == 200

def test_webhook_invalid_signature_rejected(client):
    resp = client.post("/", data=b"{}", headers={"X-Hub-Signature-256": "sha256=bad"})
    assert resp.status_code == 401
```
