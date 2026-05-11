# Prod Deployment Checklist

> **Purpose**: Pre-flight checklist before any operation against `hub-whatsapp-prod`
> **Confidence**: 0.95
> **MCP Validated**: 2026-05-08

## When to Use

Run this checklist before any command that targets `hub-whatsapp-prod`. The hook will block
the command and prompt for confirmation — use that pause to complete these checks.

---

## 1. Pre-Deployment Verification (Dev Must Pass First)

```bash
# Confirm dev deployment is healthy
gcloud run services describe wa-gateway \
  --project=hub-whatsapp-dev \
  --region=us-central1 \
  --format="value(status.conditions[0].status)"
# Expected: True

# Confirm smoke test passes in dev
# (run your project's smoke test suite here)

# Confirm no open incidents in Cloud Logging
gcloud logging read \
  'severity>=ERROR AND resource.type="cloud_run_revision"' \
  --project=hub-whatsapp-dev \
  --limit=10 \
  --freshness=1h
```

- [ ] Dev service shows `Ready: True`
- [ ] Smoke test passes in dev
- [ ] No ERROR-level logs in dev in the last hour

---

## 2. Image and Artifact Verification

```bash
# Confirm the image tag you are deploying exists in Artifact Registry
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/hub-whatsapp-dev/wa-gateway \
  --filter="tags:v1.2.3" \
  --format="value(version)"

# Confirm the image digest matches what was built in CI
gcloud builds list \
  --project=hub-whatsapp-dev \
  --filter="status=SUCCESS" \
  --limit=1 \
  --format="value(results.images[0].digest)"
```

- [ ] Image tag exists in Artifact Registry
- [ ] CI build SHA matches the image you are promoting
- [ ] No `FAILURE` or `TIMEOUT` in the last CI build

---

## 3. Schema and Config Compatibility

- [ ] No breaking schema changes in this deployment (added columns only, never removed)
- [ ] All environment variables / secrets referenced in the new revision exist in prod Secret Manager
- [ ] Pub/Sub topic/subscription names match — no renames without migration

```bash
# Verify secrets exist in prod
gcloud secrets list --project=hub-whatsapp-prod --filter="name~wa-gateway"
```

---

## 4. Rollback Plan Confirmed

Before deploying, know exactly how to roll back:

| What changed | Rollback command |
|--------------|-----------------|
| Cloud Run revision | `gcloud run services update-traffic ... --to-revisions=PREV=100` |
| BigQuery schema | `bq cp backup_table original_table` (snapshot must exist) |
| Pub/Sub subscription config | Re-apply previous subscription Terraform config |
| IAM binding | Re-add removed binding via `add-iam-policy-binding` |

- [ ] Rollback command written down and ready to paste
- [ ] Previous Cloud Run revision name noted: _______________
- [ ] BigQuery snapshot exists (if schema changed): _______________

---

## 5. Timing and Communication

- [ ] Deployment window is off-peak (avoid business hours if possible)
- [ ] Team is aware that a prod deploy is happening
- [ ] Monitoring dashboard open during deployment (Cloud Console > Cloud Run > wa-gateway)

---

## 6. Deployment Execution

```bash
# Step 1: Deploy to prod WITHOUT traffic
gcloud run deploy wa-gateway \
  --image us-central1-docker.pkg.dev/hub-whatsapp-dev/wa-gateway:v1.2.3 \
  --no-traffic \
  --project=hub-whatsapp-prod \
  --region=us-central1

# Step 2: Verify new revision started successfully
gcloud run revisions list \
  --service=wa-gateway \
  --project=hub-whatsapp-prod \
  --region=us-central1 \
  --limit=3

# Step 3: Canary — send 10% traffic
gcloud run services update-traffic wa-gateway \
  --to-revisions=REVISION_NAME=10 \
  --project=hub-whatsapp-prod \
  --region=us-central1

# Step 4: Watch error rate for 5 minutes, then go to 100%
gcloud run services update-traffic wa-gateway \
  --to-revisions=REVISION_NAME=100 \
  --project=hub-whatsapp-prod \
  --region=us-central1
```

- [ ] Deployed with `--no-traffic` first
- [ ] Canary at 10% shows no new errors
- [ ] Full cutover complete
- [ ] Post-deploy smoke test passed

---

## 7. Post-Deployment Verification

```bash
# Check revision is serving traffic
gcloud run services describe wa-gateway \
  --project=hub-whatsapp-prod \
  --region=us-central1 \
  --format="value(status.traffic)"

# Check error rate in last 5 minutes
gcloud logging read \
  'severity>=ERROR AND resource.type="cloud_run_revision"' \
  --project=hub-whatsapp-prod \
  --limit=10 \
  --freshness=5m
```

- [ ] Revision is listed with 100% traffic
- [ ] Error rate is at baseline (no spike)
- [ ] WhatsApp webhook responded correctly to a test message

---

## Abort Criteria

Stop and roll back immediately if:

| Signal | Action |
|--------|--------|
| New revision fails to start (`FAILED` status) | Keep old revision at 100%, investigate logs |
| Error rate doubles from baseline | Roll back traffic to previous revision |
| Any 5xx from the webhook endpoint | Roll back, check Secret Manager access |
| DLQ message count rising | Roll back, drain DLQ before retry |

---

## Related

- [Safe GCP Operations](safe-gcp-operations.md)
- [Destructive Operations Explained](../concepts/gcp-destructive-operations.md)
- [Quick Reference](../quick-reference.md)
