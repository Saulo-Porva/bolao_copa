# GCP Safety Quick Reference

> Blocked vs safe commands at a glance. For rationale, see linked concept/pattern files.
> **MCP Validated**: 2026-05-08

## Hook: Blocked vs Safe

| Intent | BLOCKED (hook stops this) | SAFE alternative |
|--------|---------------------------|-----------------|
| Remove Cloud Run service | `gcloud run services delete SVC` | Deploy revision with `--no-traffic`, then redirect |
| Delete GCS objects | `gcloud storage rm --recursive gs://...` | Move to archive bucket first, then schedule lifecycle rule |
| Drop Firestore database | `gcloud firestore databases delete` | Export to GCS, then delete |
| Delete Firestore documents | `gcloud firestore documents delete` | Mark as `archived: true` via transaction |
| Drop Pub/Sub topic | `gcloud pubsub topics delete TOPIC` | Drain DLQ, detach subscriptions, then delete |
| Drop Pub/Sub subscription | `gcloud pubsub subscriptions delete SUB` | Pause push, drain messages, then delete |
| Drop BigQuery table | `bq rm -t PROJECT:DS.TABLE` | Snapshot to archive dataset first |
| Drop BigQuery dataset | `bq rm -r -d PROJECT:DS` | Verify all tables snapshotted, get explicit approval |
| SQL drop | `DROP TABLE / DROP DATASET / DROP SCHEMA` | `ALTER TABLE ... RENAME`, or snapshot + recreate |
| Destroy infra | `terraform destroy` / `terragrunt destroy` | `terraform plan -destroy` first, manual approval |
| Revoke IAM binding | `gcloud projects remove-iam-policy-binding` | Review `get-iam-policy` output, add replacement first |
| Cancel build | `gcloud builds cancel BUILD_ID` | Only if build is confirmed broken; check logs first |
| Delete artifact | `gcloud artifacts delete ...` | Tag as deprecated, retain for 30 days |
| Force delete files | `rm -rf /path` (non-tmp) | Move to trash or archive; never auto-delete prod data |

## Prod Project Guard

| Trigger | Hook reaction |
|---------|---------------|
| `--project=hub-whatsapp-prod` in any command | Blocked — explicit user confirmation required |
| `--project=*-prod*` pattern | Blocked — applies to any prod-pattern project ID |
| No `--project` flag (uses gcloud default) | Allowed — but set default to dev intentionally |

## Safe Read-Only Commands (Always Allowed)

```bash
gcloud run services describe SERVICE --project=hub-whatsapp-dev
gcloud run services list --project=hub-whatsapp-dev
gcloud storage ls gs://bucket/
bq show --schema PROJECT:DATASET.TABLE
gcloud projects get-iam-policy PROJECT_ID
gcloud pubsub topics list
gcloud firestore databases list
terraform plan   # read-only
```

## Dev-First Deployment Order

```text
1. gcloud builds submit --project=hub-whatsapp-dev
2. Verify: gcloud run services describe --project=hub-whatsapp-dev
3. Run smoke test against dev
4. Get explicit approval for prod
5. gcloud builds submit --project=hub-whatsapp-prod  (requires confirmation)
```

## Related Files

| Topic | Path |
|-------|------|
| Why each op is dangerous | `concepts/gcp-destructive-operations.md` |
| Safe implementation patterns | `patterns/safe-gcp-operations.md` |
| Pre-prod checklist | `patterns/prod-deployment-checklist.md` |
| Full index | `index.md` |
