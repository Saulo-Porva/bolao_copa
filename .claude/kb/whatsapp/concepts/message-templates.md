# Message Templates (HSM)

## What They Are

Pre-approved message formats required for **business-initiated** conversations. Users who haven't messaged in 24h must receive a template message first.

## When Required

| Scenario | Template needed? |
|----------|-----------------|
| Driver messages bot first | No — session window open 24h |
| Bot messages driver after 24h silence | Yes |
| Proactive notification (CMR approved) | Yes |
| Responding within 24h session | No |

## Template Categories

| Category | Examples | Cost |
|----------|---------|------|
| Utility | Order confirmation, delivery status | Lower |
| Authentication | OTP codes | Lower |
| Marketing | Promotions, offers | Higher |

**This project uses:** Utility templates for cargo notifications.

## Template Structure

```json
{
  "name": "cmr_approval_notification",
  "language": {"code": "pt_BR"},
  "components": [
    {
      "type": "body",
      "parameters": [
        {"type": "text", "text": "{{1}}"},
        {"type": "text", "text": "{{2}}"}
      ]
    }
  ]
}
```

## Sending a Template

```python
def send_template(self, to: str, template_name: str, params: list[str]) -> str:
    return self._client.post(
        f"{GRAPH_API_BASE}/{self.phone_number_id}/messages",
        headers=self._headers(),
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "pt_BR"},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in params],
                }],
            },
        },
    ).json()["messages"][0]["id"]
```

## 24-Hour Session Window

```
User sends message → 24h window opens
  └── Bot can reply freely (any format)
  └── Window resets with each user message

After 24h silence → window closes
  └── Bot must use template to re-engage
```

## Current Project Status

Templates not yet registered — current flow is fully reactive (user always messages first, session always open). Template registration needed when proactive notifications are added (e.g., PIN expiry warnings, delivery status pushes).
