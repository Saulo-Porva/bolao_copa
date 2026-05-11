# GCP Safety — Hook-Enforced Operations

> **Purpose**: Reference for GCP destructive-operation safeguards enforced by `pre-bash-cloud-safety.js`
> **MCP Validated**: 2026-05-08

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/gcp-destructive-operations.md](concepts/gcp-destructive-operations.md) | What each blocked command does and why it is dangerous |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/safe-gcp-operations.md](patterns/safe-gcp-operations.md) | Safe alternatives for Cloud Run, GCS, Firestore, Pub/Sub, BigQuery |
| [patterns/prod-deployment-checklist.md](patterns/prod-deployment-checklist.md) | Pre-flight checklist before any prod operation |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — blocked vs safe commands side by side

---

## Hook Reference

The hook `pre-bash-cloud-safety.js` intercepts Bash tool calls before execution.

| Hook behavior | Effect |
|---------------|--------|
| Matches a blocked pattern | Execution stopped, user must confirm |
| Command targets `*-prod*` project | Execution stopped, user must confirm |
| No match | Command runs normally |

Hook location: `.claude/hooks/pre-bash-cloud-safety.js`

---

## Project Environments

| Environment | Project ID | Policy |
|-------------|------------|--------|
| dev | `hub-whatsapp-dev` | Safe to experiment |
| prod | `hub-whatsapp-prod` | Hook blocks all destructive ops |

---

## Blocked Operation Categories

| Category | Commands | Risk |
|----------|----------|------|
| Cloud Run | `services delete` | Drops live endpoint with no recovery |
| GCS | `rm --recursive` | Irreversible object deletion |
| Firestore | `databases delete`, `bulk-delete`, `documents delete` | Full database or document loss |
| Pub/Sub | `topics delete`, `subscriptions delete` | Drops message queue + in-flight messages |
| BigQuery | `bq rm`, `DROP TABLE/DATASET/SCHEMA` | Permanent data loss |
| IaC | `terraform destroy`, `terragrunt destroy` | Tears down all managed infrastructure |
| IAM | `remove-iam-policy-binding` | Locks out service accounts |
| Build | `builds cancel`, `artifacts delete` | Cancels active pipelines |
| Filesystem | `rm -rf` on non-tmp paths | Unrecoverable local deletion |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| infra-deployer | patterns/safe-gcp-operations.md | Safe deployment procedures |
| build-agent | patterns/prod-deployment-checklist.md | Pre-ship prod verification |
| kb-architect | concepts/gcp-destructive-operations.md | Reasoning about risk categories |
