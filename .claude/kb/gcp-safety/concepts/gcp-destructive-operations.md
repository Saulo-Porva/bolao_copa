# GCP Destructive Operations

> **Purpose**: What each hook-blocked command does and why it is dangerous
> **Confidence**: 0.95
> **MCP Validated**: 2026-05-08

## Overview

The hook `pre-bash-cloud-safety.js` blocks commands that have no undo path or that risk
cascading data loss. This file explains the specific risk for each blocked category.

---

## Cloud Run: `services delete`

**What it does:** Permanently removes a Cloud Run service and all its revisions.

**Risk:** Drops the live HTTPS endpoint. Any webhook subscription (e.g., WhatsApp, Eventarc) pointing to it starts receiving 404s immediately. There is no undelete — the service name becomes available to other projects.

**Hook pattern:** `gcloud run services delete`

---

## GCS: `rm --recursive`

**What it does:** Deletes every object matching the prefix, including subdirectories.

**Risk:** GCS objects are immediately unrecoverable once deleted (unless versioning is enabled on the bucket). A single typo in the prefix can wipe an entire pipeline stage's data.

**Hook pattern:** `gcloud storage rm --recursive`

---

## Firestore: `databases delete` / `bulk-delete` / `documents delete`

**What they do:**
- `databases delete` — drops the entire Firestore database and all collections.
- `bulk-delete` — deletes all documents matching a collection group filter.
- `documents delete` — deletes a specific document path.

**Risk:** Firestore has no recycle bin. Session state, conversation history, and configuration records are lost instantly. `databases delete` requires the database to be empty first, but `bulk-delete` does not.

**Hook patterns:** `gcloud firestore databases delete`, `gcloud firestore bulk-delete`, `gcloud firestore documents delete`

---

## Pub/Sub: `topics delete` / `subscriptions delete`

**What they do:**
- `topics delete` — removes the topic; all subscriptions lose their source and stop receiving messages.
- `subscriptions delete` — removes a subscription; all unacknowledged messages in that subscription are permanently lost.

**Risk:** Messages in-flight (not yet acked) vanish. DLQ messages that represent failed pipeline records are also lost. Downstream Cloud Run functions stop processing immediately.

**Hook patterns:** `gcloud pubsub topics delete`, `gcloud pubsub subscriptions delete`

---

## BigQuery: `bq rm` / `DROP TABLE` / `DROP DATASET` / `DROP SCHEMA`

**What they do:** Remove tables, datasets, or schemas from BigQuery.

**Risk:** BigQuery table deletion has a 7-day recovery window only for standard tables in the same project (using `bq cp` with `--restore`). After 7 days, or if the table was in a dataset that was dropped, data is unrecoverable. `DROP DATASET` cascades to all tables.

**Hook patterns:** `bq rm`, `DROP TABLE`, `DROP DATASET`, `DROP SCHEMA`

---

## IaC: `terraform destroy` / `terragrunt destroy`

**What they do:** Destroy all resources managed by the Terraform state file — buckets, Cloud Run services, Pub/Sub topics, IAM bindings, and everything else in the plan.

**Risk:** Destroys the entire environment in a single command. Even a `--target` destroy can cascade via dependencies. There is no rollback; re-apply will create new resources but cannot restore data (e.g., GCS objects, Firestore documents, BigQuery rows).

**Hook patterns:** `terraform destroy`, `terragrunt destroy`

---

## IAM: `remove-iam-policy-binding`

**What it does:** Removes a specific role binding from a principal on a project or resource.

**Risk:** Removing the wrong binding can lock a Cloud Run service account out of GCS, BigQuery, or Pub/Sub — causing silent failures or full pipeline outages. IAM changes propagate in seconds and have no undo command (you must re-add the binding manually).

**Hook pattern:** `gcloud projects remove-iam-policy-binding`

---

## Build / Artifacts: `builds cancel` / `artifacts delete`

**What they do:**
- `builds cancel` — stops an in-progress Cloud Build; partially built images may be inconsistent.
- `artifacts delete` — removes a container image version from Artifact Registry.

**Risk:** Cancelling a build mid-push can leave a corrupt or partially pushed image. Deleting an artifact version removes the only rollback target if the current prod image is bad.

**Hook patterns:** `gcloud builds cancel`, `gcloud artifacts delete`

---

## Filesystem: `rm -rf` (non-tmp paths)

**What it does:** Recursively force-deletes a directory tree without confirmation.

**Risk:** On the agent's working filesystem, this can delete source code, config files, or local credentials. The hook allows `rm -rf /tmp/...` but blocks all other paths.

**Hook pattern:** `rm -rf` where path does not start with `/tmp`

---

## Any Command Targeting `*-prod*`

**What it does:** Runs any gcloud/bq/terraform command against a production project.

**Risk:** Even read-only commands like `gcloud run deploy` can overwrite a live service. The blanket prod guard ensures every prod operation is a deliberate, confirmed action.

**Hook pattern:** `--project=*-prod*` anywhere in the command string

---

## Related

- [Safe GCP Operations](../patterns/safe-gcp-operations.md)
- [Prod Deployment Checklist](../patterns/prod-deployment-checklist.md)
- [Quick Reference](../quick-reference.md)
