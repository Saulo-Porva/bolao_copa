# WhatsApp Webhooks

## Overview

Meta delivers all incoming events (messages, status updates, read receipts) via HTTP POST to a registered webhook URL. The `wa_gateway` Cloud Run function is this endpoint.

## Registration

```bash
# Register webhook subscription (done once per app)
curl -X POST "https://graph.facebook.com/v21.0/{APP_ID}/subscriptions" \
  -d "object=whatsapp_business_account" \
  -d "callback_url=https://wa-gateway-xxx.run.app/" \
  -d "verify_token=hub_cmr_verify_2026_piloto" \
  -d "fields=messages" \
  -d "access_token={APP_TOKEN}"
```

## Verification Challenge (GET)

When registering or re-registering, Meta sends a GET to verify ownership:

```
GET /?hub.mode=subscribe&hub.challenge=NONCE&hub.verify_token=YOUR_TOKEN
```

Handler must return the `hub.challenge` value as plain text with HTTP 200.

```python
@app.route("/", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge", ""), 200
    return "Forbidden", 403
```

## HMAC-SHA256 Signature Verification

Every POST carries an `X-Hub-Signature-256` header. **Must verify before processing.**

```python
# From shared/adapters/whatsapp.py
def verify_webhook_signature(payload: bytes, signature_header: str | None, app_secret: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature_header)
```

Critical: use `hmac.compare_digest` to prevent timing attacks.

## Payload Structure

Meta wraps every event in a consistent envelope:

```
body.entry[0].changes[0].value
├── messages[]          ← incoming messages (what we process)
├── statuses[]          ← delivery/read receipts (discard or log)
├── contacts[]          ← sender profile info (name)
└── metadata            ← phone_number_id, display_phone_number
```

## What to Discard

Status callbacks (delivery receipts, read receipts) come through the same endpoint. Detect and skip them:

```python
value = body["entry"][0]["changes"][0]["value"]
if not value.get("messages"):
    return None  # status update — skip
```

## Delivery Guarantees

- Meta delivers webhooks **at least once** — idempotency is your responsibility
- Message ID (`wamid.xxx`) is the idempotency key
- Check `message_id` against Firestore before processing
- Meta retries failed webhooks (non-200) up to 20 times over 72 hours

## Idempotency Pattern (Firestore)

```python
# In state_manager.py
def is_duplicate(message_id: str, db: firestore.Client) -> bool:
    ref = db.collection("processed_messages").document(message_id)
    doc = ref.get()
    if doc.exists:
        return True
    ref.set({"processed_at": datetime.now(UTC).isoformat()})
    return False
```

## Response Requirements

- Must return HTTP 200 within **20 seconds** or Meta marks as failed
- Return 200 immediately, process asynchronously via Pub/Sub
- Never block the webhook response on LLM calls or BigQuery writes
