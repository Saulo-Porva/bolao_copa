# Safe GCP Operations

> **Purpose**: Safe patterns for Cloud Run, GCS, Firestore, Pub/Sub, and BigQuery operations
> **Confidence**: 0.95
> **MCP Validated**: 2026-05-08

## Cloud Run — Safe Deployment

Never delete a service to replace it. Use traffic splitting for zero-downtime updates.

```bash
# Deploy new revision WITHOUT sending traffic
gcloud run deploy wa-gateway \
  --image gcr.io/hub-whatsapp-dev/wa-gateway:v2 \
  --no-traffic \
  --project=hub-whatsapp-dev \
  --region=us-central1

# Verify new revision is healthy
gcloud run revisions describe wa-gateway-00002 \
  --project=hub-whatsapp-dev \
  --region=us-central1

# Gradually shift traffic
gcloud run services update-traffic wa-gateway \
  --to-revisions=wa-gateway-00002=10 \
  --project=hub-whatsapp-dev

# Full cutover only after confirming no errors
gcloud run services update-traffic wa-gateway \
  --to-revisions=wa-gateway-00002=100 \
  --project=hub-whatsapp-dev
```

**Rollback:** Point traffic back to the previous revision — no rebuild required.

```bash
gcloud run services update-traffic wa-gateway \
  --to-revisions=wa-gateway-00001=100 \
  --project=hub-whatsapp-dev
```

---

## GCS — Safe Object Management

Enable versioning on buckets that hold pipeline data. Never use `rm --recursive` directly.

```bash
# Enable versioning (one-time setup)
gcloud storage buckets update gs://hub-whatsapp-dev-invoices \
  --versioning

# Move objects to archive prefix instead of deleting
gcloud storage mv \
  gs://hub-whatsapp-dev-invoices/raw/2026-01/* \
  gs://hub-whatsapp-dev-invoices/archive/2026-01/

# Set lifecycle rule to auto-delete archive after 90 days
gcloud storage buckets update gs://hub-whatsapp-dev-invoices \
  --lifecycle-file=lifecycle.json
```

**lifecycle.json example:**
```json
{
  "rule": [{
    "action": {"type": "Delete"},
    "condition": {
      "age": 90,
      "matchesPrefix": ["archive/"]
    }
  }]
}
```

---

## Firestore — Safe Document Operations

Always use transactions for multi-document writes. Never delete documents directly — archive them.

```python
from google.cloud import firestore

db = firestore.Client()

@firestore.transactional
def archive_session(transaction: firestore.Transaction, session_ref: firestore.DocumentReference) -> None:
    """Archive a session document instead of deleting it."""
    doc = session_ref.get(transaction=transaction)
    if not doc.exists:
        return
    data = doc.to_dict()
    data["archived"] = True
    data["archived_at"] = firestore.SERVER_TIMESTAMP
    transaction.update(session_ref, data)

# Safe bulk soft-delete: filter archived=False before processing
sessions = db.collection("sessions").where("archived", "==", False).stream()
```

**Never use `gcloud firestore documents delete` on prod. Use `archived: true` flag instead.**

---

## Pub/Sub — Safe Topic/Subscription Changes

Drain before removing. Always confirm DLQ is empty.

```bash
# Check undelivered message count before any subscription change
gcloud pubsub subscriptions describe SUBSCRIPTION \
  --project=hub-whatsapp-dev \
  --format="value(messageRetentionDuration,deadLetterPolicy)"

# Drain DLQ: pull all messages and ack them (or process them)
gcloud pubsub subscriptions pull DLQ_SUBSCRIPTION \
  --project=hub-whatsapp-dev \
  --limit=1000 \
  --auto-ack

# Only after DLQ is empty: detach subscriber, then delete topic
gcloud pubsub subscriptions modify-push-config SUBSCRIPTION \
  --push-endpoint="" \
  --project=hub-whatsapp-dev
```

**New topics always require a DLQ subscription:**
```bash
gcloud pubsub topics create new-topic --project=hub-whatsapp-dev

gcloud pubsub subscriptions create new-topic-dlq \
  --topic=new-topic \
  --project=hub-whatsapp-dev

gcloud pubsub subscriptions create new-topic-sub \
  --topic=new-topic \
  --dead-letter-topic=new-topic-dlq \
  --max-delivery-attempts=5 \
  --project=hub-whatsapp-dev
```

---

## BigQuery — Safe Schema Changes

Inspect before modifying. Never drop; snapshot first.

```bash
# Inspect current schema
bq show --schema --format=prettyjson hub-whatsapp-dev:invoices.extracted_data

# Snapshot table before schema migration
bq cp \
  hub-whatsapp-dev:invoices.extracted_data \
  hub-whatsapp-dev:invoices.extracted_data_backup_20260508

# Add a column (safe — backwards compatible)
bq update --schema new_schema.json hub-whatsapp-dev:invoices.extracted_data

# Rename a column (safe pattern: add alias, migrate, drop old)
# Step 1: Add new column
# Step 2: Backfill with SELECT old_col AS new_col
# Step 3: Update producers to write new_col
# Step 4: After full backfill, mark old_col as deprecated in schema description
```

**Never run `DROP TABLE` on prod. Use `bq cp` snapshot + `bq rm` only on the backup after validation.**

---

## IAM — Safe Binding Changes

Always add the replacement binding before removing the old one.

```bash
# View current bindings before any change
gcloud projects get-iam-policy hub-whatsapp-dev \
  --format=json > iam-policy-backup.json

# Add new binding first
gcloud projects add-iam-policy-binding hub-whatsapp-dev \
  --member="serviceAccount:new-sa@hub-whatsapp-dev.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Verify the function works with new SA
gcloud run services update wa-gateway \
  --service-account=new-sa@hub-whatsapp-dev.iam.gserviceaccount.com \
  --project=hub-whatsapp-dev

# Only after confirming: remove old binding
# (requires explicit user confirmation — hook blocks this)
```

---

## Secret Manager — Safe Access

```python
from google.cloud import secretmanager

def get_secret(project_id: str, secret_id: str) -> str:
    """Fetch secret value from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")

# Rotate: add new version, update references, then disable old version
# Never delete the only active version of a secret
```

---

## Related

- [Destructive Operations Explained](../concepts/gcp-destructive-operations.md)
- [Prod Deployment Checklist](prod-deployment-checklist.md)
- [Quick Reference](../quick-reference.md)
