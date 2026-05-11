# AWS Safety Knowledge Base

> **Purpose**: Reference for safe AWS operations — blocked commands, safe patterns, and IAM least-privilege
> **MCP Validated**: 2026-05-08

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/aws-destructive-operations.md](concepts/aws-destructive-operations.md) | What each blocked operation does and why it's dangerous |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/safe-s3-operations.md](patterns/safe-s3-operations.md) | S3 list, download, upload, sync without --delete |
| [patterns/safe-ec2-operations.md](patterns/safe-ec2-operations.md) | EC2 describe, start/stop vs terminate |
| [patterns/iam-least-privilege.md](patterns/iam-least-privilege.md) | Principle of least privilege for AWS IAM |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Blocked vs safe commands side by side

---

## Hook Enforcement

This project uses the `pre-bash-cloud-safety.js` hook to **automatically block** dangerous AWS commands before they execute.

| Hook File | Location | Effect |
|-----------|----------|--------|
| `pre-bash-cloud-safety.js` | `.claude/hooks/` | Intercepts Bash tool calls, aborts blocked patterns |

The hook blocks two categories:

1. **Destructive resource operations** — irreversible deletes and terminations
2. **Production profile commands** — any `--profile *prod*` or `--profile *production*`

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Blast radius** | How much damage a mistake can cause — minimize by scoping IAM tightly |
| **Immutability** | Prefer creating new resources over modifying or deleting existing ones |
| **Profile isolation** | Use named AWS profiles to separate dev/prod credentials |
| **Dry-run first** | Most destructive AWS CLI commands support `--dry-run` — always use it |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Start here** | quick-reference.md |
| **Understand the risks** | concepts/aws-destructive-operations.md |
| **Safe S3 work** | patterns/safe-s3-operations.md |
| **Safe EC2 work** | patterns/safe-ec2-operations.md |
| **IAM hardening** | patterns/iam-least-privilege.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| aws-deployer | patterns/safe-s3-operations.md | Deploy artifacts to S3 |
| lambda-builder | concepts/aws-destructive-operations.md | Understand what not to delete |
| infra-deployer | patterns/iam-least-privilege.md | Configure IAM for new services |
