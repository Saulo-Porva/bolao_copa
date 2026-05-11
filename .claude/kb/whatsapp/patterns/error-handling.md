# Pattern: Error Handling in WhatsApp Pipelines

## Principle

Never let a backend error surface as silence to the driver. Every error path must:
1. Log structured details for debugging
2. Send a user-friendly message in the driver's language
3. Route to DLQ if data may be recoverable
4. Preserve the raw message for reprocessing

## Error Categories

| Category | Example | Recovery |
|----------|---------|---------|
| Transient (network/timeout) | Gemini timeout, BigQuery unavailable | Pub/Sub retry via DLQ |
| Permanent (bad input) | Blank image, wrong document type | Inform user, no retry |
| Auth (token expired) | Meta 190 error | Alert ops, refresh token |
| Rate limit | Meta 131030 | Exponential backoff + DLQ |

## Transient Error Pattern

```python
# Don't fail the webhook — push to DLQ for retry
try:
    result = await process_message(message)
except (TimeoutError, httpx.TimeoutException, google.api_core.exceptions.ServiceUnavailable):
    logger.warning(
        "transient_error_dlq",
        extra={"message_id": message.message_id, "error": str(e)},
    )
    publish_to_dlq(message)
    # Do NOT send "error" message to user — they'll get it on successful retry
    return
```

## User-Facing Error Messages

Keep messages short, actionable, in the driver's language. Never expose stack traces.

```python
ERROR_MESSAGES = {
    "media_unreadable": {
        "pt": "Não consegui ler o documento. Tente uma foto mais nítida, com boa iluminação.",
        "en": "Could not read the document. Try a clearer photo with good lighting.",
        "nl": "Kon het document niet lezen. Maak een duidelijkere foto.",
        "de": "Konnte das Dokument nicht lesen. Bitte machen Sie ein deutlicheres Foto.",
    },
    "processing_error": {
        "pt": "Erro temporário. Seu documento foi salvo e será reprocessado em breve.",
        "en": "Temporary error. Your document was saved and will be reprocessed shortly.",
    },
    "invalid_pin": {
        "pt": "PIN inválido. Verifique o código com a transportadora.",
        "en": "Invalid PIN. Please verify the code with your carrier.",
    },
}

def get_error_message(key: str, lang: str = "pt") -> str:
    return ERROR_MESSAGES.get(key, {}).get(lang, ERROR_MESSAGES[key]["pt"])
```

## DLQ Processor

```python
# functions/dlq_processor/main.py
@functions_framework.cloud_event
def dlq_processor(event: CloudEvent) -> None:
    message = decode_pubsub_message(event)
    retry_count = message.get("_retry_count", 0)

    if retry_count >= MAX_RETRIES:
        logger.error("message_exhausted", extra={"message_id": message["message_id"]})
        write_to_dead_letter_table(message)  # BigQuery dead letter table
        return

    message["_retry_count"] = retry_count + 1
    # Re-publish to main topic with backoff
    time.sleep(2 ** retry_count)
    publish_to_routing_topic(message)
```

## Idempotency in Error Recovery

```python
# Always check before reprocessing from DLQ
def safe_process(message: dict, db: firestore.Client) -> None:
    msg_id = message["message_id"]

    # Check if already successfully processed since DLQ enqueue
    doc = db.collection("processed_messages").document(msg_id).get()
    if doc.exists and doc.get("status") == "success":
        logger.info("already_processed_skipping", extra={"message_id": msg_id})
        return

    process(message)
    db.collection("processed_messages").document(msg_id).set({
        "status": "success",
        "processed_at": datetime.now(UTC).isoformat(),
    })
```

## Monitoring Checklist

| Alert | Threshold | Action |
|-------|-----------|--------|
| DLQ depth > 10 | 10 messages | Investigate handler errors |
| Extraction confidence < 0.7 avg | 24h window | Review prompt or image quality |
| Meta 190 errors | Any | Refresh access token immediately |
| Webhook 20s timeout | Any | Check Cloud Run cold start |
| LangFuse cost spike | > 2x baseline | Check runaway extraction loop |
