# Pattern: Intent-Based Message Routing

## Problem

A single WhatsApp number receives messages for multiple workflows (CMR scanning, vehicle inspection, eco-zone queries, PIN codes, ADR). Routing must be fast (< 1ms), deterministic, and testable without LLM calls.

## Pattern: Keyword + Type Classifier

```python
# intent_classifier.py — zero LLM, zero latency
def classify_intent(message: WhatsAppWebhookMessage) -> str:
    msg_type = message.message_type
    body = (message.text_body or "").strip().lower()

    # Type-driven routing (highest priority)
    if msg_type in ("image", "document"):
        return "cmr_scan"
    if msg_type == "location":
        return "location_check"
    if msg_type == "interactive":
        return "confirm"

    # Text-driven routing (keyword sets)
    if _PIN_PATTERN.match(body.upper()):
        return "pin_confirm"
    if any(kw in body for kw in _CHECKLIST_KEYWORDS):
        return "checklist"
    if any(kw in body for kw in _ECO_ZONE_KEYWORDS):
        return "eco_zone"
    if any(kw in body for kw in _PIN_KEYWORDS):
        return "pin_liberacao"
    if any(kw in body for kw in _ADR_KEYWORDS):
        return "adr_register"

    return "general"  # → LLM Q&A fallback
```

## Handler Dispatch Table

```python
HANDLERS: dict[str, Callable] = {
    "cmr_scan":      cmr_handler.handle,
    "checklist":     checklist_handler.handle,
    "eco_zone":      eco_zone_handler.handle,
    "location_check": eco_zone_handler.handle_location,
    "confirm":       confirm_handler.handle,
    "pin_liberacao": pin_handler.handle_liberacao,
    "pin_confirm":   pin_handler.handle_confirm,
    "adr_register":  adr_handler.handle,
    "general":       general_handler.handle,  # LLM
}

async def route(message: WhatsAppWebhookMessage) -> None:
    intent = classify_intent(message)
    logger.info("intent_classified", extra={"intent": intent, "type": message.message_type})
    handler = HANDLERS.get(intent, general_handler.handle)
    await handler(message)
```

## State-Aware Routing

For multi-turn conversations (e.g., PIN flow: request → confirm), the router checks Firestore session state first:

```python
def classify_with_state(message: WhatsAppWebhookMessage, session: dict | None) -> str:
    # Ongoing flow takes priority over fresh classification
    if session and session.get("flow") == "pin_liberacao":
        if session.get("awaiting") == "confirm":
            return "pin_confirm"

    return classify_intent(message)
```

## Adding a New Intent

1. Add keyword set to `intent_classifier.py`
2. Add pattern match in `classify_intent()`
3. Register handler in `HANDLERS` dict
4. Add to DEFINE doc: input trigger, expected output, error path
5. Test with at least 5 real message examples per language

## Multilingual Support

The keyword sets cover PT/EN/NL/DE/IT/FR for the Euro trucking corridor. When adding keywords, add translations for all 6 languages.

```python
_CHECKLIST_KEYWORDS = frozenset({
    "checklist",        # EN/PT universal
    "inspecao",         # PT
    "inspection",       # EN
    "inspectie",        # NL
    "ispezione",        # IT
    "fahrzeugprüfung",  # DE
})
```

## Data Flow to BigQuery

Every routed message generates an event row:

```python
# Routing event logged to BQ for analytics
{
    "message_id": "wamid.xxx",
    "from_number": "+5511999999999",
    "tenant_id": "default",
    "intent": "cmr_scan",
    "message_type": "image",
    "timestamp": "2026-04-23T10:00:00Z",
    "handler": "cmr_handler",
    "session_id": "sess_abc123",
}
```

This feeds the analytics dashboard showing intent distribution over time.
