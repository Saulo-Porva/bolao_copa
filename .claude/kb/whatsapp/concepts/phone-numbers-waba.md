# Phone Numbers & WABA

## Hierarchy

```
Business Manager
└── WhatsApp Business Account (WABA)
    └── Phone Number
        ├── phone_number_id  (used in API calls)
        ├── display number   (shown to users)
        └── verified name    (shown in chat header)
```

## This Project

| Field | Value |
|-------|-------|
| Phone Number ID | `988336007706186` |
| WABA ID | in Secret Manager |
| Display number | Configured in Meta Business Manager |

## E.164 Format

All phone numbers in the project use E.164 format: `+{country_code}{number}`

```python
# Normalization (from webhook.py)
from_number_raw = msg.get("from", "")
from_number = f"+{from_number_raw}" if not from_number_raw.startswith("+") else from_number_raw
# Meta sends without "+" → we normalize to E.164
```

## Multi-Tenant Architecture

The `tenant_id` field in `WhatsAppWebhookMessage` enables multi-carrier/multi-customer deployment. Each tenant can have:
- Separate WABA
- Separate phone number
- Isolated Firestore namespace

Current: single-tenant pilot (`tenant_id = "default"` or derived from phone number routing).

## Phone Number Verification

To send business-initiated messages, the number must have:
1. Display name approved by Meta
2. Business verification complete
3. Two-factor authentication enabled

## Optin Requirement

Users must opt in before receiving business-initiated messages. For inbound flows (user messages first), no explicit optin is needed.
