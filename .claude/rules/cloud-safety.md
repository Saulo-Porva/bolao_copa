# Cloud Safety Rules — Multi-Cloud

Rules for safe cloud operations across GCP, AWS, and Azure.
The `pre-bash-cloud-safety.js` hook enforces the most critical ones automatically.

---

## Project Naming Convention

| Environment | Pattern | Purpose |
|-------------|---------|---------|
| dev | `{project-name}-dev` | Development — safe to experiment |
| staging | `{project-name}-stg` | Staging — test before prod |
| prod | `{project-name}-prod` | Production — never touch without explicit confirmation |

**Rule:** Any command targeting a `*-prod` environment requires explicit user confirmation. The hook blocks it automatically.

---

## What NEVER runs without explicit user confirmation

```bash
# ❌ GCP — blocked by pre-bash-cloud-safety.js
gcloud run services delete ...
gcloud storage rm --recursive ...
gcloud firestore databases delete ...
gcloud pubsub topics delete ...
bq rm -r ...
terraform destroy
terragrunt destroy
gcloud projects remove-iam-policy-binding ...

# ❌ AWS — blocked
aws s3 rb --force ...
aws s3 rm --recursive ...
aws ec2 terminate-instances ...
aws rds delete-db-instance ...
aws lambda delete-function ...
aws cloudformation delete-stack ...

# ❌ Azure — blocked
az group delete ...
az vm delete ...
az storage account delete ...
az aks delete ...
az keyvault delete ...
```

---

## Deployment Pattern (safe)

```bash
# 1. Always deploy to dev first
{deploy-command} --project={project}-dev

# 2. Verify before promoting
{describe-command} --project={project}-dev

# 3. Only then promote to prod (requires user confirmation)
{deploy-command} --project={project}-prod
```

---

## Secret Management

- **Never** log, print, or commit secret values
- Access via cloud secret manager only — never hardcode in env vars or code
- The `pre-bash-secrets.js` hook blocks commands that appear to pass secrets inline

```python
# ✓ Correct — via secret manager
secret = client.access_secret_version(name=f"{secret_id}/versions/latest")

# ✗ Wrong — hardcoded
API_KEY = "sk-..."
```

---

## Service Account Rules

- Each service/function gets its own service account with least-privilege roles
- Never bind `roles/editor` or `roles/owner` to a service account
- Validate role bindings before deploying

---

## Data Safety

| Risk | Mitigation |
|------|-----------|
| Bad LLM extraction overwrites good data | Append-only writes + audit timestamp column |
| Webhook flood crashes service | Max instance limit + rate limiting |
| State corruption | Transactions for multi-document writes |
| LLM cost spike | Cost alerts + per-request token budget |
